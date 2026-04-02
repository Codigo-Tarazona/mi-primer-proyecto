from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Usuario, Pago, Trayectoria
from utils import generar_pdf_comprobante
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wolfteam.db'
app.config['SECRET_KEY'] = 'wolf_secret_2026'
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
        nuevo = Usuario(
            nombre_completo=request.form['nombre'], edad=request.form['edad'],
            categoria=request.form['categoria'], intensidad=request.form['intensidad'],
            horario=request.form['horario'], telefono=request.form['telefono'],
            contacto_emergencia=request.form['emergencia_nombre'], tel_emergencia=request.form['emergencia_tel']
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('trayectoria'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario')
        pw = request.form.get('password')
        print(f"DEBUG: Intentando entrar con usuario: {user}") # Esto saldrá en tu terminal

        admin = Admin.query.filter_by(usuario=user).first()

        if admin:
            print("DEBUG: Usuario encontrado en BD")
            if admin.check_password(pw):
                print("DEBUG: Contraseña CORRECTA")
                login_user(admin)
                return redirect(url_for('dashboard'))
            else:
                print("DEBUG: Contraseña INCORRECTA")
        else:
            print("DEBUG: Usuario NO encontrado")
            
        flash("Credenciales inválidas", "danger")
    return render_template('login.html')

# --- RUTAS PRIVADAS ---
from datetime import datetime

@app.route('/dashboard')
@login_required
def dashboard():
    usuarios = Usuario.query.all()
    estados = {}
    
    # Obtenemos el mes actual en español para comparar
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_actual = meses[datetime.now().month - 1]

    for u in usuarios:
        # Buscamos si el usuario tiene AL MENOS un pago registrado para el mes actual
        pago_existente = Pago.query.filter_by(
            usuario_id=u.id, 
            mes_correspondiente=mes_actual
        ).first()
        
        if pago_existente:
            estados[u.id] = 'Al Día'
        else:
            estados[u.id] = 'Mora'
            
    return render_template('dashboard.html', usuarios=usuarios, estados=estados)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/eliminar_usuario/<int:usuario_id>')
@login_required
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado', 'success')
    return redirect(url_for('dashboard'))

@app.route('/registrar_pago/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
def registrar_pago(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    
    if request.method == 'POST':
        # Capturamos los datos del formulario
        monto_f = request.form.get('monto')
        mes_f = request.form.get('mes')
        metodo_f = request.form.get('metodo')

        # Creamos el pago con los datos capturados
        pago = Pago(
            monto=monto_f,
            mes_correspondiente=mes_f,
            metodo=metodo_f,
            usuario_id=usuario.id,
            fecha_pago=datetime.now()
        )
        
        db.session.add(pago)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('pagos.html', usuario=usuario)

@app.route('/ver_usuario/<int:usuario_id>')
@login_required
def ver_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('dashboard'))
    pagos = Pago.query.filter_by(usuario_id=usuario.id).order_by(Pago.fecha_pago.desc()).all()
    
    return render_template('perfil_usuario.html', usuario=usuario, pagos=pagos)

@app.route('/editar_pago/<int:pago_id>', methods=['GET', 'POST'])
@login_required
def editar_pago(pago_id):
    pago = db.session.get(Pago, pago_id)
    if not pago:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        pago.monto = request.form.get('monto')
        pago.mes_correspondiente = request.form.get('mes')
        pago.metodo = request.form.get('metodo')
        db.session.commit()
        return redirect(url_for('ver_usuario', usuario_id=pago.usuario_id))
    
    # ASEGÚRATE DE QUE ESTO COINCIDA CON EL NOMBRE DEL ARCHIVO:
    return render_template('editar_pago.html', pago=pago)

@app.route('/eliminar_pago/<int:pago_id>')
@login_required
def eliminar_pago(pago_id):
    pago = db.session.get(Pago, pago_id)
    if pago:
        usuario_id = pago.usuario_id
        db.session.delete(pago)
        db.session.commit()
        flash("Pago eliminado. El estado del usuario se ha actualizado.", "info")
        return redirect(url_for('ver_usuario', usuario_id=usuario_id))
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run()