from controllers.database import get_db_connection

def get_pacientes():
    """
    Obtiene una lista de todos los pacientes y sus datos de usuario.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.id, 
            p.nombre_completo, 
            p.email, 
            p.telefono, 
            u.username 
        FROM pacientes p
        JOIN usuarios u ON p.usuario_id = u.id
        ORDER BY p.nombre_completo
    """)
    
    pacientes = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in pacientes]