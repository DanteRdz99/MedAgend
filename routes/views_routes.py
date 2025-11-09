from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from services import paciente_service, medico_service, cita_service # <-- AÑADIDO cita_service
from functools import wraps
import json

# --- ¡NUEVO! Importamos el decorador de paciente ---
from routes.chat_routes import patient_required 

views_bp = Blueprint('views', __name__)

# --- Decorador de Admin ---
def admin_required(f):
    """
    Un decorador para asegurar que solo los admins
    puedan acceder a esta ruta.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or g.user['role'] != 'admin':
            flash("No tienes permiso para acceder a esta página.", "error")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@views_bp.route('/admin/dashboard', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    
    if request.method == 'POST':
        if 'registrar_medico' in request.form:
            nombre = request.form['nombre_completo']
            especialidad = request.form['especialidad']
            horario_json = request.form['horario_trabajo']
            ubicacion = request.form['ubicacion'] # <-- ¡NUEVO CAMPO!
            
            # Ejemplo simple de horario por defecto si está vacío
            if not horario_json:
                horario_json = json.dumps({
                    "lunes": ["09:00-13:00", "14:00-17:00"],
                    "martes": ["09:00-13:00", "14:00-17:00"],
                    "miercoles": ["09:00-13:00", "14:00-17:00"],
                    "jueves": ["09:00-13:00", "14:00-17:00"],
                    "viernes": ["09:00-13:00", "14:00-17:00"]
                })
            
            # --- ¡FUNCIÓN ACTUALIZADA! ---
            resultado = medico_service.crear_medico(nombre, especialidad, horario_json, ubicacion)
            
            if resultado.get('success'):
                flash("Médico registrado exitosamente.", "success")
            else:
                flash(resultado.get('error'), "error")
            
            return redirect(url_for('views.admin_dashboard'))

    # Para el método GET
    pacientes = paciente_service.get_pacientes()
    medicos = medico_service.get_medicos()
    
    return render_template('admin_dashboard.html', pacientes=pacientes, medicos=medicos)

# --- ¡TODA ESTA ES LA NUEVA SECCIÓN PARA EL PORTAL DE PACIENTE! ---

@views_bp.route('/portal')
@patient_required
def portal_paciente():
    """
    Muestra el nuevo Portal de Paciente.
    """
    # Obtenemos los datos para mostrar en el portal
    
    # 1. Médicos (para la tarjeta de "Consultar Médicos")
    medicos = medico_service.get_medicos()
    
    # 2. Citas (para la tarjeta de "Mis Próximas Citas")
    # g.user es el paciente logueado (incluye 'paciente_id')
    citas_paciente = cita_service.get_citas_paciente(g.user['paciente_id'])
    
    # (Opcional) Convertir los horarios JSON de los médicos en algo legible
    # Esto es avanzado, pero lo haremos en la plantilla con un truco.
    
    return render_template(
        'portal_paciente.html', 
        medicos=medicos, 
        citas=citas_paciente
    )