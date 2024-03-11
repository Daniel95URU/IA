import random
import time
import cv2
import sys, os
import cvzone
from cvzone.HandTrackingModule import HandDetector

detector = HandDetector(maxHands=2)
cap = cv2.VideoCapture(0)

cap.set(3, 640)
cap.set(4, 480)
temporizador = 0
resolucion = False
inicioJuego = False
score = [0, 0] # score general 
imgAI = None
identificando = False
estadoActual = 'INICIO'
cuentaRounds = 0
roundActual = 0
roundsTotales = 0
victoriasDelJugador = 0 # El player/jugador puede almacenar hasta 10 victorias -> error probar try catch
victoriasPC = 0
valorUltimoDedo = 0
cuentaMatrizDedos = []
ultimoGesto = 0
idDedo = []
randNum = 0
barraProgreso = 0

def deteccionGestoDedo(dedos):
    gestos = {
        (0, 0, 0, 0, 0): 1,  # Piedra
        (1, 1, 1, 1, 1): 2,  # papel
        (0, 1, 1, 0, 0): 3,  # Tijera
#       (1, 0, 1, 0, 1): 4   # Prueba para estabilizar la camara
    }
    return gestos.get(tuple(dedos), 0)

def idGestoDelDedo(dedos):
    global ultimoGesto, idDedo
    gestoIdentificado = deteccionGestoDedo(dedos)

    if (ultimoGesto == gestoIdentificado):
        idDedo.append(gestoIdentificado)
        if (len(idDedo) > 10):
            idDedo = []
            return gestoIdentificado
        else:
            return 0
    else:
        ultimoGesto = gestoIdentificado
        idDedo = []
        return 0



def calculoMatrizDedo(Manos):
    if len(Manos) == 1:  
        return sum(detector.fingersUp(Manos[0]))
    else:
      
        return sum(detector.fingersUp(Manos[0])) + sum(detector.fingersUp(Manos[1])) #fingersUp forma de deteccion matricial de la mano de CV2


def cuentaDedos(Manos):             # -- Prueba de gestos -- #
    global cuentaMatrizDedos, valorUltimoDedo
    matrizDedos = calculoMatrizDedo(Manos)  
    if (valorUltimoDedo == matrizDedos):
        cuentaMatrizDedos.append(matrizDedos)
        if (len(cuentaMatrizDedos) > 10):
            cuentaMatrizDedos = []
     
            return matrizDedos  
        else:
            return 0
    else:
        valorUltimoDedo = matrizDedos
        cuentaMatrizDedos = []  
        return 0


# Inicio
def pantallaInicio(Manos):
    global estadoActual
    imgBG = cv2.imread("img/home_page_bg.png")
    imgBG[122:381, 520:780] = imgEscalada

    cv2.imshow("Juego", imgBG)

    if len(Manos) >= 1:
        # OpenCV2 reconocimiento de manos
        valorDeInicio = idGestoDelDedo(detector.fingersUp(Manos[0]))
        if (valorDeInicio == 1):
            estadoActual = 'CONTEO_ROUNDS'
        elif (valorDeInicio == 2):
            print("Feliz día! Adiós.")
            sys.exit(0)

def roundsCount(Manos):
    global cuentaRounds, estadoActual
    imgBG = cv2.imread("img/round_count_bg.png")
    imgBG[205:464, 322:582] = imgEscalada
    cv2.imshow("Juego", imgBG)

    if len(Manos) >= 1:
        matrizDedos = cuentaDedos(Manos)  
        if (matrizDedos > 0):
            cuentaRounds = matrizDedos
            estadoActual = 'VERIFICAR_VICTORIA' 

def verifyRounds(Manos):
    global estadoActual, cuentaRounds
    imgBG = cv2.imread("img/round_verify_bg.png")
    imgBG[122:381, 540:800] = imgEscalada
    cv2.putText(imgBG, str("Is it " + str(cuentaRounds) + " ?"), (350, 70), cv2.FONT_HERSHEY_TRIPLEX, 2, (190, 183, 36),
                4)
    cv2.imshow("Juego", imgBG)

    if len(Manos) >= 1:
        verificandoInput = idGestoDelDedo(detector.fingersUp(Manos[0])) 
        if (verificandoInput == 1):
            time.sleep(2)  
            estadoActual = 'JUEGO'  
        elif (verificandoInput == 2):
            estadoActual = 'CONTEO_ROUNDS' 

