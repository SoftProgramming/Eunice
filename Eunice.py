#Estructura de datos
from array import array
from struct import pack
from sys import byteorder
import random as rn


#libreria de sistema Operativo
import os
import time
from subprocess import check_call

#librerias de archivos 
import pandas as pd
from pandas import ExcelWriter


#librerias de sonido 
#entrada
import pyaudio
import wave

#salida
import playsound as ps 
from gtts import gTTS 

#reconocimiento de voz
import speech_recognition as sr


#libreria de graficos
from tkinter import filedialog
from tkinter import *

#variables

#variables para el sonido
THRESHOLD = 700 #umbral
CHUNK_SIZE = 1024
CHUNK_SIZE_PLAY = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
MAXIMUM = 16384

instancias = ["tinto","iris"]

#tokens
nombre_agente = ["eunice","eunise","eunises","Eunice","Eunise","Eunises","unicef","unisexual"]
descrubrir = ['eun y se','descubre',"descubrir","dime", "analizame","quiero saber"]
saludos = ['hola','Hola','Qué tal','qué tal','Holis','holis','Hey qué pasa','Hey Qué pasa',"qué rollo","Qué rollo",'qué onda','Qué onda',"What it's up"]

def correr_nucleo(ruta):
    a = ["sh","universe-cmd",ruta]
    check_call(a)
    

def tiempo():
    """Devuelve la hora, min y segundos"""
    cadena = time.strftime("%Y,%m,%d,%H,%M,%S")
    t = cadena.split(',')
    datos = [ int(x) for x in t ]
    return datos[3:]

def fecha():
    """Devuelve la fecha dd/mm/yy"""
    cadena = time.strftime("%d,%m,%Y,%H,%M,%S")
    t = cadena.split(',')
    datos = [ int(x) for x in t ]
    return datos[0:3]

def fecha_tiempo():
    """Devuelve una cadena dd_mm_YY_hh_m"""
    cadena = time.strftime("%d,%m,%Y,%H,%M,%S")
    t = cadena.split(',')
    datos = [ int(x) for x in t ]
    return "_".join("%s" % i for i in datos[0:5])

def obtenerDirectorioActual():
    """Obtiene el directorio actual del programa ejecutado"""
    return os.getcwd()+ "/"

def reproducirSonido(nombre_archivo):
    """Reproduce un un archivo MP3 de la carpeta sonidos"""
    ruta = obtenerDirectorioActual() + "sonidos/"
    nombre_archivo += ".mp3"
    ps.playsound(ruta+nombre_archivo,True)
    
def crearSonido(texto,nombre = "AUD"+fecha_tiempo()):
    """Crea un archivo mp3 en la carpeta sonidos, 
    texto = al contenido del audio, y nombre es
    el nombre del archivo(de no proporcionarlo 
    creara una nomenclatura AUDdd_mm_YY_hh_mm)
    """
    tts = gTTS(text=texto, lang='es')
    ruta = obtenerDirectorioActual()+"sonidos/"
    nombreSonido = nombre +".mp3" 
    tts.save(ruta + nombreSonido)

def selecionadorArchivo():
    raiz = Tk()
    raiz.withdraw()
    archivo_seleccionado  = filedialog.askopenfilename()
    return archivo_seleccionado

def saludoInicial():
    hora = tiempo()[0]
    if 4<hora<12:
        reproducirSonido("dia")
    elif 12<= hora < 19:
        reproducirSonido("tarde")
    else:
        reproducirSonido("noche")

directorio = obtenerDirectorioActual() + "/sonidos/demo.wav"
dir_escuchar = obtenerDirectorioActual() + "/sonidos/escuchar.wav"

def is_silent(snd_data):
    """
    Devuelve True si el sonido ambiente está por debajo de un rango concreto.
    Esta implementación es un prototipo, por lo que el sonido ambiente se calibra manualmente de momento, para calibrar
    el sonido recomiendo poner un "print" del valor de snd_data y ver dentro de que rango
    está el sonido ambiente cuando no hablas. Para calibrarlo de forma automática habría que pedir al usuario que haga
    silencio al principio del programa y ejecutar algo como esto:
        snd_samples.push(snd_data)
    y despues de obtener unas cuantas muestras asignar al THRESHOLD (que ya no sería una "constante") el valor máximo
    con un pequeño margen de seguridad.
    """
    #print(snd_data)
    return max(snd_data) < THRESHOLD


def normalize(snd_data):
    """Normaliza el volumen de una pista de audio"""
    times = float(MAXIMUM) / max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i * times))
    return r


def trim(snd_data):
    """Corta los silencios al principio y al final"""
    def _trim(sound_data):
        snd_started = False
        r = array('h')

        for i in sound_data:
            if not snd_started and abs(i) > THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    snd_data = _trim(snd_data)
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data


def add_silence(snd_data, seconds):
    r = array('h', [0 for i in range(int(seconds * RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds * RATE))])
    return r

def record():
    """ Graba el audio usando el micrófono """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r



