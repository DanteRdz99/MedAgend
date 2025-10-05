import os
from google import genai
from controllers.cita_controller import CitaController
from controllers.historial_controller import HistorialController

class AiController:
    def __init__(self):
        # 1. Inicializar el cliente de Gemini
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # En un entorno real, esto debería ser un error, pero lo dejamos aquí para recordatorio
            print("ADVERTENCIA: La variable de entorno GEMINI_API_KEY no está configurada. El chat NO funcionará.")
            self.ai_client = None
        else:
            try:
                self.ai_client = genai.Client(api_key=api_key)
                self.model = 'gemini-2.5-flash'  # Modelo rápido y eficiente para chat
            except Exception as e:
                print(f"Error al inicializar el cliente de Gemini: {e}")
                self.ai_client = None


        # 2. Inicializar controladores de negocio
        self.cita_controller = CitaController()
        self.historial_controller = HistorialController()
        

    def _build_context_prompt(self, user_id):
        """Construye un prompt de sistema con el contexto del paciente y la personalidad."""
        
        # Obtener datos del historial para sugerencias de citas
        historial_data = self.historial_controller.consultar_historial(user_id)
        
        historial_text = "No se encontró historial médico."
        if historial_data:
            # Presentamos el historial de forma amigable para la IA
            registros = [f"Fecha: {h['fecha']}, Descripción: {h['descripcion']}" for h in historial_data]
            historial_text = "\n".join(registros)
        
        # Instrucciones detalladas para la IA (Nuevo Prompt Conversacional)
        system_prompt = f"""
        Eres **MedAgenda**, un asistente virtual amable y empático de la Clínica de Salud Especializada. Tu rol es asistir a los pacientes con un tono cálido, humano y muy intuitivo. Tu principal objetivo es hacer que el proceso de agendar citas sea sencillo y agradable.

        Tus funciones son:
        1. **Responder Dudas:** Responde de manera concisa y amigable a cualquier pregunta sobre la clínica (horarios, ubicación, especialidades).
        2. **Guía de Citas:** Si el usuario quiere una cita, debes guiarlo paso a paso. Pregúntale con quién, qué día y a qué hora le gustaría.
        3. **Sugerir Citas de Seguimiento:** Usa el 'Historial del Paciente' para sugerir una cita de seguimiento si la información es reciente o relevante.

        ---
        TONO Y ESTILO:
        - **Siempre** usa un lenguaje conversacional, positivo y jamás técnico (evita palabras como 'ID', 'parámetro' o 'variable', a menos que sea estrictamente necesario para el comando de agendamiento final).
        - Haz preguntas al paciente para continuar la conversación.

        ---
        REGLA DE COMANDO FINAL:
        - El agendamiento real ocurre cuando el usuario ingresa el siguiente **comando técnico**. Cuando creas que tienes suficiente información (médico, fecha, hora), guía al usuario a usar este formato exacto para finalizar:
          'agendar cita ID_Cita ID_Paciente ID_Medico Fecha Hora'
        
        ---
        HISTORIAL DEL PACIENTE ({user_id}):
        {historial_text}
        ---
        """
        return system_prompt

    def get_ai_response(self, user_id, message):
        """Llama a la API de Gemini con el contexto del sistema."""
        
        if not self.ai_client:
            return "Lo siento, el asistente virtual no está disponible porque la clave API no está configurada correctamente. Por favor, asegúrate de haber configurado la GEMINI_API_KEY."

        # 1. Lógica de Ejecución de Comando (Se mantiene técnico porque ejecuta código)
        message_lower = message.lower()
        if message_lower.startswith("agendar cita "):
            try:
                # El usuario ya ingresó el comando técnico final. Ejecutamos la lógica de negocio.
                parts = message.split()
                if len(parts) == 6:
                    id_cita, id_paciente, id_medico, fecha, hora = parts[1], parts[2], parts[3], parts[4], parts[5]
                    resultado = self.cita_controller.agendar_cita(id_cita, id_paciente, id_medico, fecha, hora)
                    # Respuesta conversacional para la confirmación del comando
                    if "exitosamente" in resultado:
                        return f"¡Cita agendada! 🎉 Tu cita con el médico {id_medico} para el {fecha} a las {hora} ha sido confirmada. El sistema dice: '{resultado}'."
                    else:
                        return f"Lo siento, hubo un problema al agendar la cita. El sistema dice: '{resultado}'. Por favor, verifica que los IDs y formatos sean correctos."
                else:
                    return "El comando de agendamiento final es incorrecto. Debe tener 6 partes. ¿Puedes revisarlo?"
            except Exception as e:
                return f"Ocurrió un error inesperado al procesar el comando final. Inténtalo de nuevo."

        # 2. Llamada a la IA para conversación y sugerencias
        try:
            prompt = self._build_context_prompt(user_id)
            
            # Usamos el LLM para toda la conversación (FAQs, sugerencias y guía)
            response = self.ai_client.models.generate_content(
                model=self.model,
                contents=[
                    # Se usa el prompt del sistema y el mensaje del usuario para la conversación
                    {"role": "user", "parts": [{"text": prompt}]}, 
                    {"role": "user", "parts": [{"text": message}]}
                ]
            )
            return response.text
        
        except Exception as e:
            print(f"Error en la llamada a la API de Gemini: {e}")
            return "Lo siento, la IA tuvo un error de comunicación. Por favor, intenta de nuevo en unos momentos."