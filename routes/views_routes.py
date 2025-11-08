from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from services import paciente_service, medico_service
from functools import wraps
import json

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
            
            # Ejemplo simple de horario por defecto si está vacío
            if not horario_json:
                horario_json = json.dumps({
                    "lunes": ["09:00-13:00", "14:00-17:00"],
                    "martes": ["09:00-13:00", "14:00-17:00"],
                    "miercoles": ["09:00-13:00", "14:00-17:00"],
                    "jueves": ["09:00-13:00", "14:00-17:00"],
                    "viernes": ["09:00-13:00", "14:00-17:00"]
                })
            
            resultado = medico_service.crear_medico(nombre, especialidad, horario_json)
            
            if resultado.get('success'):
                flash("Médico registrado exitosamente.", "success")
            else:
                flash(resultado.get('error'), "error")
            
            return redirect(url_for('views.admin_dashboard'))

    # Para el método GET
    pacientes = paciente_service.get_pacientes()
    medicos = medico_service.get_medicos()
    
    return render_template('admin_dashboard.html', pacientes=pacientes, medicos=medicos)