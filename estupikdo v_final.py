# carga las librerias necesarias
import pygame, sys
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import random

# Pygame Variables
pygame.init()
pygame.mixer.init()

clock = pygame.time.Clock()

# ancho y alto de pantalla
ancho = 640
alto = 480

# asigna a la variable pantalla la ventana de trabajo
pantalla = pygame.display.set_mode( (ancho, alto))
pantalla = pygame.display.set_mode( (ancho, alto)) # esta linea sobra, es para evitar un bug en el mac

# el título que sale en la ventana de windows
pygame.display.set_caption('¿ESTÚPIKDO?')

#función preguntas
def prepara_preguntas():

    lista_total = []
    try:
        fichero_preguntas = open('preguntas.txt', encoding="utf-8")

        for lee_linea in range(0,36):
             pregunta = fichero_preguntas.readline().rstrip()  # lee una línea con pregunta y respuestas
             pregunta = tuple ( pregunta.split(',') )  # convierte la cadena leída en una tupla usando como separador la coma
             lista_total.append(pregunta) # añade la tupla a la variable lista_total
            

        fichero_preguntas.close()

    except: # evita que salte error de python y muestre lctura en caso de que falte el fichero de preguntas
        print ('Falta el fichero de configuración de preguntas')
        pygame.quit()
        sys.exit()

    lista_preguntas = []


############# todo este bloque es para comprobar el tamaño de las preguntas, solo para revisión interna
    
    # print ('Longitud de las preguntas máx. 70 caracteres')
    # print ('Longitud de las respuestas máx. 34 caracteres')
    x=1
    for pregunta,a,b,c,d,e in lista_total:
        if len(pregunta) > 70:
            print (x, pregunta, len(pregunta))
        if len(a) > 34:
            print (x, a, len(a))
        if len(b) > 34:
            print (x, b, len(b))
        if len(c) > 34:
            print (x, c, len(c))
        if len(d) > 34:
            print (x, d, len(d))
        x +=1
        
#################################################
        

    for x in range(0,35,3): # crea la lista de 12 preguntas aleatorias por niveles de 3 en 3
        i = random.randint(x,x+2)
        lista_preguntas.append(lista_total[i])

    return lista_preguntas

# variables globales
lista_preguntas = prepara_preguntas() # llama a la función de crear la lista de preguntas


# tupla con las posiciones del marcador de nivel
pos_nivel = ( (19,148) , (19,135) , (19,122), (19,109), (19,96), (19,83), (19,70), (19,57), (19,44), (19,31), (19,18), (19,5) )

# lista de premios
premios = ('100','250','500','1.000','5.000','10.000','25.000','50.000','100.000','250.000','500.000','1.000.000')


# diccionario con las zonas de pinchar con el ratón
zona_raton = { 'respuesta_a': (60,280,290,310),
               'respuesta_b': (380,280,610,310),
               'respuesta_c': (60,350,290,380),
               'respuesta_d': (380,350,610,380),
               'me_planto': (535,112,600,150),
               'si': (443,411,512,444),
               'no': (527,411,596,444)
            }

# tupla posiciones respuestas marcadas
pos_resp_marcada = ( (46,280) , (365,280) , (46,348) , (365,348) )

# posiciones botones
pos_boton = { 'me_planto' : (534,113),
              'si-no' : (443,411)
              }

# diccionario booleanas de control de flujo
control = { 'bucle_juego': False,
            'espera_confirmacion': False,
            'respuesta_confirmada': False,
            'respuesta_marcada': '',
            'pantalla_record': False,
            'pantalla_presentacion': True,
            'espera_plantarse': False,
            'plantarse_ok': False
        }

# diccionario con sonidos
sonido = {  'select': pygame.mixer.Sound('sonido_select.mp3'),
            'no_select': pygame.mixer.Sound('sonido_no_select.mp3'),
            'reloj': pygame.mixer.Sound('sonido_reloj.mp3')
            }

# diccionario con musicas
musica = {  'presentacion': 'sonido_presentacion.mp3',
            'juego': 'sonido_juego.mp3',
            'record': 'sonido_record.mp3'
            }

