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
        # g.user es cargado en app.py
        if not g.user or g.user['role'] != 'paciente':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@chat_bp.route('/')
@patient_required
def chat_view():
    """
    Muestra la página principal del chat.
    La ruta final será /chat/ gracias al prefijo en app.py
    """
    # Inicializar el historial en la sesión
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    # Pasamos el historial guardado en la sesión a la plantilla
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
    
    # --- ESTA ES LA CORRECCIÓN ---
    # Asegurarse de que el historial exista si el usuario lo limpió
    if 'chat_history' not in session:
        session['chat_history'] = []
    # --- FIN DE LA CORRECCIÓN ---
    
    # Añadir mensaje de usuario al historial de sesión
    session['chat_history'].append({"role": "user", "content": user_message})
    
    try:
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
        
    except Exception as e:
        # Manejo de errores (ej. API Key de Gemini inválida)
        print(f"Error en api_chat_message: {e}")
        error_message = "Lo siento, tuve un error de conexión con el asistente. (Verifica la API Key de Gemini)"
        
        # AÑADIDO: También guardar este error en el historial
        if 'chat_history' in session:
            session['chat_history'].append({"role": "ai", "content": error_message})
            session.modified = True
            
        return jsonify({"response": error_message}), 500


@chat_bp.route('/api/chat/clear', methods=['POST'])
@patient_required
def api_chat_clear():
    """Limpia el historial de chat de la sesión."""
    session.pop('chat_history', None)
    return jsonify({"success": True, "message": "Historial limpiado."})