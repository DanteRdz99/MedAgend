import sqlite3
from controllers.database import get_db_connection
from datetime import datetime, timedelta
import json

def agendar_nueva_cita(paciente_id, medico_id, fecha_hora_inicio_str, duracion_minutos=30, notas=""):
    """
    Agenda una nueva cita con validación de conflictos.
    Esta es la lógica "sin fallas".
    """
    
    # 1. Validar formato de fecha
    try:
        fecha_hora_inicio = datetime.fromisoformat(fecha_hora_inicio_str)
        fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=duracion_minutos)
    except ValueError:
        return {"error": "Formato de fecha y hora inválido. Use AAAA-MM-DDTHH:MM"}

    if fecha_hora_inicio < datetime.now():
        return {"error": "No se puede agendar una cita en el pasado."}

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 2. Validar horario de trabajo del médico
    cursor.execute("SELECT horario_trabajo FROM medicos WHERE id = ?", (medico_id,))
    medico = cursor.fetchone()
    if not medico:
        conn.close()
        return {"error": "El médico no existe."}

    try:
        horario = json.loads(medico['horario_trabajo'])
        dia_semana = fecha_hora_inicio.strftime('%A').lower() # ej. 'lunes'
        
        if dia_semana not in horario:
            conn.close()
            return {"error": f"El médico no trabaja los {dia_semana}."}

        # Comprobar si la cita cae dentro de algún turno de trabajo
        esta_en_turno = False
        for turno in horario[dia_semana]:
            inicio_turno_str, fin_turno_str = turno.split('-')
            inicio_turno = fecha_hora_inicio.replace(hour=int(inicio_turno_str.split(':')[0]), minute=int(inicio_turno_str.split(':')[1]))
            fin_turno = fecha_hora_inicio.replace(hour=int(fin_turno_str.split(':')[0]), minute=int(fin_turno_str.split(':')[1]))
            
            if fecha_hora_inicio >= inicio_turno and fecha_hora_fin <= fin_turno:
                esta_en_turno = True
                break
        
        if not esta_en_turno:
            conn.close()
            return {"error": "La cita está fuera del horario de trabajo del médico."}
            
    except Exception as e:
        conn.close()
        return {"error": f"Error al validar horario del médico: {e}"}

    # 3. Validar conflictos con OTRAS citas (Overlap check)
    cursor.execute("""
        SELECT * FROM citas
        WHERE medico_id = ? 
        AND estado = 'programada'
        AND (
            (fecha_hora_inicio < ? AND datetime(fecha_hora_inicio, '+' || duracion_minutos || ' minutes') > ?) OR
            (fecha_hora_inicio >= ? AND fecha_hora_inicio < ?)
        )
    """, (medico_id, fecha_hora_fin, fecha_hora_inicio, fecha_hora_inicio, fecha_hora_fin))
    
    conflicto = cursor.fetchone()
    if conflicto:
        conn.close()
        return {"error": f"El médico ya tiene una cita en ese horario (ID Cita: {conflicto['id']})."}

    # 4. ¡Todo bien! Insertar la cita
    try:
        cursor.execute("""
            INSERT INTO citas (paciente_id, medico_id, fecha_hora_inicio, duracion_minutos, notas_paciente)
            VALUES (?, ?, ?, ?, ?)
        """, (paciente_id, medico_id, fecha_hora_inicio, duracion_minutos, notas))
        
        nueva_cita_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return {
            "success": True, 
            "id_cita": nueva_cita_id, 
            "mensaje": "Cita agendada exitosamente."
        }
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        return {"error": f"Error de integridad: {e}"}
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"error": f"Error inesperado al guardar: {e}"}

def get_citas_paciente(paciente_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, m.nombre_completo as medico_nombre, m.especialidad as medico_especialidad
        FROM citas c
        JOIN medicos m ON c.medico_id = m.id
        WHERE c.paciente_id = ?
        ORDER BY c.fecha_hora_inicio DESC
    """, (paciente_id,))
    citas = cursor.fetchall()
    conn.close()
    return [dict(row) for row in citas]