pregunta_actual = 0
# variables para el temporizador
# no se pueden meter en diccionario porque la función pygame.time.get_ticks() no lo permite
cronometro = 30
intervalo_act = 0
intervalo_ant = 0

debug = False # variable para activar el modo debug (muestra en el shell la respuesta correcta
            

# función pantalla de presentación
def presentacion():
    
    pygame.mixer.music.load(musica['presentacion'])
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)

    for y in range(0,480,7): # bucle para escalar la imagen en vertical de 0 a 480

        pantalla.fill((0,0,0)) # rellena de negro (borra la pantalla)
        imagen = pygame.image.load('intro.jpg') # carga el jpg en la variable imagen
        imagen = pygame.transform.scale (imagen,(640,y)) # cambia el tamaño de la imagen
        pantalla.blit(imagen,(0, (alto / 2)- (y / 2) )) # coloca la imagen en pantalla calculando los centros

        clock.tick(60)
        pygame.display.update() # actualiza la pantalla para que se vean lo que se ha pintado

    # bucle para que el programa espere que se pulse espacio para continuar
    salida = False
    while salida == False:

        for event in GAME_EVENTS.get(): # lee los eventos (teclas pulsadas, raton, etc)
            if event.type == pygame.KEYDOWN: # comprueba si en los eventos se ha pulsado alguna tecla
                if event.key == pygame.K_SPACE: # comprueba si la tecla pulsada es espacio
                    salida = True # si es espacio, cambia la variable salida a uno, con lo que el while acaba

            if event.type == GAME_GLOBALS.QUIT: # comprueba si se cierra la ventana con el boton X
                pygame.quit()
                sys.exit()

            if pygame.mouse.get_pressed()[0] == True:
                salida = True

    control['pantalla_presentacion'] = False
    control['bucle_juego'] = True
    
    pygame.mixer.music.stop()
    pygame.mixer.music.load(musica['juego'])
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


def imprime_pregunta(): # función para imprimir las preguntas

    global lista_preguntas , pregunta_actual
    fuente = pygame.font.Font(None, 24) # tipo y tamaño de letra

    # convierte los textos en imágenes para colocar
    pregunta = fuente.render(lista_preguntas[pregunta_actual][0], 1, (255,255,255) )

    fuente = pygame.font.Font(None, 20) # tipo y tamaño de letra
    
    cad_a = fuente.render('A: ', 1, (255,255,0) )
    resp_a = fuente.render(lista_preguntas[pregunta_actual][1], 1, (255,255,255) )

    cad_b = fuente.render('B: ', 1, (255,255,0) )
    resp_b = fuente.render(lista_preguntas[pregunta_actual][2], 1, (255,255,255) )

    cad_c = fuente.render('C: ', 1, (255,255,0) )
    resp_c = fuente.render(lista_preguntas[pregunta_actual][3], 1, (255,255,255) )

    cad_d = fuente.render('D: ', 1, (255,255,0) )
    resp_d = fuente.render(lista_preguntas[pregunta_actual][4], 1, (255,255,255) )

    # esta linea es solo para debug, imprime en el shell la respuesta buena
    if debug:
        print (lista_preguntas[pregunta_actual][0], lista_preguntas[pregunta_actual][5])
    
    # coloca las imágenes de los textos

    ancho_texto = pregunta.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(pregunta, ( (ancho / 2)-(ancho_texto / 2) ,200))

    pantalla.blit(cad_a, (60,288)) # imprime la A:
    pantalla.blit(resp_a, (78,288)) # imprime la respuesta A

    pantalla.blit(cad_b, (380,288)) # imprime la B:
    pantalla.blit(resp_b, (398,288)) # imprime la respuesta B

    pantalla.blit(cad_c, (60,355)) # imprime la C:
    pantalla.blit(resp_c, (78,355)) # imprime la respuesta C

    pantalla.blit(cad_d, (380,355)) # imprime la C:
    pantalla.blit(resp_d, (398,355)) # imprime la respuesta D

def imprime_nivel(): # marca con un rectángulo el nivel de pregunta en que está el juego
    global pregunta_actual , pos_nivel
    pygame.draw.rect(pantalla, (255,255,0), (pos_nivel[pregunta_actual],( 90, 14) ), 2)

    
