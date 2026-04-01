from app import app
from models import db, Admin

def create_admin():
    with app.app_context():
        # Verificamos si ya existe
        if not Admin.query.filter_by(usuario="entrenador_wolf").first():
            admin_principal = Admin(usuario="entrenador_wolf")
            # Configura aquí tu contraseña segura
            admin_principal.set_password("Wolf2026!Admin") 
            
            db.session.add(admin_principal)
            db.session.commit()
            print("✅ Administrador 'entrenador_wolf' creado con éxito.")
        else:
            print("⚠️ El administrador ya existe.")

if __name__ == "__main__":
    create_admin()