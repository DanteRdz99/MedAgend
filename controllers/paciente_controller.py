from controllers.database import Database

class PacienteController:
    def __init__(self):
        self.db = Database()

    def registrar_paciente(self, id_paciente, nombre, telefono, email):
        if not all([id_paciente, nombre, telefono, email]):
            return "Error: Todos los campos son obligatorios."

        if self.consultar_paciente(id_paciente):
            return "Error: El ID del paciente ya existe."

        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pacientes (id_paciente, nombre, telefono, email) VALUES (?, ?, ?, ?)",
            (id_paciente, nombre, telefono, email)
        )
        conn.commit()
        conn.close()
        return "Paciente registrado exitosamente."

    def consultar_paciente(self, id_paciente):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE id_paciente = ?", (id_paciente,))
        result = cursor.fetchone()
        conn.close()
        return result

    def listar_pacientes(self):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pacientes")
        result = cursor.fetchall()
        conn.close()
        return result