def temporizador():
    global control , cronometro , intervalo_act, intervalo_ant

    intervalo_act = pygame.time.get_ticks() # con esta función se mira el tiempo que ha pasado desde la vez anterior
    if intervalo_act - intervalo_ant > 1032: # si han pasado 1032 ciclos (aprox. 1 segundo) descuenta 1 al cronómetro
        cronometro -= 1
        intervalo_ant = intervalo_act
        if cronometro < 6:
            pygame.mixer.Sound.play(sonido['reloj'])
        
    # improme el cronómetro en su posición
    fuente = pygame.font.Font(None, 40) # tipo y tamaño de letra
    tiempo = fuente.render(str(cronometro), 1, (255,255,0) )
    ancho_texto = tiempo.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(tiempo, ( (570)-(ancho_texto / 2) , 65))


def imprime_mensaje(mensaje): # se usa para los mensajes con pausa: se acabó en tiempo, se ha plantado, respuesta incorrecta...
    fuente = pygame.font.Font(None, 30) # tipo y tamaño de letra
    texto = fuente.render(mensaje, 1, (255,255,0) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto,  ((ancho/2)-(ancho_texto / 2) , 420))
    pygame.display.update()
    clock.tick(0.3) # hace una pequeña pausa mientras muestra el mensaje
    clock.tick(60)

def imprime_botones_sino():
        imagen = pygame.image.load('boton_si-no.png')
        pantalla.blit(imagen,pos_boton['si-no'])

def imprime_confirma_respuesta():
    
    fuente = pygame.font.Font(None, 30) # tipo y tamaño de letra
    texto = fuente.render('HA MARCADO LA RESPUESTA '+control['respuesta_marcada'], 1, (255,255,0) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto,  (((ancho-150)/2)-(ancho_texto / 2) , 410))

    texto = fuente.render('¿ES CORRECTO? (S/N)', 1, (255,255,0) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto,  (((ancho-150)/2)-(ancho_texto / 2) , 430))

    imprime_botones_sino()

def imprime_confirma_plantarse():
    
    fuente = pygame.font.Font(None, 30) # tipo y tamaño de letra
    texto = fuente.render('HA DECIDIDO PLANTARSE', 1, (255,255,0) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto,  (((ancho-150)/2)-(ancho_texto / 2) , 410))

    texto = fuente.render('¿ES CORRECTO? (S/N)', 1, (255,255,0) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto,  (((ancho-150)/2)-(ancho_texto / 2) , 430))

    imprime_botones_sino()

def comprueba_plantarse():
    global control
    for event in GAME_EVENTS.get(): # comprueba pulsaciones de teclas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                control['espera_plantarse'] = False
                control['plantarse_ok'] = True
                pygame.mixer.Sound.play(sonido['select'])
            elif event.key == pygame.K_n:
                control['espera_plantarse'] = False
                control['plantarse_ok'] = False
                control['respuesta_marcada'] = ''
                pygame.mixer.Sound.play(sonido['no_select'])

        # modo ratón
        posicion_raton = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] == True:
                
            if posicion_raton[0] > zona_raton['si'][0] and posicion_raton[0] < zona_raton['si'][2]:
                if posicion_raton[1] > zona_raton['si'][1] and posicion_raton[1] < zona_raton['si'][3]:
                    pygame.mixer.Sound.play(sonido['select'])
                    control['espera_plantarse'] = False
                    control['plantarse_ok'] = True

            if posicion_raton[0] > zona_raton['no'][0] and posicion_raton[0] < zona_raton['no'][2]:
                if posicion_raton[1] > zona_raton['no'][1] and posicion_raton[1] < zona_raton['no'][3]:
                    pygame.mixer.Sound.play(sonido['no_select'])
                    control['espera_plantarse'] = False
                    control['plantarse_ok'] = False
                    control['respuesta_marcada'] = ''

