from flask import Flask, session, redirect, url_for, g
from controllers.database import init_db
from services import auth_service  # Importar el servicio
import os
from dotenv import load_dotenv

# Cargar variables de entorno (GEMINI_API_KEY)
load_dotenv()

# Importar Blueprints (las nuevas rutas)
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.views_routes import views_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24) # Clave secreta segura

    # Inicializar la base de datos
    with app.app_context():
        init_db()

    # Registrar los Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth') # http://.../auth/login
    app.register_blueprint(chat_bp, url_prefix='/chat') # http://.../chat
    app.register_blueprint(views_bp, url_prefix='/views') # http://.../views/admin/dashboard

    @app.before_request
    def load_logged_in_user():
        """
        Carga los datos del usuario en g.user en cada solicitud
        si está en la sesión.
        """
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            # Usar la nueva función del servicio para obtener todos los datos
            g.user = auth_service.get_user_data_for_session(user_id)

    @app.route('/')
    def index():
        # Redirigir según el rol
        if g.user:
            if g.user['role'] == 'admin':
                return redirect(url_for('views.admin_dashboard'))
            else:
                # --- ¡CAMBIO IMPORTANTE! ---
                # Los pacientes ya no van al chat, van a su nuevo portal
                return redirect(url_for('views.portal_paciente')) 
        
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0') # debug=True para desarrollo