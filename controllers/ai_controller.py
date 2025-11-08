import os
import google.generativeai as genai
from services import medico_service, cita_service
from datetime import datetime

class AiController:
    def __init__(self, user):
        self.user = user  # El usuario que está chateando
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada en .env")
            
        genai.configure(api_key=api_key)
        
        # Definir las herramientas que la IA puede usar
        self.tools = {
            "get_medicos_disponibles": self.get_medicos_disponibles,
            "agendar_cita": self.agendar_cita,
            "get_mis_citas": self.get_mis_citas,
        }
        
        self.model = genai.GenerativeModel(
            # --- ESTA ES LA CORRECCIÓN (v3) ---
            model_name='gemini-1.0-pro',
            # --- FIN DE LA CORRECCIÓN ---
            system_instruction=self.get_system_prompt(),
            tools=list(self.tools.values()) # Pasar las funciones a Gemini
        )
        self.chat = self.model.start_chat(history=[])

    def get_system_prompt(self):
        """Genera el prompt del sistema basado en el usuario."""
        return f"""
        Eres 'MedAgenda', un asistente virtual médico de clase mundial.
        Tu propósito es ayudar a los pacientes a gestionar su salud.
        Eres amable, empático y extremadamente competente.

        Información del Usuario Actual:
        - Nombre: {self.user['nombre_completo']}
        - ID de Paciente: {self.user['paciente_id']}
        - Email: {self.user['email']}

        Reglas:
        1. NUNCA pidas el ID del paciente, ya lo sabes ({self.user['paciente_id']}).
        2. Para agendar, DEBES usar la herramienta 'agendar_cita'.
        3. Antes de agendar, usa 'get_medicos_disponibles' para encontrar al médico y su ID.
        4. El formato de fecha y hora para agendar es 'AAAA-MM-DDTHH:MM'. Hoy es {datetime.now().strftime('%Y-%m-%d')}.
        5. Sé proactivo. Si el paciente pregunta por sus citas, usa 'get_mis_citas'.
        """

    def handle_message(self, message):
        """
        Maneja un nuevo mensaje del usuario y ejecuta el ciclo de IA (Tool Calling).
        """
        try:
            # 1. Enviar mensaje a Gemini
            response = self.chat.send_message(message)
            
            # 2. Revisar si la IA quiere usar una herramienta
            while response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                tool_name = function_call.name
                tool_args = {key: value for key, value in function_call.args.items()}
                
                print(f"IA quiere llamar a: {tool_name} con args: {tool_args}")
                
                # 3. Ejecutar la herramienta (función de Python)
                if tool_name in self.tools:
                    tool_function = self.tools[tool_name]
                    
                    # --- Lógica especial de IA ---
                    # Inyectar el paciente_id si la IA no lo sabe
                    if 'paciente_id' not in tool_args and (tool_name == 'agendar_cita' or tool_name == 'get_mis_citas'):
                        tool_args['paciente_id'] = self.user['paciente_id']
                    
                    tool_result = tool_function(**tool_args)
                else:
                    tool_result = {"error": f"Herramienta '{tool_name}' desconocida."}
                
                print(f"Resultado de la herramienta: {tool_result}")

                # 4. Enviar el resultado de la herramienta de vuelta a Gemini
                response = self.chat.send_message(
                    genai.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=tool_name,
                            response={'result': tool_result}
                        )
                    )
                )
            
            # 5. La IA ha respondido con texto
            return response.text

        except Exception as e:
            # Imprime el error real en la terminal (esto es lo que vimos)
            print(f"Error en AiController: {e}") 
            return "Lo siento, tuve un error procesando tu solicitud. Por favor, intenta de nuevo."

    # --- Definiciones de Herramientas (Las funciones que la IA puede llamar) ---
    
    def get_medicos_disponibles(self, especialidad: str = None):
        """
        Obtiene una lista de médicos. Puede filtrarse por especialidad.
        
        Args:
            especialidad (str, optional): La especialidad a filtrar (ej. 'Cardiología').
        """
        print(f"Buscando médicos por especialidad: {especialidad}")
        medicos = medico_service.get_medicos(especialidad_filter=especialidad)
        if not medicos:
            return {"error": "No se encontraron médicos con esa especialidad."}
        return {"medicos": medicos}

    def agendar_cita(self, paciente_id: int, medico_id: int, fecha_hora_inicio: str, notas_paciente: str = ""):
        """
        Agenda una nueva cita para el paciente.
        
        Args:
            paciente_id (int): El ID del paciente.
            medico_id (int): El ID del médico.
            fecha_hora_inicio (str): La fecha y hora de inicio en formato 'AAAA-MM-DDTHH:MM'.
            notas_paciente (str, optional): Notas que el paciente quiera añadir.
        """
        print(f"Intentando agendar cita para paciente {paciente_id} con médico {medico_id} a las {fecha_hora_inicio}")
        resultado = cita_service.agendar_nueva_cita(
            paciente_id=paciente_id,
            medico_id=medico_id,
            fecha_hora_inicio_str=fecha_hora_inicio,
            notas=notas_paciente
        )
        return resultado # Devuelve el dict de éxito o error

    def get_mis_citas(self, paciente_id: int):
        """
        Obtiene una lista de todas las citas (pasadas y futuras) del paciente.
        
        Args:
            paciente_id (int): El ID del paciente.
        """
        print(f"Buscando citas para paciente {paciente_id}")
        citas = cita_service.get_citas_paciente(paciente_id=paciente_id)
        if not citas:
            return {"error": "No tienes citas registradas."}
        return {"citas": citas}