from controllers.database import get_db_connection
import json
import sqlite3

def get_medicos(especialidad_filter=None):
    """
    Obtiene una lista de todos los médicos.
    Si se provee 'especialidad_filter', filtra por esa especialidad.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = "SELECT * FROM medicos"
        params = []
        
        if especialidad_filter:
            # Usamos LOWER() para que no importe si el usuario escribe
            # "cardiologo" o "Cardiología".
            query += " WHERE LOWER(especialidad) LIKE LOWER(?)"
            params.append(f"%{especialidad_filter}%")
            
        cursor.execute(query, params)
        medicos = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in medicos]
        
    except Exception as e:
        conn.close()
        print(f"ERROR EN get_medicos: {e}")
        # Devolvemos una lista vacía en lugar de crashear
        return []

def crear_medico(nombre_completo, especialidad, horario_json, ubicacion): # <-- AÑADIDO 'ubicacion'
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
            # --- ¡CONSULTA ACTUALIZADA! ---
            "INSERT INTO medicos (nombre_completo, especialidad, horario_trabajo, ubicacion) VALUES (?, ?, ?, ?)",
            (nombre_completo, especialidad, horario_json, ubicacion)
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