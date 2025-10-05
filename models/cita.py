class Cita:
    def __init__(self, id_cita, id_paciente, id_medico, fecha, hora, estado="programada"):
        self.id_cita = id_cita
        self.id_paciente = id_paciente
        self.id_medico = id_medico
        self.fecha = fecha
        self.hora = hora
        self.estado = estado