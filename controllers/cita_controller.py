from controllers.database import Database
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from dateutil import parser
import re

class CitaController:
    def __init__(self):
        self.db = Database()
        self.paciente_controller = PacienteController()
        self.medico_controller = MedicoController()

    def validar_fecha_hora(self, fecha, hora):
        try:
            parser.parse(fecha)
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha):
                return False
        except ValueError:
            return False

        if not re.match(r"^\d{2}:\d{2}$", hora):
            return False
        try:
            parser.parse(f"2023-01-01 {hora}")
        except ValueError:
            return False

        return True

    def agendar_cita(self, id_cita, id_paciente, id_medico, fecha, hora):
        if not all([id_cita, id_paciente, id_medico, fecha, hora]):
            return "Error: Todos los campos son obligatorios."

        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM citas WHERE id_cita = ?", (id_cita,))
        if cursor.fetchone():
            conn.close()
            return "Error: El ID de la cita ya existe."

        if not self.paciente_controller.consultar_paciente(id_paciente):
            conn.close()
            return "Error: El paciente no existe."

        if not self.medico_controller.consultar_medico(id_medico):
            conn.close()
            return "Error: El médico no existe."

        if not self.validar_fecha_hora(fecha, hora):
            conn.close()
            return "Error: Formato de fecha (YYYY-MM-DD) o hora (HH:MM) inválido."

        cursor.execute(
            "INSERT INTO citas (id_cita, id_paciente, id_medico, fecha, hora, estado) VALUES (?, ?, ?, ?, ?, ?)",
            (id_cita, id_paciente, id_medico, fecha, hora, "programada")
        )
        conn.commit()
        conn.close()
        return "Cita agendada exitosamente."

    def modificar_cita(self, id_cita, fecha, hora):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM citas WHERE id_cita = ?", (id_cita,))
        if not cursor.fetchone():
            conn.close()
            return "Error: La cita no existe."

        if not self.validar_fecha_hora(fecha, hora):
            conn.close()
            return "Error: Formato de fecha (YYYY-MM-DD) o hora (HH:MM) inválido."

        cursor.execute(
            "UPDATE citas SET fecha = ?, hora = ? WHERE id_cita = ?",
            (fecha, hora, id_cita)
        )
        conn.commit()
        conn.close()
        return "Cita modificada exitosamente."

    def cancelar_cita(self, id_cita):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM citas WHERE id_cita = ?", (id_cita,))
        if not cursor.fetchone():
            conn.close()
            return "Error: La cita no existe."

        cursor.execute(
            "UPDATE citas SET estado = ? WHERE id_cita = ?",
            ("cancelada", id_cita)
        )
        conn.commit()
        conn.close()
        return "Cita cancelada exitosamente."

    def listar_citas(self):
        conn = self.db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM citas")
        result = cursor.fetchall()
        conn.close()
        return result