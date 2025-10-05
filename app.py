from flask import Flask, render_template, request, redirect, url_for, session, flash
from controllers.auth_controller import AuthController
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from controllers.cita_controller import CitaController
from controllers.historial_controller import HistorialController
from controllers.database import Database
from controllers.ai_controller import AiController # <-- CAMBIO 1: Nueva Importación

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necesario para usar sesiones y flash messages

# Inicializar controladores y crear tablas
db = Database()
db.crear_tablas()  # Crear las tablas al iniciar la aplicación

auth_controller = AuthController()
paciente_controller = PacienteController()
medico_controller = MedicoController()
cita_controller = CitaController()
historial_controller = HistorialController()
ai_controller = AiController() # <-- CAMBIO 2: Nueva Inicialización

# Middleware para proteger rutas
def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Por favor, inicia sesión para continuar.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
def home():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if auth_controller.login(username, password):
            session['logged_in'] = True
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('index'))
        else:
            flash("Usuario o contraseña incorrectos.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Has cerrado sesión.", "success")
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/pacientes', methods=['GET', 'POST'])
@login_required
def pacientes():
    if request.method == 'POST':
        id_paciente = request.form['id_paciente']
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        email = request.form['email']
        resultado = paciente_controller.registrar_paciente(id_paciente, nombre, telefono, email)
        flash(resultado, "success" if "exitosamente" in resultado else "error")
        return redirect(url_for('pacientes'))
    
    pacientes = paciente_controller.listar_pacientes()
    return render_template('pacientes.html', pacientes=pacientes)

@app.route('/medicos', methods=['GET', 'POST'])
@login_required
def medicos():
    if request.method == 'POST':
        id_medico = request.form['id_medico']
        nombre = request.form['nombre']
        especialidad = request.form['especialidad']
        resultado = medico_controller.registrar_medico(id_medico, nombre, especialidad)
        flash(resultado, "success" if "exitosamente" in resultado else "error")
        return redirect(url_for('medicos'))
    
    medicos = medico_controller.listar_medicos()
    return render_template('medicos.html', medicos=medicos)

@app.route('/citas', methods=['GET', 'POST'])
@login_required
def citas():
    if request.method == 'POST':
        if 'agendar' in request.form:
            id_cita = request.form['id_cita']
            id_paciente = request.form['id_paciente']
            id_medico = request.form['id_medico']
            fecha = request.form['fecha']
            hora = request.form['hora']
            resultado = cita_controller.agendar_cita(id_cita, id_paciente, id_medico, fecha, hora)
            flash(resultado, "success" if "exitosamente" in resultado else "error")
        elif 'modificar' in request.form:
            id_cita = request.form['id_cita']
            fecha = request.form['fecha']
            hora = request.form['hora']
            resultado = cita_controller.modificar_cita(id_cita, fecha, hora)
            flash(resultado, "success" if "exitosamente" in resultado else "error")
        elif 'cancelar' in request.form:
            id_cita = request.form['id_cita']
            resultado = cita_controller.cancelar_cita(id_cita)
            flash(resultado, "success" if "exitosamente" in resultado else "error")
        return redirect(url_for('citas'))
    
    citas = cita_controller.listar_citas()
    return render_template('citas.html', citas=citas)

@app.route('/historial', methods=['GET', 'POST'])
@login_required
def historial():
    if request.method == 'POST':
        if 'registrar' in request.form:
            id_historial = request.form['id_historial']
            id_paciente = request.form['id_paciente']
            fecha = request.form['fecha']
            descripcion = request.form['descripcion']
            resultado = historial_controller.registrar_historial(id_historial, id_paciente, fecha, descripcion)
            flash(resultado, "success" if "exitosamente" in resultado else "error")
        elif 'consultar' in request.form:
            id_paciente = request.form['id_paciente']
            historiales = historial_controller.consultar_historial(id_paciente)
            return render_template('historial.html', historiales=historiales)
        return redirect(url_for('historial'))
    
    return render_template('historial.html', historiales=None)

# <-- CAMBIO 3: Nueva ruta para el chat con el asistente IA
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    # Usaremos 'paciente_238' para simular que el usuario logueado es ese paciente.
    user_id_simulado = 'paciente_238'
    
    if request.method == 'POST':
        user_message = request.form['message']
        
        # Obtener respuesta de la IA
        ai_response = ai_controller.get_ai_response(user_id_simulado, user_message)
        
        # Guardar mensajes en flash para que se muestren en la plantilla
        # Usamos categorías 'user_message' y 'ai_response' para aplicar estilos en el HTML.
        flash(f"Tú: {user_message}", "user_message")
        flash(f"MedAgenda: {ai_response}", "ai_response")
        
        return redirect(url_for('chat'))
    
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)