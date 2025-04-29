#Esta biblioteca proporciona funciones para generar números aleatorios. Puede ser útil en una variedad de situaciones, como en la creación de juegos, pruebas y simulaciones donde se necesitan elementos aleatorios.
import random
#Esta biblioteca proporciona funciones para interactuar con el sistema operativo. Puede utilizarse para realizar operaciones relacionadas con archivos y directorios, como navegación por el sistema de archivos, manipulación de rutas, manipulación de variables de entorno, etc.
import os
#Esta biblioteca permite automatizar las acciones del mouse y del teclado en el sistema operativo. Puede utilizarse para escribir scripts que controlen la interacción del usuario con la interfaz gráfica de usuario (GUI), como hacer clic en botones, escribir texto, mover el mouse, etc.
import pyautogui
#Esta biblioteca proporciona funciones relacionadas con el tiempo, como la obtención de la hora actual, la medición de lapsos de tiempo y la suspensión de la ejecución del programa durante un período de tiempo específico.
import time

import re

import webbrowser

def responder_saludo():#Esta línea define una función llamada responder_saludo sin ningún argumento.
    saludos = [
    "Hola",
    "Hola, ¿cómo estás?",
    "¿Qué tal?",
    "Saludos",
    "¿Cómo va?",
    "¿Qué hay?",
    "Hola, ¿qué tal estás?",
    "Hey",
    "Hola, ¿qué pasa?",
    "¿Todo bien?",
    "¿Cómo te va?",
    "¿Cómo estás?",
    "¡Hola!",
    "¿Qué onda?",
    "¿Qué hay de nuevo?",
    "¿Cómo te encuentras?",
    "¿Qué cuentas?",
    "¿Qué tal el día?",
    "¿Cómo va todo?",
    "¿Qué hubo?",
    "¿Cómo te sientes hoy?",
    "¿Qué tal tu día?",
    "¿Cómo va eso?",
    "¿Qué tal la vida?",
    "¿Qué pasa?",
    "Hola, ¿qué hay de nuevo?",
    "¿Qué haces?",
    "¿Qué tal la jornada?",
    "¿Cómo va la semana?",
    "¿Qué tal la mañana?",
    "¿Qué novedades hay?",
    "¿Cómo te encuentras hoy?",
    "¿Cómo va todo por aquí?",
    "¿Qué tal tu estado?",
    "¿Qué cuentas?",
    "¿Cómo te va en esta jornada?",
    "¿Cómo amaneciste?",
    "¿Cómo va el día de hoy?",
    "¿Qué tal la vida?",
        ]#Aquí se crea una lista llamada saludos que contiene varios saludos como cadenas de texto. Estos saludos son posibles respuestas que el chatbot puede dar cuando alguien lo saluda.
    print("AI:", random.choice(saludos))

def formas_de_saludar():
    saludo = [
    "hola",
    "hola cómo estás",
    "buenos días",
    "buenas tardes",
    "buenas noches",
    "qué tal",
    "saludos",
    "cómo va",
    "qué hay",
    "hola qué tal estás",
    "hey",
    "hola qué pasa",
    "todo bien",
    "cómo te va",
    "cómo estás",
    "qué onda",
    "qué hay de nuevo",
    "cómo te encuentras",
    "qué cuentas",
    "qué tal el día",
    "cómo va todo",
    "qué hubo",
    "cómo te sientes hoy",
    "qué tal tu día",
    "cómo va eso",
    "qué tal la vida",
    "qué pasa",
    "hola qué hay de nuevo",
    "cómo estuvo tu día",
    "qué haces",
    "qué tal la jornada",
    "cómo va la semana",
    "qué tal la mañana",
    "qué novedades hay",
    "cómo te encuentras hoy",
    "cómo va todo por aquí",
    "qué tal tu estado",
    "qué cuentas",
    "cómo te va en esta jornada",
    "cómo amaneciste",
    "cómo va el día de hoy",
    "qué tal la vida",
    "qué tal"
        "hola",
    "hola como estas",
    "buenos dias",
    "buenas tardes",
    "buenas noches",
    "que tal",
    "saludos",
    "como va",
    "que hay",
    "hola que tal estas",
    "hey",
    "hola que pasa",
    "todo bien",
    "como te va",
    "como estas",
    "hola",
    "que onda",
    "que hay de nuevo",
    "como te encuentras",
    "que cuentas",
    "que tal el dia",
    "como va todo",
    "que hubo",
    "como te sientes hoy",
    "que tal tu dia",
    "como va eso",
    "que tal la vida",
    "que pasa",
    "hola que hay de nuevo",
    "como estuvo tu dia",
    "que haces",
    "que tal la jornada",
    "como va la semana",
    "que tal la manana",
    "que novedades hay",
    "como te encuentras hoy",
    "como va todo por aqui",
    "que tal tu estado",
    "que cuentas",
    "como te va en esta jornada",
    "como amaneciste",
    "como va el dia de hoy",
    "que tal la vida",
    "que tal la"
    ]
    return saludo

def verificar_saludo(input):
    saludo = formas_de_saludar()
    if input.lower() in saludo:
        return "saludo"
    else:
        return "indefinido"

def formas_de_afirmar():
    afirmaciones = ["si", "claro", "por supuesto", "absolutamente", "exacto", "correcto", 'aja']
    return afirmaciones

def formas_de_negar():
    negaciones = ["no", "nunca", "jamas", "de ninguna manera", "incorrecto"]
    return negaciones