def comprueba_confirmacion():
    global control
    for event in GAME_EVENTS.get(): # comprueba pulsaciones de teclas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                control['espera_confirmacion'] = False
                control['respuesta_confirmada'] = True
                pygame.mixer.Sound.play(sonido['select'])
            elif event.key == pygame.K_n:
                control['espera_confirmacion'] = False
                control['respuesta_confirmada'] = False
                control['respuesta_marcada'] = ''
                pygame.mixer.Sound.play(sonido['no_select'])

        # modo ratón
        posicion_raton = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] == True:
                
            if posicion_raton[0] > zona_raton['si'][0] and posicion_raton[0] < zona_raton['si'][2]:
                if posicion_raton[1] > zona_raton['si'][1] and posicion_raton[1] < zona_raton['si'][3]:
                    control['espera_confirmacion'] = False
                    control['respuesta_confirmada'] = True
                    pygame.mixer.Sound.play(sonido['select'])

            if posicion_raton[0] > zona_raton['no'][0] and posicion_raton[0] < zona_raton['no'][2]:
                if posicion_raton[1] > zona_raton['no'][1] and posicion_raton[1] < zona_raton['no'][3]:
                    control['espera_confirmacion'] = False
                    control['respuesta_confirmada'] = False
                    control['respuesta_marcada'] = ''
                    pygame.mixer.Sound.play(sonido['no_select'])

def comprueba_respuesta():
    global control,debug
    control['respuesta_marcada'] = ''
    for event in GAME_EVENTS.get(): # comprueba pulsaciones de teclas
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_a:
                control['respuesta_marcada'] = 'A'
                control['espera_confirmacion'] = True
                pygame.mixer.Sound.play(sonido['select'])
            if event.key == pygame.K_b:
                control['respuesta_marcada'] = 'B'
                control['espera_confirmacion'] = True
                pygame.mixer.Sound.play(sonido['select'])
            if event.key == pygame.K_c:
                control['respuesta_marcada'] = 'C'
                control['espera_confirmacion'] = True
                pygame.mixer.Sound.play(sonido['select'])
            if event.key == pygame.K_d:
                control['respuesta_marcada'] = 'D'
                control['espera_confirmacion'] = True
                pygame.mixer.Sound.play(sonido['select'])

            if event.key == pygame.K_p:
                control['respuesta_marcada'] = 'P'
                control['espera_plantarse'] = True
                control['plantarse_ok'] = False
                pygame.mixer.Sound.play(sonido['select'])

            if event.key == pygame.K_0: # si se pulsa 0 entra en el modo debug
                if debug == True:
                    debug = False
                elif debug == False:
                    debug = True

        ### añadir controles de pulsación de ratón
        posicion_raton = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] == True:
                
            if posicion_raton[0] > zona_raton['respuesta_a'][0] and posicion_raton[0] < zona_raton['respuesta_a'][2]:
                if posicion_raton[1] > zona_raton['respuesta_a'][1] and posicion_raton[1] < zona_raton['respuesta_a'][3]:
                    control['respuesta_marcada'] = 'A'
                    control['espera_confirmacion'] = True
                    pygame.mixer.Sound.play(sonido['select'])

            if posicion_raton[0] > zona_raton['respuesta_b'][0] and posicion_raton[0] < zona_raton['respuesta_b'][2]:
                if posicion_raton[1] > zona_raton['respuesta_b'][1] and posicion_raton[1] < zona_raton['respuesta_b'][3]:
                    control['respuesta_marcada'] = 'B'
                    control['espera_confirmacion'] = True
                    pygame.mixer.Sound.play(sonido['select'])

            if posicion_raton[0] > zona_raton['respuesta_c'][0] and posicion_raton[0] < zona_raton['respuesta_c'][2]:
                if posicion_raton[1] > zona_raton['respuesta_c'][1] and posicion_raton[1] < zona_raton['respuesta_c'][3]:
                    control['respuesta_marcada'] = 'C'
                    control['espera_confirmacion'] = True
                    pygame.mixer.Sound.play(sonido['select'])

            if posicion_raton[0] > zona_raton['respuesta_d'][0] and posicion_raton[0] < zona_raton['respuesta_d'][2]:
                if posicion_raton[1] > zona_raton['respuesta_d'][1] and posicion_raton[1] < zona_raton['respuesta_d'][3]:
                    control['respuesta_marcada'] = 'D'
                    control['espera_confirmacion'] = True
                    pygame.mixer.Sound.play(sonido['select'])

            if posicion_raton[0] > zona_raton['me_planto'][0] and posicion_raton[0] < zona_raton['me_planto'][2]:
                if posicion_raton[1] > zona_raton['me_planto'][1] and posicion_raton[1] < zona_raton['me_planto'][3]:
                    control['respuesta_marcada'] = 'P'
                    control['espera_plantarse'] = True
                    control['plantarse_ok'] = False
                    pygame.mixer.Sound.play(sonido['select'])


        if event.type == GAME_GLOBALS.QUIT: # comprueba si se cierra la ventana con el boton X
            pygame.quit()
            sys.exit()

