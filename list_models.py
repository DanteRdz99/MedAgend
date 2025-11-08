import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Cargar la API Key del .env
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: No se encontró GEMINI_API_KEY en el archivo .env")
    exit()

print("Conectando a Google con tu API key...")

try:
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error al configurar la API key: {e}")
    exit()

print("="*40)
print("Buscando modelos disponibles para ti:")
print("="*40)

try:
    # 2. Pedir la lista de modelos
    model_found = False
    for model in genai.list_models():
        # 3. Imprimir solo los modelos que pueden generar contenido (chatear)
        if 'generateContent' in model.supported_generation_methods:
            print(f"¡Modelo encontrado!")
            print(f"  Nombre del Modelo: {model.name}")
            print(f"  Descripción: {model.description}\n")
            model_found = True
            
    if not model_found:
        print("No se encontraron modelos de 'generateContent'. Esto es extraño.")
        print("¿Está la API 'Generative Language' habilitada en Google Cloud?")

except Exception as e:
    print("\n--- ¡ERROR! ---")
    print(f"No se pudo obtener la lista de modelos.")
    print(f"Error detallado: {e}")
    print("Verifica que tu API Key sea correcta y que la Facturación esté activa.")

print("="*40)
print("Por favor, copia el 'Nombre del Modelo' (ej. 'models/gemini-1.0-pro') y pégalo en el chat.")