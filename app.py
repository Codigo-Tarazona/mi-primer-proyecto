from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Usuario, Pago, Trayectoria
from utils import generar_pdf_comprobante
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wolfteam.db'
app.config['SECRET_KEY'] = 'wolf_secret_2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recomendado para evitar warnings

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))

# --- RUTAS PÚBLICAS ---
@app.route('/')
def trayectoria():
    info = Trayectoria.query.first()
    return render_template('index.html', info=info)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Validar que los nombres coincidan con models.py (posicion vs categoria)
        nuevo = Usuario(
            nombre_completo=request.form['nombre'], 
            edad=request.form['edad'],
            posicion=request.form['categoria'], # Ajustado a lo que vimos en el Dashboard
            horario=request.form['horario'], 
            telefono_acudiente=request.form['telefono'], # Ajustado para que se vea en la Ficha
            documento=request.form.get('documento', '') # Agregado si lo pides en el form
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("¡Registro exitoso!", "success")
        return redirect(url_for('trayectoria'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario')
        pw = request.form.get('password')
        admin = Admin.query.filter_by(usuario=user).first()

        if admin and admin.check_password(pw):
            login_user(admin)
            return redirect(url_for('dashboard'))
            
        flash("Credenciales inválidas", "danger")
    return render_template('login.html')

# --- RUTAS PRIVADAS ---

@app.route('/dashboard')
@login_required
def dashboard():
    usuarios = Usuario.query.all()
    estados = {}
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_actual = meses[datetime.now().month - 1]

    for u in usuarios:
        pago_existente = Pago.query.filter_by(
            usuario_id=u.id, 
            mes_correspondiente=mes_actual
        ).first()
        estados[u.id] = 'Al Día' if pago_existente else 'Mora'
            
    return render_template('dashboard.html', usuarios=usuarios, estados=estados)

@app.route('/ver_usuario/<int:usuario_id>')
@login_required
def ver_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('dashboard'))
    pagos = Pago.query.filter_by(usuario_id=usuario.id).order_by(Pago.fecha_pago.desc()).all()
    return render_template('perfil_usuario.html', usuario=usuario, pagos=pagos)

@app.route('/registrar_pago/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def registrar_pago(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if request.method == 'POST':
        pago = Pago(
            monto=request.form.get('monto'),
            mes_correspondiente=request.form.get('mes'),
            metodo=request.form.get('metodo'),
            usuario_id=usuario.id,
            fecha_pago=datetime.now()
        )
        db.session.add(pago)
        db.session.commit()
        flash("Pago registrado correctamente", "success")
        return redirect(url_for('ver_usuario', usuario_id=usuario.id))
    return render_template('pagos.html', usuario=usuario)

# Ruta para comprobantes PDF (si la usas)
@app.route('/descargar_comprobante/<int:pago_id>')
@login_required
def descargar_comprobante(pago_id):
    pago = db.session.get(Pago, pago_id)
    pdf_path = generar_pdf_comprobante(pago)
    return send_file(pdf_path, as_attachment=True)

# ... (Tus rutas de editar y eliminar pago están correctas)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Esto asegura que las tablas se creen en Render
    app.run(debug=True) # Activa debug para ver errores en desarrollo