def reinicia_variables_acierto():
    global pregunta_actual,cronometro,control
    
    control['espera_confirmacion'] = False
    control['respuesta_confirmada'] = False
    dibuja_escenario()
    imprime_mensaje('RESPUESTA CORRECTA')
    control['respuesta_marcada'] = ''
    pregunta_actual += 1
    cronometro = 30


def reinicia_variables_partida():
    global control
    control['bucle_juego'] = False
    control['pantalla_record'] = True
    control['respuesta_marcada'] = ''
    control['espera_confirmacion'] = False
    control['respuesta_confirmada'] = False


def bucle_principal():

    global lista_preguntas , pregunta_actual , control , cronometro

    if pregunta_actual > 11: # comprueba el máximo de preguntas
        control['bucle_juego'] = False
        control['pantalla_record'] = True
        return
            
    dibuja_escenario()

    if cronometro <= 0: # comprueba si el tiempo ha llegado a 0
        imprime_mensaje('SE ACABÓ EL TIEMPO')
        reinicia_variables_partida()
        return

    temporizador() # llama a la función del temporizador

    if control['espera_confirmacion'] == True:
        imprime_confirma_respuesta()

    if control['espera_plantarse'] == True:
        imprime_confirma_plantarse()

    clock.tick(60)
    pygame.display.update()

    if control['respuesta_marcada'] not in ('A','B','C','D','P'):
        comprueba_respuesta()

    if control['espera_confirmacion'] == True:
        comprueba_confirmacion()

    if control['espera_plantarse'] == True:
        comprueba_plantarse()

    if control['plantarse_ok'] == True:
        dibuja_escenario()
        imprime_mensaje('SE HA PLANTADO')
        control['pantalla_record'] = True
    
    if control['respuesta_confirmada'] == True:
        if control['respuesta_marcada'] == 'A' and lista_preguntas[pregunta_actual][5] == 'A':
            reinicia_variables_acierto()
            
        elif control['respuesta_marcada'] == 'B' and lista_preguntas[pregunta_actual][5] == 'B':
            reinicia_variables_acierto()

        elif control['respuesta_marcada'] == 'C' and lista_preguntas[pregunta_actual][5] == 'C':
            reinicia_variables_acierto()

        elif control['respuesta_marcada'] == 'D' and lista_preguntas[pregunta_actual][5] == 'D':
            reinicia_variables_acierto()
        else:
            dibuja_escenario()
            imprime_mensaje('RESPUESTA INCORRECTA')
            reinicia_variables_partida()
            
def dibuja_escenario():
    pantalla.fill((0,0,0)) # rellena de negro (borra la pantalla)
    imagen = pygame.image.load('escenario-final.jpg') # carga el jpg en la variable imagen
    imagen = pygame.transform.scale (imagen,(ancho,alto)) # cambia el tamaño de la imagen
    pantalla.blit(imagen,(0,0)) # coloca la imagen en pantalla calculando los centros

    marca_respuesta() # llama a la función de señalar re    spuesta        
    imprime_pregunta() # llama a la función de imprimir pregunta
    imprime_nivel() # llama a la función de marcar el nivel


    fuente = pygame.font.Font(None, 20) # tipo y tamaño de letra
    texto = fuente.render('PULSE "P" PARA PLANTARSE', 1, (255,255,255) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto,  ((ancho/2)-(ancho_texto / 2) , 250))

