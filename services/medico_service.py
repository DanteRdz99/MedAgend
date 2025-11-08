from controllers.database import get_db_connection
import json

def get_medicos(especialidad_filter=None):
    """
    Obtiene una lista de todos los médicos.
    Si se provee 'especialidad_filter', filtra por esa especialidad.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM medicos"
    params = []
    
    if especialidad_filter:
        query += " WHERE especialidad = ?"
        params.append(especialidad_filter)
        
    cursor.execute(query, params)
    medicos = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in medicos]

def crear_medico(nombre_completo, especialidad, horario_json):
    """
    Registra un nuevo médico en la base de datos.
    'horario_json' debe ser un string JSON válido.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Validar que el horario sea JSON
    try:
        json.loads(horario_json)
    except json.JSONDecodeError:
        return {"error": "El formato del horario JSON es inválido."}
    
    try:
        cursor.execute(
            "INSERT INTO medicos (nombre_completo, especialidad, horario_trabajo) VALUES (?, ?, ?)",
            (nombre_completo, especialidad, horario_json)
        )
        conn.commit()
        return {"success": True, "id_medico": cursor.lastrowid}
        
    except sqlite3.IntegrityError:
        conn.rollback()
        return {"error": "Error de integridad, ¿quizás el médico ya existe?"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Ocurrió un error: {e}"}
    finally:
        conn.close()