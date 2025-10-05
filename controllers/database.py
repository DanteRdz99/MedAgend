import sqlite3

class Database:
    def get_db(self):
        # Crear una nueva conexión para cada solicitud
        conn = sqlite3.connect("medical_system.db")
        # Asegurarse de que las conexiones sean seguras para múltiples hilos
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        return conn

    def crear_tablas(self):
        # Crear las tablas al iniciar la aplicación
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)
        cursor.execute("INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)", ("admin", "12345"))
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id_paciente TEXT PRIMARY KEY,
                nombre TEXT,
                telefono TEXT,
                email TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicos (
                id_medico TEXT PRIMARY KEY,
                nombre TEXT,
                especialidad TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                id_cita TEXT PRIMARY KEY,
                id_paciente TEXT,
                id_medico TEXT,
                fecha TEXT,
                hora TEXT,
                estado TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id_historial TEXT PRIMARY KEY,
                id_paciente TEXT,
                fecha TEXT,
                descripcion TEXT
            )
        """)
        conn.commit()
        conn.close()