import sqlite3
from controllers.database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

def validar_usuario(username, password):
    """
    Valida las credenciales de un usuario.
    Devuelve el diccionario del usuario si es válido, sino None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    
    return None

def get_user_data_for_session(user_id):
    """
    Obtiene los datos combinados de 'usuarios' y 'pacientes'
    para ser usados en la sesión (g.user).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Unimos usuarios y pacientes. Para un admin, los campos de paciente serán None.
    cursor.execute("""
        SELECT 
            u.id, 
            u.username, 
            u.role, 
            p.id as paciente_id, 
            p.nombre_completo, 
            p.email,
            p.telefono
        FROM usuarios u
        LEFT JOIN pacientes p ON u.id = p.usuario_id
        WHERE u.id = ?
    """, (user_id,))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return dict(user_data)
    
    return None

def crear_paciente(username, password, nombre_completo, email, telefono):
    """
    Crea un nuevo usuario y un nuevo paciente dentro de una transacción.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Hashear la contraseña
        password_hash = generate_password_hash(password)
        
        # 1. Crear el usuario
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, 'paciente')",
            (username, password_hash)
        )
        new_user_id = cursor.lastrowid
        
        # 2. Crear el paciente vinculado
        cursor.execute(
            """
            INSERT INTO pacientes (usuario_id, nombre_completo, email, telefono)
            VALUES (?, ?, ?, ?)
            """,
            (new_user_id, nombre_completo, email, telefono)
        )
        
        conn.commit()
        return {"success": True, "user_id": new_user_id}
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if 'UNIQUE constraint failed: usuarios.username' in str(e):
            return {"error": "El nombre de usuario ya existe."}
        if 'UNIQUE constraint failed: pacientes.email' in str(e):
            return {"error": "El email ya está registrado."}
        return {"error": f"Error de integridad: {e}"}
        
    except Exception as e:
        conn.rollback()
        return {"error": f"Ocurrió un error inesperado: {e}"}
        
    finally:
        conn.close()