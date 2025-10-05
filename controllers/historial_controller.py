from controllers.database import Database
from controllers.paciente_controller import PacienteController
from dateutil import parser
import re

class HistorialController:
    def __init__(self):
        self.db = Database()
        self.paciente_controller = PacienteController()

    def validar_fecha(self, fecha):
        try:
            parser.parse(fecha)
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
                return False
        except ValueError:
            return False
        return True

    def registrar_historial(self, id_historial, id_paciente, fecha, descripcion):
        if not all([id_historial, id_paciente, fecha, descripcion]):
            return "Error: Todos los campos son obligatorios."

        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historial WHERE id_historial = ?", (id_historial,))
        if cursor.fetchone():
            conn.close()
            return "Error: El ID del historial ya existe."

        if not self.paciente_controller.consultar_paciente(id_paciente):
            conn.close()
            return "Error: El paciente no existe."

        if not self.validar_fecha(fecha):
            conn.close()
            return "Error: Formato de fecha (YYYY-MM-DD) inválido."

        cursor.execute(
            "INSERT INTO historial (id_historial, id_paciente, fecha, descripcion) VALUES (?, ?, ?, ?)",
            (id_historial, id_paciente, fecha, descripcion)
        )
        conn.commit()
        conn.close()
        return "Historial registrado exitosamente."

    def consultar_historial(self, id_paciente):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historial WHERE id_paciente = ?", (id_paciente,))
        result = cursor.fetchall()
        conn.close()
        return result