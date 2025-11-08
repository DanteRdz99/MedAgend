from flask import Flask, session, redirect, url_for, g
from controllers.database import init_db, get_db_connection
from services.auth_service import get_user_by_id
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
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(views_bp)

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
            # Cargar usuario desde la BD
            g.user = get_user_by_id(user_id)

    @app.route('/')
    def index():
        # Redirigir según el rol
        if 'user_id' in session and g.user:
            if g.user['role'] == 'admin':
                return redirect(url_for('views.admin_dashboard'))
            else:
                return redirect(url_for('chat.chat_view')) # Pacientes van al chat
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0') # debug=True para desarrollo