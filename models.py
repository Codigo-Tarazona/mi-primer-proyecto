from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    intensidad = db.Column(db.String(50), nullable=False)
    horario = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    contacto_emergencia = db.Column(db.String(100), nullable=False)
    tel_emergencia = db.Column(db.String(20), nullable=False)
    pagos = db.relationship('Pago', backref='socio', lazy=True, cascade="all, delete-orphan")

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    mes_correspondiente = db.Column(db.String(20), nullable=False)
    metodo = db.Column(db.String(20), nullable=False) # Efectivo/Transferencia
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

class Trayectoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    logros = db.Column(db.Text)