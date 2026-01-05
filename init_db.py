from app import app, db

def init_db():
    with app.app_context():
        print("Creando tablas de base de datos...")
        db.create_all()
        print("Tablas creadas exitosamente.")

if __name__ == "__main__":
    init_db()
