import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "medical_system_v2.db"

def get_db_connection():
    """
    Crea una conexión a la base de datos optimizada para concurrencia.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")  # Modo WAL para concurrencia
    conn.execute("PRAGMA foreign_keys = ON;") # Forzar integridad referencial
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Crea todas las tablas desde cero si no existen.
    Esta es la "Base de Datos Chingona".
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # --- Usuarios: El sistema central de login ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'paciente' CHECK(role IN ('admin', 'paciente'))
    )
    """)
    
    # --- Pacientes: Vinculado a un usuario ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        nombre_completo TEXT NOT NULL,
        telefono TEXT,
        email TEXT UNIQUE NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
    )
    """)
    
    # --- Médicos: Con horarios de trabajo ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        especialidad TEXT NOT NULL,
        horario_trabajo TEXT  -- Almacenado como JSON, ej: {"lunes": ["09:00-13:00", "14:00-17:00"]}
    )
    """)
    
    # --- Citas: El núcleo del sistema, ahora robusto ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        medico_id INTEGER NOT NULL,
        fecha_hora_inicio DATETIME NOT NULL,
        duracion_minutos INTEGER NOT NULL DEFAULT 30,
        estado TEXT NOT NULL DEFAULT 'programada' CHECK(estado IN ('programada', 'cancelada', 'completada')),
        notas_paciente TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
        FOREIGN KEY (medico_id) REFERENCES medicos (id),
        UNIQUE(medico_id, fecha_hora_inicio) -- Un médico no puede tener 2 citas a la misma hora
    )
    """)
    
    # --- Historial: Vinculado a una cita ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cita_id INTEGER UNIQUE NOT NULL,
        descripcion TEXT NOT NULL,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cita_id) REFERENCES citas (id)
    )
    """)
    
    # --- Crear usuario Admin por defecto ---
    try:
        admin_pass_hash = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            ('admin', admin_pass_hash, 'admin')
        )
    except sqlite3.IntegrityError:
        pass  # El admin ya existe

    # --- (Opcional) Crear un médico de prueba ---
    try:
        horario_dr = '{"lunes": ["09:00-12:00"], "miercoles": ["09:00-12:00"], "viernes": ["09:00-12:00"]}'
        cursor.execute(
            "INSERT INTO medicos (nombre_completo, especialidad, horario_trabajo) VALUES (?, ?, ?)",
            ('Dr. Alan Turing', 'Cardiología', horario_dr)
        )
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()
    print("Base de datos inicializada exitosamente.")