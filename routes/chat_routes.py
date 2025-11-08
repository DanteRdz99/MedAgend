from flask import Blueprint, request, jsonify, render_template, session, g, redirect, url_for
from controllers.ai_controller import AiController
from functools import wraps

chat_bp = Blueprint('chat', __name__)

def patient_required(f):
    """
    Un decorador para asegurar que solo los pacientes
    puedan acceder a esta ruta.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or g.user['role'] != 'paciente':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@chat_bp.route('/chat')
@patient_required
def chat_view():
    """Muestra la página principal del chat."""
    # Inicializar el historial en la sesión
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('chat.html', chat_history=session['chat_history'])

@chat_bp.route('/api/chat', methods=['POST'])
@patient_required
def api_chat_message():
    """
    API endpoint para manejar un mensaje de chat.
    Devuelve JSON.
    """
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400
    
    # Añadir mensaje de usuario al historial de sesión
    session['chat_history'].append({"role": "user", "content": user_message})
    
    # Crear el controlador de IA (ahora necesita al usuario)
    # g.user es el usuario cargado en app.py, que incluye 'paciente_id', etc.
    ai_controller = AiController(user=g.user) 
    
    # Obtener respuesta de la IA (manejando el historial internamente)
    ai_response = ai_controller.handle_message(user_message)
    
    # Añadir respuesta de IA al historial de sesión
    session['chat_history'].append({"role": "ai", "content": ai_response})
    session.modified = True # Marcar la sesión como modificada
    
    # Devolver solo la respuesta de la IA
    return jsonify({"response": ai_response})

@chat_bp.route('/api/chat/clear', methods=['POST'])
@patient_required
def api_chat_clear():
    """Limpia el historial de chat de la sesión."""
    session.pop('chat_history', None)
    return jsonify({"success": True, "message": "Historial limpiado."})