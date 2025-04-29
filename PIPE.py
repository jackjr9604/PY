import os
from transformers import pipeline

# Cargar el modelo de lenguaje pre-entrenado
conversational_pipeline = pipeline("conversational")

def ejecutar_comando(texto_usuario):
    # Obtener respuesta del modelo de lenguaje
    respuesta = conversational_pipeline([{"role": "user", "content": texto_usuario}])

    # Imprimir la respuesta completa
    print("Respuesta completa:", respuesta)

    # Analizar la respuesta en busca de la intención del usuario
    for output in respuesta:
        generated_text = output.get('generated_text', '')
        if "abrir calculadora" in generated_text.lower():
            # Abrir la calculadora en Windows
            os.system("calc")
            return "Calculadora abierta."
    
    # Si no se detecta la intención de abrir la calculadora
    return "Lo siento, no puedo entender ese comando."


# Inicio de la conversación
print("IA:", ejecutar_comando("Hola, ¿cómo estás?"))

while True:
    # El usuario ingresa un texto
    entrada_usuario = input("Tú: ")

    if entrada_usuario.lower() in ['adios', 'chao', 'hasta luego']:
        print("IA: ¡Hasta luego!")
        break

    # Obtener respuesta de la IA
    respuesta_ia = ejecutar_comando(entrada_usuario)
    print("IA:", respuesta_ia)
