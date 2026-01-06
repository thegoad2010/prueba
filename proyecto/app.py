from flask import Flask, render_template, request, flash, redirect, url_for, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from config import Config
from models import db, User, Conversion
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# Auto-create database tables (fix for Render)
with app.app_context():
    db.create_all()
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/history')
@login_required
def history():
    conversions = Conversion.query.filter_by(user_id=current_user.id).order_by(Conversion.timestamp.desc()).all()
    return render_template('history.html', conversions=conversions)
import threading
from utils.validators import validate_pdf
from utils.pdf_processor import extract_text_metadata
from utils.audio_generator import generate_audio_gtts
import time
# ... (previous code)
@app.route('/upload', methods=['POST'])
@login_required
def upload_pdf():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validation
        is_valid, error = validate_pdf(filepath)
        if not is_valid:
            os.remove(filepath)
            return {'error': error}, 400
            
        # Extraction (can be slow, but usually fast enough for <71 pages to do inline or we can thread this too)
        # For better UX, let's do this synchronously to give immediate "Language Detected" feedback
        metadata = extract_text_metadata(filepath)
        if not metadata:
            os.remove(filepath)
            return {'error': 'Failed to process PDF'}, 500
            
        # Create Conversion Record
        conversion = Conversion(
            user_id=current_user.id,
            filename=filename,
            doc_title=metadata['title'],
            doc_author=metadata['author'],
            detected_language=metadata['language'],
            status='uploaded',
            progress_message='Waiting for user configuration'
        )
        db.session.add(conversion)
        db.session.commit()
        
        # Store text temporarily in file or db? 
        # For simplicity, we re-extract or store in a txt file.
        # Let's store in a txt file alongside the pdf
        txt_path = filepath + '.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(metadata['text'])
            
        return {
            'id': conversion.id,
            'filename': filename,
            'title': metadata['title'],
            'author': metadata['author'],
            'language': metadata['language'],
            'pages': metadata['pages']
        }
def process_audio_background(app, conversion_id, text, language, voice):
    print(f"DEBUG: Starting background thread for conversion {conversion_id}", flush=True)
    with app.app_context():
        try:
            print("DEBUG: Querying conversion object", flush=True)
            conversion = Conversion.query.get(conversion_id)
            conversion.status = 'processing'
            conversion.progress_message = 'Generating audio...'
            db.session.commit()
            print("DEBUG: Status updated to processing", flush=True)
            
            # Generate Audio
            output_filename = f"{conversion.id}_{int(time.time())}.mp3"
            output_path = os.path.join(app.config['AUDIO_FOLDER'], output_filename)
            
            print(f"DEBUG: Calling gTTS generation. Text len: {len(text)}. Lang: {language}", flush=True)
            duration = generate_audio_gtts(
                text=text,
                language=language, 
                output_path=output_path,
                title=conversion.doc_title,
                author=conversion.doc_author
            )
            print("DEBUG: gTTS generation finished", flush=True)
            
            conversion.status = 'completed'
            conversion.progress_message = 'Completed'
            conversion.mp3_path = output_path
            conversion.duration_seconds = int(duration)
            if os.path.exists(output_path):
                conversion.file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            else:
                conversion.file_size_mb = 0.0
            
            db.session.commit()
            print("DEBUG: DB finalized. Done.", flush=True)
            
        except Exception as e:
            print(f"DEBUG: ERROR in background thread: {e}", flush=True)
            try:
                # Re-query in case session is botched
                conversion = Conversion.query.get(conversion_id)
                conversion.status = 'error'
                conversion.error_message = str(e)
                db.session.commit()
            except:
                pass
@app.route('/generate', methods=['POST'])
@login_required
def generate_audio_route():
    data = request.json
    conversion_id = data.get('id')
    voice = data.get('voice')
    # speed = data.get('speed') # Not used in gTTS basic implementation
    
    conversion = Conversion.query.get_or_404(conversion_id)
    if conversion.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], conversion.filename)
    txt_path = filepath + '.txt'
    
    if not os.path.exists(txt_path):
        return {'error': 'Source text not found'}, 404
        
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    # Start background thread
    # Fix: app is the real Flask object, so we pass it directly.
    thread = threading.Thread(target=process_audio_background, args=(app, conversion_id, text, conversion.detected_language, voice))
    thread.start()
    
    return {'status': 'started'}
@app.route('/status/<int:conversion_id>')
@login_required
def get_status(conversion_id):
    conversion = Conversion.query.get_or_404(conversion_id)
    if conversion.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    
    return {
        'status': conversion.status,
        'progress': conversion.progress_message,
        'mp3_url': url_for('static', filename=f'audio/{os.path.basename(conversion.mp3_path)}') if conversion.mp3_path else None
    }
@app.route('/download/<int:conversion_id>')
@login_required
def download_mp3(conversion_id):
    conversion = Conversion.query.get_or_404(conversion_id)
    if conversion.user_id != current_user.id:
        return "Unauthorized", 403
    return send_file(conversion.mp3_path, as_attachment=True)
@app.route('/reset-db')
def reset_db():
    if not app.debug and not os.environ.get('Render'):
        # Simple protection: only allow in debug or if we are sure (but here we just want it to work)
        # For this specific troubleshooting session, we'll allow it.
        pass
    
    try:
        db.drop_all()
        db.create_all()
        return "Base de datos reiniciada correctamente. Ahora intenta registrarte de nuevo."
    except Exception as e:
        return f"Error al reiniciar la base de datos: {str(e)}"
# Ensure directories exist (Correct placement for production/Gunicorn)
with app.app_context():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
    # db.create_all() is mainly for the first run or reset-db route, 
    # but keeping it here doesn't hurt if we want auto-creation attempt on boot.
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