def verificar_afirmacion_o_negacion(input_usuario):
    afirmaciones = formas_de_afirmar()
    negaciones = formas_de_negar()
    if input_usuario.lower() in afirmaciones:
        return "afirmación"
    elif input_usuario.lower() in negaciones:
        return "negación"
    else:
        return "indefinido"

def tarea():
    nueva = ['Que quieres hacer?', 'que haremos hoy?']
    print('AI:', random.choice(nueva))

def continuar_calculo():
    intentos = 0
    while True:
        continuar = input('IA: ¿Deseas realizar otra operación? ')
        tipo = verificar_afirmacion_o_negacion(continuar)
        if tipo == "afirmación":
            cerrar_calculadora()
            print('IA: Dime qué operación calcular')
            return True
        elif tipo == "negación":
            cerrar_calculadora()
            print('AI: Ok volvere a saludar')
            volver_al_inicio()
            return False
        else:
            intentos += 1
            if intentos <= 3:
                mensajes_error = ["Por favor, responde 'sí' o 'no'.", "No entendí tu respuesta. ¿Podrías responder 'sí' o 'no'?", "¿Podrías repetir eso? No entendí."]
                print("IA:", random.choice(mensajes_error))
            elif intentos > 3:
                print("IA: Me parece que estás teniendo dificultades. ¡Hasta luego!")
                return False

def validar_expresion(expresion):
    # Expresión regular para validar la entrada como una expresión matemática básica
    patron = re.compile(r'^[\d\s()+\-*/.]*$')
    return patron.match(expresion) is not None

def realizar_operacion_calculadora():
    intentos = 0
    while True:
        operacion = input("Tú: ")
        if operacion.lower() == 'cerrar':
            print('IA: Entonces no :)')
            break
        elif operacion == 'adios':
            terminar_conversacion()
            return
        elif not validar_expresion(operacion):
            print("IA: Error al evaluar la expresión: expresión no válida")
            return
        resultado = str(eval(operacion))
        os.system('start calc')
        time.sleep(1)
        pyautogui.write(resultado, interval=0.1)
        pyautogui.press('enter')
        if not continuar_calculo():
            return
        
def volver_al_inicio():
        return responder_saludo()

def cerrar_calculadora():
    os.system('taskkill /f /im CalculatorApp.exe > nul 2>&1')  # Cierra la calculadora

def abrir_aplicacion(aplicacion):# aqui se crea una funcion para abrir diferentes aplicaciones
    if aplicacion.lower() == 'excel': #si la funcion aplicacion (se convierte a minuscula) y si lo q se pasa es igual a 'excel' pasa la funcion para inciar el programa
        if os.name == 'posix':  # Para sistemas tipo Unix (Linux, macOS)
            os.system('open -a "Microsoft Excel"')
        elif os.name == 'nt':   # Para sistemas Windows
            os.system('start excel')
    elif aplicacion.lower() == 'word':
        if os.name == 'posix':  # Para sistemas tipo Unix (Linux, macOS)
            os.system('open -a "Microsoft Word"')
        elif os.name == 'nt':   # Para sistemas Windows
            os.system('start winword')

def listar_aplicaciones_disponibles():# se cerea una funcion para listar las ap´licaciones
    return ['calculadora', 'excel', 'word']

def terminar_conversacion():# se crea una funcion para terminar la conversacion donde regresa una linea definida
    despedida = ['adios', 'chao', 'hasta luego']
    print('AI:', random.choice(despedida))

def youtube():
    while True:
        print('AI: te gustaria buscar algo en especial?')
        buscar = input("Tu: ").lower()
        tipo = verificar_afirmacion_o_negacion(buscar)
        if tipo == 'afirmación':
            print('AI: que quieres buscar?')
            termino_busqueda = input("Tu: ").lower()
            url_busqueda = "https://www.youtube.com/results?search_query=" + "+".join(termino_busqueda.split())
            webbrowser.open(url_busqueda)
            print('AI: ya mismo')
            break
        elif tipo == 'negación':
            webbrowser.open('https://www.youtube.com')
            print('AI: solo lo abrire')   
            break
        elif buscar == 'adios':
            terminar_conversacion()
            break
        else:
            print('AI: lo siento, no te entendi')

while True:
    accion_usuario = input("Tú: ").lower()
    tipo = verificar_saludo(accion_usuario)

    if tipo == 'saludo':
        responder_saludo()
        tarea()
        accion_usuario = input("Tú: ").lower()
        if accion_usuario in ['abrir una aplicacion', 'abrir una app']:
            print("AI: Las aplicaciones disponibles son:", ', '.join(listar_aplicaciones_disponibles()))
            print("AI: ¿Qué aplicación deseas abrir?")
            aplicacion = input("Tú: ").lower()
            if aplicacion == 'adios':
                terminar_conversacion()
                break
            elif aplicacion in listar_aplicaciones_disponibles():
                print("AI: Abriendo", aplicacion)
                abrir_aplicacion(aplicacion)
                if aplicacion == 'calculadora':
                    print("AI: ¿Qué operación deseas realizar en la calculadora?")
                    realizar_operacion_calculadora()

            elif aplicacion =='youtube':
                youtube()
                            
            else:
                print("AI: Lo siento, no tengo esa aplicación disponible.")
    
    elif accion_usuario == 'adios':
        terminar_conversacion()
        break
    else:
        while True:
            print('AI: Lo siento, no entendí eso. ¿Puedes repetirlo?')
            break
            


            