def marca_respuesta():
    if control['respuesta_marcada'] == 'A':
        imagen = pygame.image.load('boton_resp-marcada.png')
        pantalla.blit(imagen,pos_resp_marcada[0])
    elif control['respuesta_marcada'] == 'B':
        imagen = pygame.image.load('boton_resp-marcada.png')
        pantalla.blit(imagen,pos_resp_marcada[1])
    elif control['respuesta_marcada'] == 'C':
        imagen = pygame.image.load('boton_resp-marcada.png')
        pantalla.blit(imagen,pos_resp_marcada[2])
    elif control['respuesta_marcada'] == 'D':
        imagen = pygame.image.load('boton_resp-marcada.png')
        pantalla.blit(imagen,pos_resp_marcada[3])
        
    if control['respuesta_marcada'] == 'P':
        imagen = pygame.image.load('boton_plant.png')
        pantalla.blit(imagen,pos_boton['me_planto'])


def pantalla_record():

    pygame.mixer.music.load(musica['record'])
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)
    
    pantalla.fill((0,0,0)) # rellena de negro (borra la pantalla)
    imagen = pygame.image.load('resultado.jpg') # carga el jpg en la variable imagen
    imagen = pygame.transform.scale (imagen,(ancho,alto)) # cambia el tamaño de la imagen
    pantalla.blit(imagen,(0,0)) # coloca la imagen en pantalla calculando los centros

    # comprueba el premio según las preguntas con seguro
    if pregunta_actual <= 3:
        record = '0 Bitcoin'
    if pregunta_actual >= 4 and pregunta_actual < 8:
        record = '1.000 Bitcoins'
    if pregunta_actual >= 8 and pregunta_actual <= 11:
        record = '50.000 Bitcoins'
    if pregunta_actual == 12:
        record = '1.000.000 Bitcoins'

    # si se ha plantado el premio corresponde a la pregunta anterior donde se plantó
    if control['plantarse_ok'] == True and pregunta_actual > 0 :
        record = premios[pregunta_actual-1]+ ' Bitcoins'
        
    fuente = pygame.font.Font(None, 35) # tipo y tamaño de letra

    texto = fuente.render(str(pregunta_actual)+' respuestas', 1, (255,255,0) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto, ( (ancho/2)-(ancho_texto / 2) , 245))

    texto = fuente.render(record, 1, (255,255,0) )
    ancho_texto = texto.get_width() # calcula el ancho del texto para centrarlo
    pantalla.blit(texto, ( (ancho/2)-(ancho_texto / 2) , 353))

    clock.tick(60)
    pygame.display.update() # actualiza la pantalla para que se vean lo que se ha pintado

    # bucle para que el programa espere que se pulse espacio para continuar
    salida = False
    while salida == False:

        for event in GAME_EVENTS.get(): # lee los eventos (teclas pulsadas, raton, etc)
            if event.type == pygame.KEYDOWN: # comprueba si en los eventos se ha pulsado alguna tecla
                if event.key == pygame.K_SPACE: # comprueba si la tecla pulsada es espacio
                    salida = True # si es espacio, cambia la variable salida a uno, con lo que el while acaba

            if event.type == GAME_GLOBALS.QUIT: # comprueba si se cierra la ventana con el boton X
                pygame.quit()
                sys.exit()

            if pygame.mouse.get_pressed()[0] == True:
                salida = True

    pygame.mixer.music.stop()


while True:

 #   if pregunta_actual > 11: # comprueba el máximo de preguntas
 #       control['bucle_juego'] = False
 #       control['pantalla_record'] == True
    
    if control['pantalla_presentacion'] == True:
        presentacion()

    if control['bucle_juego'] == True:
        bucle_principal()

    if control['pantalla_record'] == True:

        pantalla_record()

        lista_preguntas = prepara_preguntas()
        
        control = { 'bucle_juego': False,
                    'espera_confirmacion': False,
                    'respuesta_confirmada': False,
                    'respuesta_marcada': '',
                    'pantalla_record': False,
                    'pantalla_presentacion': True,
                    'espera_plantarse': False,
                    'plantarse_ok': False
        }
        pregunta_actual = 0
        cronometro = 30
        

pygame.quit()
sys.exit()
            

            

    