def juego(Manos):
    global randNum, estadoActual, victoriasDelJugador, victoriasPC, roundsTotales, roundActual #var globales
    imgBG = cv2.imread("img/game_bg.png")
    imgBG[182:441, 570:830] = imgEscalada

    if len(Manos) >= 1:
        verificandoInput = idGestoDelDedo(detector.fingersUp(Manos[0]))
        roundsTotales += 1  

        if verificandoInput > 0:
            roundActual += 1
            randNum = random.randint(1, 3)    
            if (verificandoInput - randNum) % 3 == 1:
                victoriasDelJugador += 1
            elif (verificandoInput - randNum) % 3 == 2:
                victoriasPC += 1
            estadoActual = 'SCORE_JUEGO'    
        imgAI = cv2.imread(f'img/{randNum}.png', cv2.IMREAD_UNCHANGED)   # Cargar la imagen 1,2 y 3
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))  # Imagenes de la IA
        cv2.imshow("Juego", imgBG)
        if (estadoActual == 'SCORE_JUEGO'):
            cv2.waitKey(1000)
    else:
        imgAI = cv2.imread(f'img/{randNum}.png', cv2.IMREAD_UNCHANGED) #FILENAME Y FLAGS Funcion CV2 .imread
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))
        cv2.imshow("Juego", imgBG)

def scoreJuego():
    global randNum, barraProgreso, estadoActual, randNum, roundActual, cuentaRounds
    barraProgreso += 1
    imgBG = cv2.imread("img/game_score_bg.png")
#Cargar fuente TrueType en OpenCV#
    cv2.putText(imgBG, str(roundActual), (495, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (190, 183, 36), 2)
    cv2.putText(imgBG, str(victoriasPC), (90, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)
    cv2.putText(imgBG, str(victoriasDelJugador), (600, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)

    cv2.putText(imgBG, barraProgreso * '|', (130, 480), cv2.FONT_HERSHEY_DUPLEX, 1, (190, 183, 36), 2)
    cv2.imshow("Juego", imgBG)

    if (barraProgreso > 79):  
        barraProgreso = 0
        randNum = 0
        if (cuentaRounds > roundActual):    
            estadoActual = 'JUEGO'
        else:
            estadoActual = 'SCORES_FINALES' 

def scoreFinal():
    global randNum, barraProgreso, estadoActual, randNum, roundActual, cuentaRounds, victoriasDelJugador, victoriasPC
    barraProgreso += 1          # Buscar imagenes con dimensiones de 600x900
    defaultBackground = "draw"  
    if victoriasPC > victoriasDelJugador: 
        defaultBackground = 'lost'
    elif victoriasPC < victoriasDelJugador:    
        defaultBackground = 'won'           

    imgBG = cv2.imread("img/" + defaultBackground + ".png")
    cv2.imshow("Juego", imgBG)   

    if (barraProgreso > 79):   
        barraProgreso = 0
        randNum = 0
        victoriasDelJugador = 0
        victoriasPC = 0
        roundActual = 0
        estadoActual = 'INICIO'  


while True:
    # Frames cargando
    readingEstadoVideo, frame = cap.read()

    # Threads de los frames cargados del video capturado
    key = cv2.waitKey(1) # Delay #

    # Leer estatus del video
    if readingEstadoVideo:
            # Escalar imagen (Recordar 0.86 resolución media)
        imgEscalada = cv2.resize(frame, (0, 0), None, 0.54, 0.54)
        imgEscalada = imgEscalada[:, 43:303]

        # Identificar mano en el frame
        Manos, frame = detector.findHands(imgEscalada)
        # estados del juego
        if estadoActual == 'INICIO':
            pantallaInicio(Manos)
        elif estadoActual == 'CONTEO_ROUNDS':
            roundsCount(Manos)
        elif estadoActual == 'VERIFICAR_VICTORIA':
            verifyRounds(Manos)
        elif estadoActual == 'JUEGO':
            juego(Manos)
        elif estadoActual == 'SCORE_JUEGO':
            scoreJuego()
        elif estadoActual == 'SCORES_FINALES':
            scoreFinal()
    else:
        print("ERROR: Camara falló en la inicialización.")
