from app import app
from models import db, Admin

def reset_admin():
    with app.app_context():
        db.create_all() # Recrea las tablas limpias
        
        # Eliminamos cualquier rastro previo
        Admin.query.delete()
        
        # Creamos el nuevo usuario
        nuevo_admin = Admin(usuario="admin")
        nuevo_admin.set_password("12345") # Usa una simple para probar
        
        db.session.add(nuevo_admin)
        db.session.commit()
        print("✅ BASE DE DATOS RESETEADA")
        print("👤 Usuario: admin")
        print("🔑 Contraseña: 12345")

if __name__ == "__main__":
    reset_admin()