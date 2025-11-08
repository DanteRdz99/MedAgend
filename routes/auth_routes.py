from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from services import auth_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está logueado, redirigir
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = auth_service.validar_usuario(username, password)
        
        if user:
            # Iniciar sesión exitosamente
            session.clear()
            session['user_id'] = user['id']
            flash(f"¡Bienvenido de nuevo, {username}!", "success")
            return redirect(url_for('index')) # Redirige al app.py @app.route('/')
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Si el usuario ya está logueado, redirigir
    if g.user:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nombre_completo = request.form['nombre_completo']
        email = request.form['email']
        telefono = request.form['telefono']
        
        resultado = auth_service.crear_paciente(
            username, password, nombre_completo, email, telefono
        )
        
        if resultado.get('success'):
            flash("¡Cuenta creada exitosamente! Por favor, inicia sesión.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash(resultado.get('error', 'Ocurrió un error desconocido.'), "error")
            
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for('auth.login'))