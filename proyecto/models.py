from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    conversions = db.relationship('Conversion', backref='author', lazy='dynamic')

class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255))
    doc_title = db.Column(db.String(255))
    doc_author = db.Column(db.String(255))
    detected_language = db.Column(db.String(10))
    voice_used = db.Column(db.String(50))
    speed_used = db.Column(db.Float)
    mp3_path = db.Column(db.String(512))
    duration_seconds = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    file_size_mb = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending') # pending, processing, completed, error
    progress_message = db.Column(db.String(100), default='')
    error_message = db.Column(db.Text)