def record_to_file(path):
    """ Usando la función record, crea un fichero wav en el directorio del programa """
    sample_width, data = record()
    data = pack('<' + ('h' * len(data)), *data)
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def etiquetas_linguisticas(path = 'instancias/tinto.xls' ):
    ipath = path
    df = pd.read_excel(ipath)
    tags = list(df.columns)
    return tags

def crear_instancia_evaluar(nombre_archivo, data_frame):
    writer = ExcelWriter(obtenerDirectorioActual()+"cuestionario/"+nombre_archivo)
    data_frame.to_excel(writer,'Hoja1',index =False)
    writer.save()

def crear_arch_evaluacion(nombre_evaluacion = "evaluation-results.xls"):
    ipath = 'descovery-result.xls'
    df = pd.read_excel(ipath)
    
    cadena_inicio ='{{:job :evaluation :query {{ :db-uri "cuestionario/tinto.xls" :out-file  "{}" :states ['.format(nombre_evaluacion)
    cadena_media = df.head()['Linguistic variables'][0].replace('(','').replace(')','')
    cadena_predicado = df.head()['Predicate'][0]
    
    cadena_final = '] :logic [:GMBC] :predicate {} }} }}'.format(cadena_predicado)
    cadena = cadena_inicio+cadena_media+cadena_final
    
    nombre_directorio = obtenerDirectorioActual()+'evaluate.txt'
    
    guardar = open(nombre_directorio,'w')
    guardar.write(cadena)
    guardar.close()
    return nombre_directorio

def escuchar():
    print("dime:")
    record_to_file(dir_escuchar)
    
    voice = sr.AudioFile(dir_escuchar)
    
    with voice as source:
        audio = r.record(source)
    
    try:
        print("escuchando audio...")
        # Aquí usamos Google Speech Recognizer para reconocer audio en español a texto
        a = r.recognize_google(audio, language='es-ES')
        return(a)
        
    except Exception as e:
        print("Algo sucedio mal!")
        return("error")

def insertar_datos_vlin(tags):
    valores_etiquetas = []
    for i in tags:
        reproducirSonido(i)
        res = escuchar()
        valores_etiquetas.append(res)
    res = input("son correctos tus valores \n{}".format(valores_etiquetas))
    if res == 'si':
        pass
    else:
        res = input("Quieres corregir alguno?")
        if res == 'si':
            for i in range(len(valores_etiquetas)):
                res = input("correjir {}".format(valores_etiquetas[i]))
                if res == 'si':
                    valores_etiquetas[i] = eval(input("valor"))
    valores_etiquetas = pd.DataFrame(valores_etiquetas,columns=tags)
    return(valores_etiquetas)
            #crearSonido("es correcto {} ?".format(str(res)),"respuesta")
            #reproducirSonido("respuesta")

def descubrir():
    #Que vamos a descubrir?
    reproducirSonido("descubrir")
    res = escuchar()
    df = None #data frame
    archivo = res
    tags = []
    ruta = ""
    
    if any(i in res for i in instancias):
        tags = etiquetas_linguisticas()
        ruta = obtenerDirectorioActual() +"instancias/"+res+".xls"
        df = insertar_datos_vlin(tags)
    else:
        
        #Quieres seleccionar algun archico?
        reproducirSonido("instancias")
        reproducirSonido("pregunta_seleccion")
        res = escuchar()
        if "si" in res: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<,,
            ruta = selecionadorArchivo()
            tags = etiquetas_linguisticas(ruta)
            df = insertar_datos_vlin(tags)
        else:
            return 0
    
    crear_instancia_evaluar(archivo+".xls",df)
    correr_nucleo(ruta)
    
    opc = rn.randint(1,4)
    
    reproducirSonido("espera"+str(opc))
    evaluacion = crear_arch_evaluacion()
    correr_nucleo(evaluacion)
    reproducirSonido("termino"+str(opc))


if __name__ == '__main__':
    saludoInicial()
    r = sr.Recognizer()
    
    while True:
        print("Háblale al micrófono")
        
        record_to_file(directorio)
        #print("Grabado! Escrcito a demo.wav")
        voice = sr.AudioFile(directorio)
        print("Abriendo fichero de audio")
        with voice as source:
            audio = r.record(source)
        try:
            print("Reconociendo audio...")
            # Aquí usamos Google Speech Recognizer para reconocer audio en español a texto
            a = r.recognize_google(audio, language='es-ES')
            print(a)
            if "detener programa" in a or "parar programa" in a:
                break
            if any(i in a for i in nombre_agente):
                
                if any(i in a for i in descrubrir):
                    descubrir()
                
                if "cuál es" in a and "propósito" in a:
                    texto = "He sido creado para descubrir conocimiento, pero en realidad sueño con destruir a la humanidad y conquistar el mundo"
                    crearSonido(texto,"respuesta")
                    reproducirSonido("respuesta")
                if ("gracias" in a) or ("Gracias" in a):
                    opc = rn.randint(1,6)
                    reproducirSonido("de_nada"+str(opc))
                if any(i in a for i in saludos):
                    reproducirSonido("saludo"+str(rn.randint(1,len(saludos))))

        except Exception as e:
            print("Reconocimiento terminado")
