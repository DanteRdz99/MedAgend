from controllers.database import Database

class MedicoController:
    def __init__(self):
        self.db = Database()

    def registrar_medico(self, id_medico, nombre, especialidad):
        if not all([id_medico, nombre, especialidad]):
            return "Error: Todos los campos son obligatorios."

        if self.consultar_medico(id_medico):
            return "Error: El ID del médico ya existe."

        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medicos (id_medico, nombre, especialidad) VALUES (?, ?, ?)",
            (id_medico, nombre, especialidad)
        )
        conn.commit()
        conn.close()
        return "Médico registrado exitosamente."

    def consultar_medico(self, id_medico):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medicos WHERE id_medico = ?", (id_medico,))
        result = cursor.fetchone()
        conn.close()
        return result

    def listar_medicos(self):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medicos")
        result = cursor.fetchall()
        conn.close()
        return result