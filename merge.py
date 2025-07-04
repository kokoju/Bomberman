# Módulos necesarios 
from pygame import *  # Importa todos los módulos de Pygame necesarios para el juego
from time import sleep  # Importa sleep para manejar los Threads
from random import choice, randint  # Importa choice para seleccionar elementos aleatorios de listas (movimiento enemigo)
from threading import Thread  # Importa los Threads para el manejo de entidades en paralelo
from config import *  # Importa las configuraciones del juego, como dimensiones y FPS
from assets import *  # Importa los sprites del jugador y otros elementos visuales
from niveles import *
from math import hypot

# Usaremos una definición HD (1280x720p)
# En la parte superior de la pantalla, dejaremos una HUD de tamaño 1280x176 
# Abajo del HUD, haremos matrices de 11x26 (siendo cada bloque de 48x48): esto nos dejará con 32 pixeles sobrantes, repartidos en 16 pixeles en la parte izquierda y 16 pixeles en la parte derecha de la pantalla
# Además, dejé un espacio de 16 pixeles entre la matriz y el borde inferior, para que no se vea tan pegado
# Haremos los niveles con matrices (11x26), y como no se requiere crear nuevos, podemos ponerlos dentro del archivo de código

# ==========================================================================
#  GUARDADO Y LECTURA DE ARCHIVOS
# ==========================================================================

# Guarda un string en un archivo
def guardar_archivo(file_path, content):
        archivo = open(file_path, 'w')  # w crea o trunca el archivo
        archivo.write(content)
        archivo.close()
        
# Lee la información de un archivo y devuelve su contenido evaluado según su formato
def leer_archivo(path):
        archivo = open(path, 'r')
        contenido = archivo.read()
        archivo.close()
        if not contenido.strip():  # Si el contenido está vacío, devuelve una lista vacía
            return []
        return eval(contenido)

# Ordena por el puntaje (índice 1) de mayor a menor
# key=lambda x: x[1]  # Ordena por el segundo elemento de cada tupla (el puntaje)
# key es una función que toma un elemento de la lista y devuelve el valor por el cual se ordenará
# 
puntajes = sorted(leer_archivo(ARCHIVO_PUNTAJES), key=lambda elemento: elemento[1], reverse=True)  

font.init()  # Inicializa el módulo de fuentes de Pygame
fuente_texto = font.Font("assets/FuenteTexto.ttf", 30)  # Tipografía del texto del juego

# ==========================================================================
#  ELEMENTOS RELACIONADOS CON EL JUGADOR
# ==========================================================================

# Clase Jugador
class Jugador:
    def __init__(self, jugar, num_skin=2):
        self.jugar = jugar
        self.pantalla = jugar.pantalla_juego  # Pantalla donde se dibuja el jugador
        self.nivel = jugar.nivel  # Nivel actual del jugador (se usa para verificar colisiones)

        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.num_skin = num_skin  # Número de skin del jugador (se puede cambiar para personalizar el jugador)
        self.skin_hoja_sprites = cargar_skins(self.num_skin, puntos_iniciales_skins_jugador)  # Carga la skin del jugador desde la hoja de sprites

        self.direccion = "abajo"  # Dirección inicial del jugador (y a la que está mirando)
        self.frame = 0  # Frame actual del sprite del jugador
        self.sprite = self.skin_hoja_sprites[self.direccion][self.frame] #Sprite inicial del jugador
        
        self.vidas = VIDAS  # Cantidad de vidas del jugador
        self.vidas_max = VIDAS  # Cantidad de vidas máximas del jugador
        self.cantidad_bombas = CANTIDAD_BOMBAS  # Cantidad de bombas que puede colocar el jugador AL MISMO TIEMPO, sus bombas son infinitas
        self.velocidad = 5  # Velocidad de movimiento del jugador (en pixeles)
        self.golpe = GOLPE_INICIAL_BOMBA  # Daño que causa el jugador al explotar una bomba
        self.rango = 1 # Rango inicial de la bomba
        self.moviendose = False  # Indica si el jugador se está moviendo o no
        
        self.puntaje_total = 0  # Puntaje total del jugador
        self.puntaje = 0  # Puntaje del jugador

        # Habilidades e ítems del jugador
        self.tiene_habilidad = True
        self.habilidad_en_uso = False
        self.tiene_item_1 = False 
        self.tiene_item_2 = False

        self.tiempo_desde_habilidad = pg.time.get_ticks()
        self.enfriamiento_habilidad = ENFRIAMIENTO_HABILIDAD

        self.tiene_llave = False  # Indica si el jugador tiene la llave para abrir la puerta del siguente nivel

        self.mascara = pg.mask.from_surface(self.sprite)
        self.rect = Rect(X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR, ANCHO_JUGADOR, ALTO_JUGADOR) #  Rectangulo del jugador para posicion y colision
        self.contador_rojos = 0  # Contador de caramelos de daño consumidos (para hacer reset al pasar de nivel)
        self.contador_azules = 0  # Contador de caramelos de rango consumidos (para hacer reset al pasar de nivel)

        self.atraviesa_destructibles = False  # Indica si el jugador puede atravesar bloques destructibles (por la habilidad de la oveja común)
        self.golpes_penetrantes = False  # Indica si las bombas del jugador no se detienen al tocar muros destructibles (por la habilidad de la oveja albina)
        self.enemigos_congelados = False  # Indica si el jugador tiene enemigos congelados (por la habilidad de la oveja rosada)

        self.invulnerable = False
        self.invulnerabilidad() #Inicia invulnerable
    
    def pasar_nivel(self, nivel):
        self.rect.topleft = X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR #Reinicia la pos del jugador
        self.nivel = nivel #Cambia el nivel del jugador
        self.bombas += BOMBAS_DISPONIBLES
    
    def sacar_esquinas(self, rect):
        #Hay un offset de 1 porque hay un borde no visible de bloques solidos
        return (
            (izq := rect.left // MEDIDA_BLOQUE+1, arriba := rect.top // MEDIDA_BLOQUE+1), #Superior izquierda
            (izq, abajo := rect.bottom // MEDIDA_BLOQUE+1), #Inferior izquierda
            (der := rect.right // MEDIDA_BLOQUE+1, arriba), #Superior derecha
            (der, abajo) #Inferior derecha
        )
        
    def verificar_colision(self, rect):
        #Verifica si alguna esquina esta en un tile que no sea aire
        for x, y in self.sacar_esquinas(rect):
            if self.atraviesa_destructibles:
                if self.nivel[y][x] != 0 and self.nivel[y][x] != 2:
                    return 
            elif not self.atraviesa_destructibles:
                if self.nivel[y][x] != 0:
                    return False
        return True
    
    def verificar_en_bloque_destructible(self, rect):
        # Verifica si el jugador está en un bloque destructible
        for x, y in self.sacar_esquinas(rect):
            if self.nivel[y][x] == 2:
                return True
        return False  # Si no está en un bloque destructible, devuelve False
    
    def actualizar(self):
        keys = pg.key.get_pressed()
        dx, dy = 0, 0
        if any(self.rect.colliderect(el.rect) for el in self.jugar.lista_pegamento):  # Si el jugador colisiona con el pegamento
            velocidad = RALENTIZACION_PEGAMENTO * self.velocidad  # Reduce la velocidad del jugador al pisar el pegamento
        else:
            velocidad = self.velocidad  # Velocidad normal del jugador
        # Saca el input del usuario
        self.moviendose = False
        self.movimientos_posibles = {
            K_w: (0, -(velocidad), "arriba"),  # Arriba
            K_s: (0, velocidad, "abajo"),     # Abajo
            K_a: (-(velocidad), 0, "izquierda"), # Izquierda
            K_d: (velocidad, 0, "derecha")     # Derecha
        }

        for tecla in self.movimientos_posibles.keys():
            if keys[tecla]:
                self.moviendose = True
                tx, ty, self.direccion = self.movimientos_posibles[tecla]    
                # Se suman para que no se reemplazen en el for por 0 (en caso de movimiento diagonal)
                dx += tx
                dy += ty  
        
        # Movimiento del jugador
        # Si está dentro de los límites del mapa y camina en aire
        rect_dx, rect_dy = self.rect.move(dx, 0), self.rect.move(0, dy)
        # Verifica los ejes independientemente para mantener deslizamiento en muros con movimiento diagonal
        if self.verificar_colision(rect_dx):
            self.rect = self.rect.move(dx, 0)
        if self.verificar_colision(rect_dy):
            self.rect = self.rect.move(0, dy)
    
        # Animación
        if time.get_ticks() - self.ultima_actualizacion_frame > 150:  # Si el jugador se está moviendo y han pasado 150ms
            self.actualizar_frame_sprite()  # Actualiza el frame del sprite del jugador
            self.ultima_actualizacion_frame = time.get_ticks()  # Reinicia el tiempo de la última actualización del sprite
            self.mascara = pg.mask.from_surface(self.sprite)

        # print(self.tiene_habilidad)

    def actualizar_frame_sprite(self):
        if self.moviendose: # Jugador se mueve
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.skin_hoja_sprites) # Frame ciclico, se reinicia cuando llega al final
        else: # Jugador no se mueve
            self.frame = 0 # Reinicia
        self.sprite = self.skin_hoja_sprites[self.direccion][self.frame]


    def dibujar(self):
        if self.jugar.debug:
            # Dibuja la hitbox del jugador
            draw.rect(self.pantalla, ROJO, self.rect, 2)
            
        if self.invulnerable and time.get_ticks() % 200 < 100:
            return  # No dibujar el sprite en este frame (parpadeo)
 
        self.pantalla.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))  # Dibuja el sprite del jugador

    def poner_bomba(self):
        if self.cantidad_bombas > 0:
            bx = self.rect.centerx//MEDIDA_BLOQUE+1
            by = self.rect.centery//MEDIDA_BLOQUE+1
            for bomba in self.jugar.capas[2]: # No poner bombas encima de otras
                if (bomba.bx, bomba.by) == (bx, by):
                    return
                
            self.cantidad_bombas -= 1
            Bomba(self)

    # No-clip (Oveja común) -> Permite al jugador atravesar bloques destructibles por un tiempo limitado
    # Explosivo (Oveja albina) -> Aumenta el rango de las bombas del jugador por un tiempo limitado, además de no detenerse al contacto de un muro
    # Freeze (Oveja rosada) -> Congela a los enemigos por un tiempo limitado
    def habilidad(self):
        if self.tiene_habilidad:  # Si el jugador no tiene la habilidad especial
            self.habilidad_en_uso = True
            self.tiene_habilidad = False  # Desactiva la bandera de la habilidad especial
            if self.num_skin == 1:  # Si el jugador es de skin 1 (Oveja común)
                self.atraviesa_destructibles = True
            elif self.num_skin == 2:  # Si el jugador es de skin 2 (Oveja albina)
                self.rango += 3  # Aumenta el rango de las bombas del jugador
                self.golpes_penetrantes = True  # Las bombas del jugador no se detienen al tocar muros destructibles
            elif self.num_skin == 3:  # Si el jugador es de skin 3 (Oveja rosada)
                self.enemigos_congelados = True  # Congela a los enemigos por un tiempo limitado

            def reestablecer():
                sleep(DURACION_EFECTOS / 1000)  # Espera el tiempo de duración del efecto de la habilidad especial
                if self.num_skin == 1:  # Si el jugador es de skin 1 (Oveja común)
                    # Reduce el lag usando un sleep más largo y chequeos menos frecuentes
                    while self.verificar_en_bloque_destructible(self.rect):
                        self.atraviesa_destructibles = True
                        sleep(0.1)  # Chequea cada 100ms en vez de un bucle apretado
                    self.atraviesa_destructibles = False  # Vuelve a la normalidad al salir del bloque destructible
                elif self.num_skin == 2:  # Si el jugador es de skin 2 (Oveja albina)
                    self.rango -= 3  # Vuelve al rango normal de las bombas del jugador
                    self.golpes_penetrantes = False  # Las bombas del jugador se detienen al tocar muros destructibles00000
                elif self.num_skin == 3:  # Si el jugador es de skin 3 (Oveja rosada)
                    self.enemigos_congelados = False  # Descongela a los enemigos
                self.habilidad_en_uso = False  # Vuelve a activar la bandera de la habilidad especial
                self.tiempo_desde_habilidad = pg.time.get_ticks()  # Reinicia el tiempo desde que se usó la habilidad especial
                hilo = Thread(target=reestablecer_enfriamiento)  # Crea un hilo para administrar el enfriamiento de la habilidad
                hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
                hilo.start()  # Inicia el hilo

            def reestablecer_enfriamiento():
                sleep(self.enfriamiento_habilidad / 1000)  # Espera el tiempo de enfriamiento de la habilidad especial
                self.tiene_habilidad = True  # Vuelve a activar la bandera de la habilidad especial

            self.hilo = Thread(target=reestablecer)  # Crea un hilo para administrar el enfriamiento de la habilidad
            self.hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
            self.hilo.start()  # Inicia el hilo
        
    def item1(self):
        if self.tiene_item_1:
            self.tiene_item_1 = False  # Desactiva la bandera de la habilidad 1
            self.velocidad += 5

            def restaurar():
                sleep(DURACION_EFECTOS / 1000)  # Espera el tiempo de duración del efecto del item 1
                self.velocidad -= 5  # Vuelve a la velocidad normal

            hilo = Thread(target=restaurar)  # Se crea un hilo para restaurar la velocidad
            hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
            hilo.start()  # Inicia el hilo
    
    def item2(self):
        if self.tiene_item_2:
            self.tiene_item_2 = False  # Desactiva la bandera de la habilidad 2
            self.invulnerable = True  # Activa la invulnerabilidad

            def restaurar():
                sleep(DURACION_EFECTOS / 1000)  # Espera el tiempo de duración del efecto del item 2
                self.invulnerable = False  # Vuelve a la normalidad

            hilo = Thread(target=restaurar)  # Se crea un hilo para restaurar la velocidad
            hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
            hilo.start()  # Inicia el hilo
    
    def morir(self):
        if self.invulnerable:
            return
        if self.vidas > 1:
            self.vidas -= 1  # Cada golpe (de bomba o enemigo) resta uno de vida (hecho así para que castigue menos si la bomba tiene más daño)
            hilo = Thread(target=self.invulnerabilidad)
            hilo.daemon = True
            hilo.start()
        else:
            self.jugar.resultados = Resultados(self.jugar.game)  # Si no tiene vidas, se muestra la pantalla de Game Over
    
    def invulnerabilidad(self):
        self.invulnerable = True
        sleep(1.5)
        self.invulnerable = False
    
    def eventos(self, evento):
        if evento.type == KEYDOWN:
            if evento.key == K_SPACE: #Si le da a espacio
                self.poner_bomba()

            if evento.key == K_1: #Si le da a 1
                self.item1()
                
            elif evento.key == K_2: #O si le da a 2
                self.item2()

            elif evento.key == K_e:  # Si le da a E
                self.habilidad()  # Usa la habilidad especial del jugador

class GameOver:
    def __init__(self, pantalla):
        self.pantalla = pantalla  # Pantalla donde se dibuja la pantalla de Game Over
        self.imagen = cargar_gameover()

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla con un color
        self.pantalla.blit(self.imagen, (0, 0))  # Dibuja la pantalla de Game Over
        


class Enemigo:
    def __init__(self, jugar, x, y):
        self.jugar = jugar
        self.jugador = jugar.jugador
        self.pantalla = jugar.pantalla_juego
        self.nivel = jugar.nivel
        self.x = x
        self.y = y
        self.num_nivel = jugar.manager_niveles.num_nivel

        self.frame = 0
        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = self.num_nivel  # Número de skin del enemigo (se puede cambiar para hacerlo más complicado)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_inciales_skins_enemigos)  # Carga la skin del enemigo desde la hoja de sprites
        self.vidas = self.num_nivel # La cantidad de vida de los enemigos será igual al número de nivel
        self.velocidad = 2
        self.rect = Rect(self.x, self.y, int(MEDIDA_BLOQUE*0.75), int(MEDIDA_BLOQUE*0.75))  # Rectángulo que representa al enemigo en el canvas (uso para colisiones)
        self.movimientos = {"arriba" : (0, -self.velocidad), "abajo" : (0, self.velocidad), "izquierda" : (-self.velocidad, 0), "derecha" : (self.velocidad, 0)}  # Diccionario con los movimientos posibles
        self.movimiento_elegido = choice(list(self.movimientos.keys()))  # Elige un movimiento aleatorio del diccionario
        self.sprite = self.skin_hoja_sprites[self.movimiento_elegido][self.frame] #Sprite inicial del enemigo
        
        self.moviendose = False

    # Mueve al enemigo en una dirección aleatoria
    def actualizar(self):
        if self.jugador.enemigos_congelados:  # Si el jugador tiene enemigos congelados, no se mueve
            return
        if self.num_nivel >= 3:  # Si el nivel es 3, el enemigo suelta pegamento
            self.soltar_pegamento()
        dx, dy = self.movimientos[self.movimiento_elegido]
        # Movimiento en eje X
        rect_dx = self.rect.move(dx, 0)
        if self.verificar_colision(rect_dx):  # Si puede moverse
            self.rect = rect_dx
            self.x = self.rect.x
            self.y = self.rect.y
        else:
            self.movimiento_elegido = choice(list(self.movimientos.keys()))
            return  # Sale para que el nuevo movimiento se intente en el siguiente frame

        # Movimiento en eje Y
        rect_dy = self.rect.move(0, dy)
        if self.verificar_colision(rect_dy):  # Si puede moverse
            self.rect = rect_dy
            self.x = self.rect.x
            self.y = self.rect.y
        else:
            self.movimiento_elegido = choice(list(self.movimientos.keys()))

        self.actualizar_frame_sprite()  # Actualiza el frame del sprite del enemigo
        if not self.jugador.invulnerable and self.rect.colliderect(self.jugador.rect):
            self.jugador.morir()

    
    def verificar_colision(self, rect):
        #Hay un offset de 1 porque hay un borde no visible de bloques solidos
        esquinas = (
            (izq := rect.left // MEDIDA_BLOQUE+1, arriba := rect.top // MEDIDA_BLOQUE+1), #Superior izquierda
            (izq, abajo := rect.bottom // MEDIDA_BLOQUE+1), #Inferior izquierda
            (der := rect.right // MEDIDA_BLOQUE+1, arriba), #Superior derecha
            (der, abajo) #Inferior derecha
        )
        
        #Verifica si alguna esquina esta en un tile que no sea aire
        for x, y in esquinas:
            if self.nivel[y][x] != 0: #Si no es aire
                return False
            for bomba in self.jugar.capas[2]: #Verificar si hay una bomba
                if (x, y) == (bomba.bx, bomba.by):
                    return False
        return True
    
    def actualizar_frame_sprite(self):
        if time.get_ticks() - self.ultima_actualizacion_frame > 150:  # Si el enemigo se está moviendo y han pasado 150ms
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.skin_hoja_sprites) # Frame ciclico, se reinicia cuando llega al final
        self.sprite = self.skin_hoja_sprites[self.movimiento_elegido][self.frame]

    def soltar_pegamento(self):
        pos = (self.rect.centerx // MEDIDA_BLOQUE + 1, self.rect.centery // MEDIDA_BLOQUE + 1)
        posiciones_pegamento = [(el.bx, el.by) for el in self.jugar.lista_pegamento]
        if pos not in posiciones_pegamento:
            pegamento = Pegamento(self)  # Crea un pegamento si no hay uno en la misma posición
            self.jugar.lista_pegamento.append(pegamento)
            # print(len(self.jugar.lista_pegamento))  # Para debug, muestra la cantidad de pegamento en pantalla

    def quitar_vida(self, golpe):
        self.vidas -= golpe
        if self.vidas < 1:
            self.jugar.capas[3].remove(self)
            self.jugador.puntaje += 100
        
    
    #  Dibuja al enemigo en la pantalla
    def dibujar(self):
        self.pantalla.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))

class Jefe:
    def __init__(self, jugar, x, y):
        self.sprites = cargar_jefe()
        self.sprites_actuales = self.sprites["idle"]
        self.direccion = "izquierda"
        self.frame = 0
        self.sprite = self.sprites_actuales[self.direccion][0]
        
        for sprites in self.sprites.values():
            print(len(sprites[self.direccion]))


        self.jugar = jugar
        self.jugador = jugar.jugador
        self.pantalla = jugar.pantalla_juego
        self.nivel = jugar.nivel

        self.mascara = pg.mask.from_surface(self.sprite)
        self.rect = Rect(x*MEDIDA_BLOQUE, y*MEDIDA_BLOQUE, int(MEDIDA_BLOQUE*0.75), int(MEDIDA_BLOQUE*0.75))  # Rectángulo que representa al enemigo en el canvas (uso para colisiones)
        self.ultima_actualizacion_frame = pg.time.get_ticks()  # Tiempo de la última actualización del sprite
        
        self.vidas = 20
        self.velocidad = 1
        
        self.ultima_accion = pg.time.get_ticks()
        self.acciones = {self.moverse:"idle", self.atacar:"atacar", self.summon:"summon"}
        self.accion = self.idle
        self.proxima_accion = self.summon
        self.accion_terminada = True
        self.muriendo = False

    def quitar_vida(self, golpe):
        if self.muriendo:
            return
        self.vidas -= golpe
        if self.vidas < 1:
            self.muriendo = True
            self.accion = self.morir
            self.actualizar_sprites("morir")
            
    def morir(self):
        pass
        
    def idle(self):
        pass
    
    def summon(self):
        pass
    
    def atacar(self):
        pass
    
    def moverse(self):
        # Calcula la dirección hacia el jugador
        dx = self.jugador.rect.centerx - self.rect.centerx
        dy = self.jugador.rect.centery - self.rect.centery
        distancia = hypot(dx, dy)
        if distancia == 0:
            return  # Ya está en la misma posición

        # Normaliza el vector y multiplica por la velocidad
        dx = int(round(self.velocidad * dx / distancia))
        dy = int(round(self.velocidad * dy / distancia))

        # Movimiento en eje X
        rect_dx = self.rect.move(dx, 0)
        if self.verificar_colision(rect_dx):
            self.rect = rect_dx
            self.x = self.rect.x
            self.y = self.rect.y

        # Movimiento en eje Y
        rect_dy = self.rect.move(0, dy)
        if self.verificar_colision(rect_dy):
            self.rect = rect_dy
            self.x = self.rect.x
            self.y = self.rect.y

        self.direccion = "derecha" if dx > 0 else "izquierda"
            
    def actualizar(self):
        #self.moverse()
        ahora = pg.time.get_ticks()
        
        if self.accion_terminada:
            self.accion = choice(list(self.acciones.keys()))
            self.actualizar_sprites(self.acciones[self.accion])
            self.ultima_accion = ahora
            self.accion_terminada = False
            self.frame = 0
        

        if ahora - self.ultima_accion > 200:
            self.ultima_accion = ahora
            self.frame = (self.frame + 1) % len(self.sprites_actuales)
            self.sprite = self.sprites_actuales[self.direccion][self.frame]
            self.mascara = pg.mask.from_surface(self.sprite)
            
            # Si hemos completado un ciclo de animación
            if self.frame == 0:
                if self.muriendo:
                    self.jugar.capas[3] = [] #Mata a todos los enemigos
                    self.jugar.capas[1].append(Llave(self.jugar, self.rect.x//MEDIDA_BLOQUE+1, self.rect.y//MEDIDA_BLOQUE+1))
                self.accion_terminada = True
        

        jefe_draw_x, jefe_draw_y = self.rect.centerx - self.sprite.get_width() // 2, self.rect.centery - self.sprite.get_height() // 2
        jugador_draw_x, jugador_draw_y = self.jugador.rect.centerx - self.jugador.sprite.get_width() // 2, self.jugador.rect.centery - self.jugador.sprite.get_height() // 2

        offset = (jugador_draw_x - jefe_draw_x, jugador_draw_y - jefe_draw_y)
        if self.mascara.overlap(self.jugador.mascara, offset):
            self.jugador.morir()

    def actualizar_sprites(self, llave):
        print(llave)
        self.sprites_actuales = self.sprites[llave]
        self.current_frame = 0
        self.sprite = self.sprites_actuales[self.direccion][0]

    
    def verificar_colision(self, rect):
        #Hay un offset de 1 porque hay un borde no visible de bloques solidos
        esquinas = (
            (izq := rect.left // MEDIDA_BLOQUE+1, arriba := rect.top // MEDIDA_BLOQUE+1), #Superior izquierda
            (izq, abajo := rect.bottom // MEDIDA_BLOQUE+1), #Inferior izquierda
            (der := rect.right // MEDIDA_BLOQUE+1, arriba), #Superior derecha
            (der, abajo) #Inferior derecha
        )
        
        #Verifica si alguna esquina esta en un tile que no sea aire
        for x, y in esquinas:
            if self.nivel[y][x] != 0: #Si no es aire
                return False
            for bomba in self.jugar.capas[2]: #Verificar si hay una bomba
                if (x, y) == (bomba.bx, bomba.by):
                    return False
        return True

    def dibujar(self):
        self.pantalla.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))
        pg.draw.rect(self.pantalla, ROJO, self.rect, 2)
    

class Pegamento:  # Los enemigos más avanzados sueltan pegamento al moverse, que ralentiza al jugador
    def __init__(self, enemigo):
        self.jugar = enemigo.jugar
        self.pantalla = enemigo.pantalla
        self.bx = enemigo.rect.centerx//MEDIDA_BLOQUE+1 #Bloque en x
        self.by = enemigo.rect.centery//MEDIDA_BLOQUE+1 #Bloque en y
        self.x = (self.bx-1) * MEDIDA_BLOQUE #X en pixeles
        self.y = (self.by-1) * MEDIDA_BLOQUE #Y en pixeles
        self.rect = Rect(self.x, self.y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al pegamento en el canvas
        self.sprite = cargar_pegamento()  # Carga la skin del pegamento desde la hoja de sprites
        self.activo = True  # Indica si el pegamento está activo
        self.tiempo_creacion = pg.time.get_ticks()  # Tiempo de creación del pegamento
        self.hilo = Thread(target=self.duracion)  # Crea un hilo para actualizar el pegamento
        self.hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
        self.hilo.start()

    def actualizar(self):
        pass

    def duracion(self):
        sleep(PEGAMENTO_DURACION / 1000) 
        self.activo = False  # Desactiva el pegamento después de un tiempo
        self.jugar.lista_pegamento.remove(self)

    def dibujar(self):

        self.pantalla.blit(self.sprite, (self.x, self.y)) #Dibuja el sprite


class Bomba:
    def __init__(self, jugador):
        self.rango = jugador.rango
        self.jugar = jugador.jugar
        self.jugador = jugador
        self.pantalla = jugador.pantalla
        self.bx = jugador.rect.centerx//MEDIDA_BLOQUE+1 #Bloque en x
        self.by = jugador.rect.centery//MEDIDA_BLOQUE+1 #Bloque en y
        self.x = (self.bx-1) * MEDIDA_BLOQUE #X en pixeles
        self.y = (self.by-1) * MEDIDA_BLOQUE #Y en pixeles
        self.sprites = self.jugar.sprites_bomba
        self.golpes_penetrantes = jugador.golpes_penetrantes  # Si el jugador tiene golpes penetrantes, la bomba no se detiene al tocar muros destructibles
        
        self.tiempo_creacion = pg.time.get_ticks()
        self.ultima_actualizacion_frame = self.tiempo_creacion
        self.frame = 0
        self.sprite = self.sprites["bomba"][0]
        self.tiempo_detonar = 2000  # Tiempo en ms para que la bomba explote
        self.golpe = jugador.golpe  # Daño que causa la bomba al explotar
        self.activa = True
        self.hitbox_activa = False  # Se activa cuando el jugador se mueve fuera de la bomba
        
        self.jugar.capas[2].append(self)  # Capa de las bombas
        hilo = Thread(target=self.detonar)  # Crea un hilo para la bomba
        hilo.daemon = True
        hilo.start()

    def detonar(self):
        sleep(self.tiempo_detonar/1000)  # Pasa el tiempo a segundos
        self.activa = False #Explota
        self.jugar.nivel[self.by][self.bx] = 0  # Quita la hitbox
        Explosion(self, self.rango)
        self.jugar.capas[2].remove(self) # Ya no procesa la bomba
        self.jugador.cantidad_bombas += 1  # El contador de bombas vuelve a subir
        
    def actualizar(self):
        if not self.hitbox_activa and (self.bx,self.by) not in self.jugador.sacar_esquinas(self.jugador.rect):  # Crea la hitbox de la bomba cuando el jugador se va
            self.hitbox_activa = True
            self.jugar.nivel[self.by][self.bx] = 3  # Pone un bloque invisible
        
        # Acelera que tan rapido cambia el frame de la bomba entre menos tiempo le queda
        tiempo_actual = pg.time.get_ticks()
        intervalo_frame = max(100, (self.tiempo_detonar + self.tiempo_creacion - tiempo_actual)//5) # Cambia cada 1/5 parte del tiempo restante
        
        if tiempo_actual - self.ultima_actualizacion_frame > intervalo_frame: # Si han pasado 200 ms
            # Actualiza el frame a dibujar
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.sprites["bomba"]) # Frame ciclico, se reinicia cuando llega al final
            self.sprite = self.sprites["bomba"][self.frame] # Actualiza self.sprite
    
    def dibujar(self):
        self.pantalla.blit(self.sprite, (self.x, self.y)) #Dibuja el sprite actual

class Explosion:
    def __init__(self, bomba, rango):
        self.jugar = bomba.jugar
        self.jugador = self.jugar.jugador
        self.pantalla = bomba.pantalla
        self.bomba = bomba
        self.x = bomba.x//MEDIDA_BLOQUE+1
        self.y = bomba.y//MEDIDA_BLOQUE+1
        self.sprites = bomba.sprites
        self.nivel = self.jugar.nivel
        
        self.poder = 4
        self.rango = rango
        self.activa = True
        self.frame = 0
        self.disipador = 1 #Variable para subir los frames y devolverlos al final, dando un efecto de que se disipa la bomba
        self.jugar.capas[5].append(self) #  Agrega la explosion para ser procesada
        self.frame_expansion = len(self.sprites["centro"]) - len(self.sprites["izquierda"]) #Cuantos frames pasan del centro antes de la explosion hacia los lados
        self.ultima_actualizacion_frame = time.get_ticks()
        self.bloques_afectados, self.bloques_rotos = self.obtener_bloques_afectados()
        
    def obtener_bloques_afectados(self):
        direcciones = (0, -1), (0, 1), (-1, 0), (1, 0) #Arriba, abajo, izq, der
        bloques_afectados = [(self.x, self.y)]
        bloques_rotos = []
        for dx, dy in direcciones: #Por cada direccion
            poder_restante = self.poder
            for i in range(1, self.rango+1): #Por cada bloque en el rango
                bloque_x = self.x + dx*i
                bloque_y = self.y + dy*i
                bloque = self.nivel[bloque_y][bloque_x]
                
                if bloque == 0: #Aire
                    bloques_afectados.append((bloque_x, bloque_y)) #Explosion ocurre en ese tile
                elif bloque == 2: #Bloque rompible
                    poder_restante -= 1
                    bloques_afectados.append((bloque_x, bloque_y)) #Explosion ocurre en ese tile
                    bloques_rotos.append((bloque_x, bloque_y))
                    if poder_restante == 0:
                        break
                else:
                    break
        return bloques_afectados, bloques_rotos

    def matar(self):
        # Destruye bloques
        if self.frame == self.frame_expansion:
            for x, y in self.bloques_rotos:
                self.nivel[y][x] = 0
                self.jugador.puntaje += 50  # Aumenta el puntaje del jugador al destruir un bloque
            
        # Mata entidades
        for x, y in self.bloques_afectados:
            if not self.jugador.invulnerable and (x, y) == (self.jugador.rect.centerx//MEDIDA_BLOQUE+1, self.jugador.rect.centery//MEDIDA_BLOQUE+1): #Si el jugador no esta invulnerable
                self.jugador.morir()
                break
            for enemigo in self.jugar.capas[3]:  # Capa donde se guardan los enemigos y venenos
                if not isinstance(enemigo, Enemigo):
                    continue
                if (x, y) == (enemigo.rect.centerx//MEDIDA_BLOQUE+1, enemigo.rect.centery//MEDIDA_BLOQUE+1):
                    enemigo.quitar_vida(self.jugador.golpe)
    
    def actualizar(self):
        ahora = pg.time.get_ticks()
        if ahora - self.ultima_actualizacion_frame < 50: #Si no han pasado 50ms
            return
           
        if self.frame >= self.frame_expansion: #Ocurre la explosion, mata enemigos, el jugador y destruye bloques
            self.matar()

        self.ultima_actualizacion_frame = ahora
        self.frame += self.disipador

        if self.frame >= len(self.sprites["centro"])-1:
            self.disipador = -1
            
        elif self.frame == self.frame_expansion and self.disipador == -1:
            self.jugar.capas[5].remove(self) #En la capa 5 se guardan las explosiones, por tanto se remuve al terminar

    def dibujar(self):
        if self.frame < self.frame_expansion:
            self.pantalla.blit(self.sprites["centro"][self.frame], ((self.x-1)*MEDIDA_BLOQUE, (self.y-1)*MEDIDA_BLOQUE))
            return

        for bx, by in self.bloques_afectados:
            x = bx * MEDIDA_BLOQUE
            y = by * MEDIDA_BLOQUE

            if (bx, by) == (self.x, self.y):
                self.pantalla.blit(self.sprites["centro"][self.frame], (x-MEDIDA_BLOQUE, y-MEDIDA_BLOQUE))
                continue

            subframe = min(self.frame - 2, 2)

            #Vertial
            if bx == self.x:
                #Arriba
                if by < self.y:
                    punta = not (bx, by - 1) in self.bloques_afectados
                    llave = "punta_arriba" if punta else "arriba"
                #Abajo
                else:
                    punta = not (bx, by + 1) in self.bloques_afectados
                    llave = "punta_abajo" if punta else "abajo"
                    
            #Horizontal
            else:
                #Izquierda
                if bx < self.x:
                    punta = not (bx - 1, by) in self.bloques_afectados
                    llave = "punta_izquierda" if punta else "izquierda"
                #Derecha
                else:
                    punta = not (bx + 1, by) in self.bloques_afectados
                    llave = "punta_derecha" if punta else "derecha"

            self.pantalla.blit(self.sprites[llave][subframe], (x-MEDIDA_BLOQUE, y-MEDIDA_BLOQUE))


# ==========================================================================
#  ELEMENTOS DE INTERFAZ DE USUARIO
# ==========================================================================

# Clase para botones: necesario para los botones del menú
class Boton:
    def __init__(self, x, y, ancho, alto, texto, pantalla, color=BLANCO, color_texto=NEGRO):
        self.x = x  # Posición en el eje X
        self.y = y  # Posición en el eje Y
        self.ancho = ancho  # Ancho del botón
        self.alto = alto  # Alto del botón
        self.texto = texto  # Texto del botón
        self.pantalla = pantalla  # Pantalla donde se dibuja el botón
        self.color = color  # Color del botón (por defecto es blanco)
        self.color_texto = color_texto  # Color del texto del botón (por defecto es negro)
        self.rect = pg.Rect(self.x, self.y, self.ancho, self.alto)  # Rectángulo que representa el botón para colisiones
        self.fuente = fuente_texto
        
        # Permite que no detecta un click todo el tiempo que mantiene click si no solo uno
        self.fue_presionado = False # Pasado
        self.presionado = False  # Presente

    def detectar(self, mouse_pos, *botones):
        if self.rect.collidepoint(mouse_pos) and any(botones) and not self.presionado:
            self.presionado = True
            return True
        else:
            self.presionado = False
        return False    
        
    def dibujar(self):
        pg.draw.rect(self.pantalla, self.color, self.rect)  # Dibuja el botón en la pantalla
        pg.draw.rect(self.pantalla, NEGRO, self.rect, 2)  # Le crea un borde al botón (eso es lo que indica el 2, que es el grosor del borde)
        texto_renderizado = self.fuente.render(self.texto, True, self.color_texto)  # Renderiza el texto del botón
        self.pantalla.blit(texto_renderizado, (self.rect.x + (self.rect.width - texto_renderizado.get_width()) // 2, self.rect.y + (self.rect.height - texto_renderizado.get_height()) // 2))  # Dibuja el texto centrado en el botón

    def detectar_presionado(self, mouse_pos, *presses):
        ahora_presionado = any(presses) # Si presiono cualquier boton valido
        self.presionado = self.rect.collidepoint(mouse_pos) and ahora_presionado # self.presionado = mouse encima del boton y lo presiona
        presionado = self.presionado and not self.fue_presionado # Si acaba de presionar (no solo esta manteniendo click)
        self.fue_presionado = self.presionado #Actualiza fue_presionado
        return presionado

# Clase para la caja de entrada de texto: necesario para el nombre del usuario y la dirección
class InputBox:
    def __init__(self, pantalla, x, y, max_ancho:float=500, color_fuente=NEGRO, color_fondo=BLANCO,):
            self.pantalla = pantalla
            self.x = x
            self.y = y
            self.fuente = fuente_texto
            self.color_fuente = color_fuente
            self.color_fondo = color_fondo
            self.max_ancho = max_ancho
            self.color_activo = VERDE_AGUA
            self.color_pasivo = GRIS
            self.caracteres_validos = "012345789AaBbCcDdEeFfGgHhIiJjKkLlMmNnÑñOoPpQqRrSsTtUuVvWwXxYyZz "
            self.texto = ""
            self.altura = self.fuente.get_height()
            self.rect = pg.Rect(x, y, max_ancho, self.altura*1.1) # La barra es un poco más grande que el texto que recibe
            self.activa = False
            
    def escribir(self, evento, mouse_pos, click_izq):
        pasar_encima = self.rect.collidepoint(mouse_pos)
        if pasar_encima and click_izq:  # Si se le pasa por encima a la barra y se le hace click
            self.activa = True  # La barra se activa
        elif click_izq and not pasar_encima and self.activa == True:  # Si se hace click fuera de la barra y la barra está activa
            self.activa = None  # Si se hace click fuera de la barra, se desactiva
        
        if self.activa:  # Si la caja de entrada está activa
            if evento.type == pg.KEYDOWN: # Si se presiona una tecla
                if evento.key == pg.K_BACKSPACE and len(self.texto) >= 1: # Si se presiona la tecla de retroceso y hay texto
                    self.texto = self.texto[:-1] # Elimina el último carácter del texto
                else:
                    letra = evento.unicode  
                    if letra in self.caracteres_validos:  # Si la letra es válida
                        ancho_letra = self.fuente.size(self.texto + letra)[0]
                        if ancho_letra < self.max_ancho:  # Si el ancho del texto con la nueva letra es menor que el máximo
                            self.texto += letra  # Agrega la letra al texto
        return False  # Caso en donde no es escribe un caracter válido

    def dibujar(self):
        pg.draw.rect(self.pantalla, self.color_fondo, self.rect)  # Dibuja el fondo de la caja de entrada
        self.texto_render = self.fuente.render(self.texto, True, self.color_fuente)  # Renderiza el texto de la caja de entrada
        self.pantalla.blit(self.texto_render, (self.x + self.max_ancho//2 - self.texto_render.get_width()//2, self.y))  # Dibuja el texto en la caja de entrada 
        if not self.activa:  # Si la caja de entrada no está activa, dibuja un borde pasivo
            pg.draw.rect(self.pantalla, self.color_pasivo, self.rect, width=1)  # Pone frame pasivo
        else:
            pg.draw.rect(self.pantalla, self.color_activo, self.rect, width=1)  # Pone frame activo

class Deslizante:
    def __init__(self, pantalla, x, y, ancho, alto, parametro, min_parametro=0, max_parametro=1, radio_control=10):
        self.pantalla = pantalla
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.parametro = parametro #Valor a cambiar cuando se desliza la barra
        self.min_parametro = min_parametro #Minimo valor que puede tomar
        self.max_parametro = max_parametro #Maximo valor que puede tomar
        self.radio = radio_control
        
        self.x_control = self.x + int(self.ancho * self.parametro)  # Posición del control en x
        self.deslizando = False #Indica si se esta deslizando la barra
        
    def eventos(self, evento):
        mouse_pos = pg.mouse.get_pos()
        if evento.type == pg.MOUSEBUTTONDOWN:
            if abs(mouse_pos[0] - self.x_control) <= self.radio and abs(mouse_pos[1] - (self.y) + self.alto // 2) <= self.radio:  # Si el cursor está cerca del control deslizante
                self.deslizando = True  # Indica que se está arrastrando el control de la barra
            
        elif evento.type == pg.MOUSEBUTTONUP:
            self.deslizando = False #Suelta el deslizante
            
    def actualizar(self):
        if self.deslizando:  # Si se está arrastrando la barra de sonido
            self.x_control = self.x + int(self.ancho * self.parametro)  # Posición del control en x
            self.parametro = max(0, min(1, (pg.mouse.get_pos()[0] - self.x) / self.ancho))  # Calcula el nuevo valor del parametro según la posición del mouse
    
    def dibujar(self):
        pg.draw.rect(self.pantalla, GRIS, (self.x, self.y, self.ancho, self.alto))  # Dibuja el fondo de la barra
        pg.draw.rect(self.pantalla, VERDE, (self.x, self.y, self.ancho * self.parametro, self.alto))
        pg.draw.circle(self.pantalla, BLANCO, (self.x_control, self.y + self.alto // 2), self.radio)  # Dibuja el control deslizante en la barra de sonido

class BarraVida:
    def __init__(self, x, y, ancho, alto, jugar):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.jugar = jugar  # Instancia del juego donde se dibuja la barra de vida
        self.pantalla = jugar.pantalla
        self.jugador = self.jugar.jugador
        self.vida = self.jugador.vidas  # Vida actual del jugador
        self.vida_maxima = self.jugador.vidas_max  # Vida máxima del jugador
        self.ratio = self.vida / self.vida_maxima  # Calcula el ratio de vida actual sobre la máxima

    def actualizar(self):
        self.vida_maxima = self.jugador.vidas_max
        self.vida = self.jugador.vidas  # Actualiza la vida actual del jugador
        self.ratio = self.vida / self.vida_maxima  # Calcula el ratio de vida actual sobre la máxima

    def dibujar(self):
        pg.draw.rect(self.pantalla, ROJO, (self.x, self.y, self.ancho, self.alto))  # Dibuja el fondo de la barra de vida
        pg.draw.rect(self.pantalla, VERDE, (self.x, self.y, self.ancho * self.ratio, self.alto))  # Dibuja la barra de vida actual del jugador

# Clase HUD (Head-Up Display) que muestra información del juego en la pantalla
class HUD:
    def __init__(self, jugar):
        self.jugar = jugar
        self.pantalla = jugar.pantalla  # Pantalla donde se dibuja el HUD
        self.jugador = jugar.jugador  # Jugador del juego
        self.num_skin = self.jugador.num_skin  # Número de skin del jugador
        self.fuente = fuente_texto  # Fuente del texto del HUD
        self.texto_vidas = self.fuente.render("Vida", True, BLANCO)
        self.barra_vida = BarraVida(SEPARACION_BORDES_PANTALLA + self.texto_vidas.get_width() + 10, 20, 200, 20, jugar)  # Barra de vida del jugador
        self.textos = []  # Lista para almacenar los textos del HUD
        self.iconos_habilidades = cargar_habilidades()  # Carga los iconos de las habilidades del jugador
        self.cargar_sprites_en_proporcion()  # Carga los sprites de los items del jugador en proporción

    def cargar_sprites_en_proporcion(self):
        self.pociones = cargar_pociones()  # Carga los sprites de las pociones
        self.llave = cargar_llave()  # Carga el sprite de la llave
        self.llave = pg.transform.scale(self.llave, (96, 96))
        for llave in self.pociones.keys():
            # Escala los sprites de las pociones a 96x96 píxeles
            self.pociones[llave] = pg.transform.scale(self.pociones[llave], (96, 96))
        self.sprites = [self.pociones["velocidad"], self.pociones["invulnerabilidad"], self.llave]  # Lista con los sprites de los items (de esta forma para ordenarlos en el HUD)

    def actualizar_textos(self):
        # Actualiza el puntaje del jugador en el HUD
        self.textos = [
        self.fuente.render(f"Bombas: {self.jugador.cantidad_bombas}", True, BLANCO),  # Texto de las bombas del jugador
        self.fuente.render(f"Rango: {self.jugador.rango}", True, BLANCO),  # Texto del rango de las bombas del jugador
        self.fuente.render(f"Puntaje: {self.jugador.puntaje}", True, BLANCO),  # Texto del puntaje del jugador
        self.fuente.render(f"Daño: {self.jugador.golpe}", True, BLANCO)  # Texto de las vidas del jugador
        ]

    def actualizar(self):
        self.barra_vida.actualizar()  # Actualiza la barra de vida del jugador
        self.actualizar_textos()
        # Actualiza el HUD con la información del jugador

    def dibujar(self):
        self.pantalla.blit(self.texto_vidas, (SEPARACION_BORDES_PANTALLA, 10))  # Dibuja el texto de "Vida" en la pantalla
        for i, texto in enumerate(self.textos):  # Dibuja cada texto del HUD (consiguendo el índice y el elemento con enumerate)
            self.pantalla.blit(texto, (SEPARACION_BORDES_PANTALLA, 40 + i * 30))
        self.barra_vida.dibujar()  # Dibuja la barra de vida del jugador

        # Cuadros de 96x96 para los items del jugador
        condiciones = [self.jugador.tiene_item_1, self.jugador.tiene_item_2, self.jugador.tiene_llave]  # Lista de condiciones para los items del jugador
        for i in range(len(condiciones)):
            if condiciones[i]:
                # Si el jugador tiene el item, dibuja el sprite correspondiente
                self.pantalla.blit(self.sprites[i], (SEPARACION_BORDES_PANTALLA + 300 + i * 112, 40))
            pg.draw.rect(self.pantalla, BLANCO, (SEPARACION_BORDES_PANTALLA + 300 + i * 112, 40, 96, 96), 4)  # Dibuja los cuadros de los items del jugador
        
        pg.draw.rect(self.pantalla, ROJO, (SEPARACION_BORDES_PANTALLA + 300 + 3 * 112, 40, 96, 96))  # Dibuja el cuadro del la habilidad del jugador
        # Dibuja un cuadro que se rellenará con en base al CD de la habilidad del jugador (de abajo hacia arriba)
        if self.jugador.tiene_habilidad:  # Si el jugador tiene la habilidad especial
            pg.draw.rect(self.pantalla, VERDE, (SEPARACION_BORDES_PANTALLA + 300 + 3 * 112, 40, 96, 96))  # Dibuja el borde del cuadro del item de velocidad
        elif self.jugador.habilidad_en_uso:  # Si el jugador está usando la habilidad especial
            pg.draw.rect(self.pantalla, AZUL, (SEPARACION_BORDES_PANTALLA + 300 + 3 * 112, 40, 96, 96))  # Dibuja el borde del cuadro del item de velocidad
        else:
            ratio = (pg.time.get_ticks() - self.jugador.tiempo_desde_habilidad) / self.jugador.enfriamiento_habilidad  # Calcula el ratio de la habilidad del jugador (para que no se vea vacío si no tiene habilidad)
            # Calcula la altura del rectángulo verde según el ratio
            altura = int(96 * ratio)
            y_base = 136 - altura  # La base es 136, restamos la altura para que crezca hacia arriba
            pg.draw.rect(self.pantalla, VERDE, (SEPARACION_BORDES_PANTALLA + 300 + 3 * 112, y_base, 96, altura))
        
        # Dibuja los íconos de las habilidades
        self.pantalla.blit(self.iconos_habilidades[self.num_skin], (SEPARACION_BORDES_PANTALLA + 300 + 3 * 112, 40))

        # Dibuja el marco de la habilidad del jugador
        pg.draw.rect(self.pantalla, BLANCO, (SEPARACION_BORDES_PANTALLA + 300 + 3 * 112, 40, 96, 96), 4)  # Dibuja los cuadros de los items del jugador

# ==========================================================================
#  CONSUMIBLES DEL JUEGO + PUERTA Y LLAVE
# ==========================================================================

# Función para cargar la llave, es especial, porque es un objeto que se encuentra dentro de un bloque aleatorio del nivel, y aparece al romperlo
class Llave:
    def __init__(self, jugar, x, y):
        self.x_bloque = x  # Posición en el eje X del bloque donde se encuentra la llave
        self.y_bloque = y  # Posición en el eje Y del bloque donde se encuentra la llave
        self.jugar = jugar
        self.nivel = self.jugar.nivel  # Nivel donde se encuentra la llave (se usa para verificar colisiones)
        self.jugador = self.jugar.jugador  # Jugador que recogerá la llave
        self.pantalla = self.jugar.pantalla_juego  # Pantalla donde se dibuja la llave
        self.sprite = cargar_llave()  # Carga el sprite de la llave desde la hoja de sprites
        self.rect = Rect((self.x_bloque - 1)* MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa la llave en el canvas (uso para colisiones)
        self.bloque_roto = False  # Indica si el bloque donde se encuentra la llave ha sido roto

    def actualizar(self):
        if self.nivel[self.y_bloque][self.x_bloque] == 0:
            self.bloque_roto = True
        if self.rect.colliderect(self.jugador.rect) and not self.jugador.atraviesa_destructibles:  # Si el jugador colisiona con la llave y no puede atravesar destructibles
            self.jugador.tiene_llave = True
            self.jugar.capas[1].remove(self)  # Elimina la llave de la capa de objetos

    def dibujar(self):
        if self.bloque_roto and not self.jugador.tiene_llave:
            self.pantalla.blit(self.sprite, self.rect)  # Dibuja el sprite de la llave en la pantalla

class Puerta:
    def __init__(self, jugar, y):
        self.jugar = jugar
        self.x_bloque = ANCHO_MATRIZ  # La puerta se encuentra en el borde derecho del nivel
        self.y_bloque = y
        self.nivel = jugar.nivel  # Nivel donde se encuentra la puerta (se usa para verificar colisiones)
        self.jugador = jugar.jugador  # Jugador que abrirá la puerta
        self.pantalla = jugar.pantalla_juego  # Pantalla donde se dibuja la puerta
        self.sprite = cargar_puerta()  # Carga el sprite de la puerta desde la hoja de sprites
        self.rect = Rect((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa la puerta en el canvas (uso para colisiones)

    def actualizar(self):
        if self.rect.colliderect(self.jugador.rect) and self.jugador.tiene_llave:
            self.jugador.tiene_llave = False
            for _ in range(self.jugador.contador_rojos):
                self.jugador.golpe -= 1
            for _ in range(self.jugador.contador_azules):
                self.jugador.rango -= 1
            # Reinicio de los contadores de caramelos
            self.jugador.contador_rojos = 0
            self.jugador.contador_azules = 0
            self.jugador.puntaje_total += self.jugar.jugador.puntaje  # Suma el puntaje del jugador al puntaje total
            self.jugar.mejoras = Mejoras(self.jugar)  # Si el jugador colisiona con la puerta y tiene la llave, se abre el menú de mejoras
            self.jugar.menu_mejoras()

    def dibujar(self):
        self.pantalla.blit(self.sprite, ((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE))

class Pociones:  # Las pociones son un objeto que se encuentra en el nivel, y al recogerlos y usarlos, el jugador gana habilidades especiales temporalmente - ITEMS
    # Estos, al igual que la llave, se encuentran dentro de un bloque aleatorio del nivel, y aparecen al romperlo
    def __init__(self, jugar, x, y):
        self.x_bloque = x
        self.y_bloque = y
        self.jugar = jugar
        self.nivel = self.jugar.nivel  # Nivel donde se encuentra la poción (se usa para verificar colisiones)
        self.jugador = self.jugar.jugador  # Jugador que recogerá la poción
        self.pantalla = self.jugar.pantalla_juego  # Pantalla donde se dibuja la poción
        self.tipo = choice(["velocidad", "invulnerabilidad"])  # Tipo de poción (velocidad o invulnerabilidad)
        self.sprite = cargar_pociones()[self.tipo]  # Carga el sprite de la poción desde la hoja de sprites
        self.rect = Rect((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
        self.bloque_roto = False  # Indica si el bloque donde se encuentra la poción ha sido roto

    def actualizar(self):
        if self.nivel[self.y_bloque][self.x_bloque] == 0:  # Si el bloque donde se encuentra la poción ha sido roto
            self.bloque_roto = True
        if self.rect.colliderect(self.jugador.rect) and not self.jugador.atraviesa_destructibles:  # Si el jugador colisiona con la poción
            if self.tipo == "velocidad" and not self.jugador.tiene_item_1:
                self.jugador.tiene_item_1 = True  # Hace que el jugador pueda usar la habilidad de velocidad (1)
                self.jugar.capas[1].remove(self)  # Elimina el caramelo de la capa de objetos
            elif self.tipo == "invulnerabilidad" and not self.jugador.tiene_item_2:
                self.jugador.tiene_item_2 = True  # Hace que el jugador pueda usar la habilidad de invulnerabilidad (2)
                self.jugar.capas[1].remove(self)  # Elimina la poción de la capa de objetos

    def dibujar(self):
        if self.bloque_roto:
            self.pantalla.blit(self.sprite, ((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE))  # Dibuja el sprite de la poción en la pantalla

class Caramelos:  # Los caramelos son un objeto que se encuentra en el nivel, y al recogerlos, el jugador gana estadísticas (daño, rango, vida) -> POWER-UPS
    # Estos, al igual que la llave, se encuentran dentro de un bloque aleatorio del nivel, y aparecen al romperlo
    def __init__(self, jugar, x, y):
        self.x_bloque = x
        self.y_bloque = y
        self.jugar = jugar
        self.nivel = self.jugar.nivel  # Nivel donde se encuentra el caramelo (se usa para verificar colisiones)
        self.jugador = self.jugar.jugador  # Jugador que recogerá el caramelo
        self.pantalla = self.jugar.pantalla_juego  # Pantalla donde se dibuja el caramelo
        self.tipo = choice(["daño", "rango", "vida"])  # Tipo de caramelo (vida, rango o daño)
        self.sprite = cargar_caramelos()[self.tipo]  # Carga el sprite del caramelo desde la hoja de sprites
        self.rect = Rect((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
        self.bloque_roto = False  # Indica si el bloque donde se encuentra el caramelo ha sido roto

    def actualizar(self):
        if self.nivel[self.y_bloque][self.x_bloque] == 0:  # Si el bloque donde se encuentra el caramelo ha sido roto
            self.bloque_roto = True
        if self.rect.colliderect(self.jugador.rect) and not self.jugador.atraviesa_destructibles:  # Si el jugador colisiona con el caramelo
            if self.tipo == "daño":
                self.jugar.capas[1].remove(self)  # Elimina el caramelo de la capa de objetos
                self.jugador.golpe += 1  # Aumenta el daño del jugador
                self.jugador.contador_rojos += 1  # Aumenta el contador de caramelos rojos del jugador
            elif self.tipo == "rango":
                self.jugar.capas[1].remove(self)  # Elimina el caramelo de la capa de objetos
                self.jugador.rango += 1  # Aumenta el rango de la bomba del jugador
                self.jugador.contador_azules += 1  # Aumenta el contador de caramelos azules del jugador
            elif self.tipo == "vida" and self.jugador.vidas < self.jugador.vidas_max:  # Si el jugador tiene menos vidas que las máximas
                self.jugador.vidas += 1  # Aumenta la vida del jugador
                self.jugar.capas[1].remove(self)  # Elimina el caramelo de la capa de objetos

    def dibujar(self):
        if self.bloque_roto:
            self.pantalla.blit(self.sprite, ((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE))  # Dibuja el sprite del caramelo en la pantalla

# ==========================================================================
#  PESTAÑAS DENTRO Y FUERA DEL MENU
# ==========================================================================

# Clase Ajustes: aquí se pueden agregar las configuraciones del juego, como el volumen
class Ajustes:
    def __init__(self, menu):
        self.menu = menu
        self.game = menu.game
        self.pantalla = menu.pantalla  # Pantalla donde se dibuja la información
        self.musica = menu.game.canciones[0]
        self.boton_cerrar = Boton(ANCHO_PANTALLA - 70, 20, 50, 50, "X", self.pantalla, ROJO, BLANCO)  # Botón para volver al menu desde alguna opcion
        self.fuente = fuente_texto  # Fuente del texto de la información
        self.barra_sonido = Deslizante(self.pantalla, ANCHO_PANTALLA//2 - 200, SEPARACION_BORDES_PANTALLA*9, 400, 10, self.game.volumen)

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        
        self.texto_renderizado = self.fuente.render("Ajustes", True, BLANCO)  # Renderiza el texto de los ajustes
        self.texto_musica_renderizado = self.fuente.render("Volumen de la música", True, BLANCO)  # Renderiza el texto del volumen de la música
        
        self.pantalla.blit(self.texto_renderizado, (ANCHO_PANTALLA // 2 - self.texto_renderizado.get_width() // 2, 30))  # Dibuja el texto centrado en la pantalla
        self.pantalla.blit(self.texto_musica_renderizado, (SEPARACION_BORDES_PANTALLA * 4, SEPARACION_BORDES_PANTALLA * 8))
        
        self.barra_sonido.dibujar()
        self.boton_cerrar.dibujar()  # Dibuja el botón de cerrar la pantalla
        
    def eventos(self, evento):
        mouse_pos = pg.mouse.get_pos()
        
        self.barra_sonido.eventos(evento)
        
        if self.boton_cerrar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            self.menu.game.cambiar_modo(self.menu)
    
    def actualizar(self):
        self.barra_sonido.actualizar()
        if self.barra_sonido.deslizando: # Si se está deslizando la barra de sonido
            self.game.volumen = self.barra_sonido.parametro #Cambia el volumen en todo el juego
            self.musica.set_volume(self.game.volumen)  # Establece el volumen de la música

class Informacion:
    def __init__(self, menu):
        self.menu = menu
        self.pantalla = menu.pantalla  # Pantalla donde se dibuja la información
        self.musica = menu.game.canciones[0]
        self.boton_cerrar = Boton(ANCHO_PANTALLA - 70, 20, 50, 50, "X", self.pantalla, ROJO, BLANCO)  # Botón para volver al menu desde alguna opcion
        
        self.texto = "Información del juego"  # Texto de la información del juego
        self.fuente = fuente_texto  # Fuente del texto de la información
        self.foto_juan = pg.image.load("assets/carnets/JuanFoto.png").convert_alpha()  # Carga la imagen de Juan
        self.foto_pablo = pg.image.load("assets/carnets/PabloFoto.jpg").convert_alpha()  # Carga la imagen de Pablo
        self.foto_juan = pg.transform.scale(self.foto_juan, (150, 150))  # Reescala la imagen de Juan a 150x150 píxeles
        self.foto_pablo = pg.transform.scale(self.foto_pablo, (150, 150))  # Reescala la imagen de Pablo a 150x150 píxeles
        
        self.lineas = dividir_texto(TEXTO_INFO)

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        
        y = 50
        for linea in self.lineas:
            render = self.fuente.render(linea, True, BLANCO)
            x = (ANCHO_PANTALLA - render.get_width()) // 2  # Centra el texto en la pantalla
            self.pantalla.blit(render, (x, y))
            y += self.fuente.get_height() + 5
        self.boton_cerrar.dibujar()  # Dibuja el botón de cerrar la información
        
        self.pantalla.blit(self.foto_juan, (ANCHO_PANTALLA // 2 - self.foto_juan.get_width() - 20, ALTO_PANTALLA // 2 + self.foto_juan.get_height() // 2))  # Dibuja la foto de Juan
        self.pantalla.blit(self.foto_pablo, (ANCHO_PANTALLA // 2 + 20, ALTO_PANTALLA // 2 + self.foto_pablo.get_height() // 2))  # Dibuja la foto de Pablo B)
        
    def actualizar(self):  # Realmente no necesita actualizar nada, pero es necesario para el ciclo del juego
        pass
    
    def eventos(self, evento):
        mouse_pos = pg.mouse.get_pos()
        if self.boton_cerrar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            self.menu.game.cambiar_modo(self.menu)

class Puntajes:
    def __init__(self, menu):
        self.menu = menu
        self.pantalla = menu.pantalla  # Pantalla donde se dibuja la información
        self.musica = menu.game.canciones[0]
        self.boton_cerrar = Boton(ANCHO_PANTALLA - 70, 20, 50, 50, "X", self.pantalla, ROJO, BLANCO)  # Botón para volver al menu desde alguna opcion
        self.fuente = fuente_texto  # Fuente del texto de los puntajes
        self.mensaje = "No hay puntajes aún"  # Mensaje que se muestra si no hay puntajes
        self.ordenar_puntajes()  # Carga los puntajes desde el archivo

    def ordenar_puntajes(self):
        self.top = []  # Lista para almacenar los puntajes
        self.top_render = []  # Lista para almacenar los puntajes renderizados
        self.cantidad_mostrada = min(5, len(puntajes))  # Cantidad de puntajes a mostrar (máximo 5)
        for i in range(self.cantidad_mostrada):  # Almacena los mejores 5 puntajes
            if puntajes != []:
                self.top.append((i + 1, puntajes[i]))  # Agrega el puntaje y su posición a la lista de puntajes
            else:
                break
        
        for top_puntajes in self.top:
            self.top_render.append(self.fuente.render(f"{top_puntajes[0]}. {top_puntajes[1][0]} - {top_puntajes[1][1]}", True, AMARILLO if top_puntajes[0] == 1 else BLANCO))  # Agrega el texto renderizado a la lista de puntajes renderizados


    def actualizar(self):
        self.ordenar_puntajes()  # Vuelve a ordenar los puntajes cada vez que se actualiza

    def eventos(self, evento):
        mouse_pos = pg.mouse.get_pos()
        if self.boton_cerrar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            self.menu.game.cambiar_modo(self.menu)

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        self.texto_renderizado = self.fuente.render("Mejores 5 puntajes", True, BLANCO)  # Renderiza el texto de los ajustes
        self.pantalla.blit(self.texto_renderizado, (ANCHO_PANTALLA // 2 - self.texto_renderizado.get_width() // 2, 30))  # Dibuja el texto centrado en la pantalla

        self.boton_cerrar.dibujar()
        if self.top != []:
            for i, texto in enumerate(self.top_render):
                self.pantalla.blit(texto, (ANCHO_PANTALLA//2 - texto.get_width()//2, ALTO_PANTALLA//3 + self.fuente.get_height() * i))
        else:
            self.mensaje_renderizado = self.fuente.render(self.mensaje, True, BLANCO)
            self.pantalla.blit(self.mensaje_renderizado, (ANCHO_PANTALLA//2 - self.mensaje_renderizado.get_width()//2, ALTO_PANTALLA//2))

class Personalizacion:
    def __init__(self, menu):
        self.menu = menu
        self.pantalla = menu.pantalla  # Pantalla donde se dibujan los aspectos de personalización
        self.boton_cerrar = Boton(ANCHO_PANTALLA - 70, 20, 50, 50, "X", self.pantalla, ROJO, BLANCO)  # Botón para volver al menu desde alguna opcion
        self.boton_confirmar = Boton(ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA - 150, 200, 50, "Confirmar", self.pantalla, VERDE, BLANCO)  # Botón para confirmar la personalización
        self.musica = menu.game.canciones[0]
        self.cambiar_modo = menu.game.cambiar_modo(self)  # Método para cambiar el modo del juego

        self.fuente = fuente_texto  # Fuente del texto de la información
        self.num_skin = 1  # Número del skin actual (1 por defecto)

        self.texto_renderizado = self.fuente.render("Esta es la leyenda de:", True, BLANCO)  # Renderiza el texto de los ajustes
        self.inputbox = InputBox(self.pantalla, ANCHO_PANTALLA // 2 - 250, 90)

        self.imagenes_skins = cargar_skins(self.num_skin, puntos_iniciales_skins_jugador)  # Carga las imágenes de los skins desde la carpeta de personajes
        self.imagen_mostrada = self.imagenes_skins["derecha"][0]  # Imagen que se muestra en la pantalla (por defecto es la imagen de la derecha del skin 1)
        self.imagen_mostrada = pg.transform.scale(self.imagen_mostrada, (128, 128))  # Escala la imagen
        self.lineas = dividir_texto(INFORMACION_PERSONAJES, self.num_skin)  # Divide el texto de información del personaje en líneas para que se ajuste a la pantalla

    def cambio_de_skin(self, accion):
        self.num_skin += accion
        if self.num_skin == 4:  # Si se sale del rango de skins desde la 3era skin, vuelve a la 1era skin
            self.num_skin = 1
        elif self.num_skin == 0:  # Si se sale del rango de skins desde la 1era skin, vuelve a la 3era skin
            self.num_skin = 3

    def reinciar(self):  # Reinicia la personalización al skin 1 y limpia la caja de entrada de texto
        self.num_skin = 1
        self.inputbox.texto = ""  # Limpia la caja de entrada de texto

    def actualizar(self):  # Actualiza la información del personaje según el skin seleccionado
        self.imagenes_skins = cargar_skins(self.num_skin, puntos_iniciales_skins_jugador)  # Carga las imágenes de los skins desde la carpeta de personajes
        self.imagen_mostrada = self.imagenes_skins["derecha"][0]  # Imagen que se muestra en la pantalla (por defecto es la imagen de la derecha del skin 1)
        self.imagen_mostrada = pg.transform.scale(self.imagen_mostrada, (128, 128))  # Escala la imagen
        self.lineas = dividir_texto(INFORMACION_PERSONAJES, self.num_skin)  # Divide el texto de información del personaje en líneas para que se ajuste a la pantalla
        # print(self.num_skin)

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        self.pantalla.blit(self.texto_renderizado, (ANCHO_PANTALLA // 2 - self.texto_renderizado.get_width() // 2, 30))  # Dibuja el texto centrado en la pantalla
        self.inputbox.dibujar()

        self.pantalla.blit(self.imagen_mostrada, (ANCHO_PANTALLA//2 - self.imagen_mostrada.get_width()//2 , ALTO_PANTALLA//2 - self.imagen_mostrada.get_height()//2))

        # Impresión del texto
        y = ALTO_PANTALLA//2 + self.imagen_mostrada.get_height()//2 + 32  # 32 es el espacio de separación entre el sprite y el texto
        for linea in self.lineas:
            render = self.fuente.render(linea, True, BLANCO)
            x = (ANCHO_PANTALLA - render.get_width()) // 2  # Centra el texto en la pantalla
            self.pantalla.blit(render, (x, y))
            y += self.fuente.get_height() + 5
        self.boton_cerrar.dibujar()  # Dibuja el botón de cerrar
        self.boton_confirmar.dibujar()  # Dibujar el botón de confirmar la personalización


    def eventos(self, evento):
        self.inputbox.escribir(evento, pg.mouse.get_pos(), pg.mouse.get_pressed()[0])  # Escribe en la caja de entrada de texto
        mouse_pos = pg.mouse.get_pos()
        if self.boton_cerrar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            self.menu.game.cambiar_modo(self.menu)
        if self.boton_confirmar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            if self.inputbox.texto != "":  # Si se ha escrito algo en la caja de entrada
                self.menu.game.nombre_jugador = self.inputbox.texto  # Asigna el nombre del jugador al texto escrito en la caja de entrada
            else:
                self.menu.game.nombre_jugador = "Jugador"  # Si no se ha escrito nada, asigna un nombre por defecto al jugador
            self.menu.jugar = Jugar(self.menu.game, self.num_skin)  # Crea un nuevo juego con el skin seleccionado
            self.menu.game.cambiar_modo(self.menu.jugar)  # Cambia el modo del juego al menú principal
            self.reinciar()  # Reinicia la personalización al skin 1 y limpia la caja de entrada de texto

        if evento.type == KEYDOWN:
            if evento.key == K_RIGHT:
                self.cambio_de_skin(+1)
            elif evento.key == K_LEFT:
                self.cambio_de_skin(-1)

class Mejoras:
    def __init__(self, jugar):
        self.jugar = jugar
        self.jugador = jugar.jugador
        self.pantalla = jugar.pantalla
        self.dibujar_texto = jugar.dibujar_texto
        
        self.puntos = self.jugador.puntaje
        self.precio_vida = 100
        self.precio_golpe = 100
        self.precio_rango = 100
        
        self.crear_botones()
    
    def crear_botones(self):
        self.boton_vida = Boton(100, 100, 200, 75, f"VIDA {self.precio_vida}", self.pantalla, VERDE)
        self.boton_golpe = Boton(100, 300, 200, 75, f"GOLPE {self.precio_golpe}", self.pantalla, ROJO)
        self.boton_rango = Boton(100, 500, 200, 75, f"RANGO {self.precio_rango}", self.pantalla, AZUL)
        self.pasar_nivel = Boton(1000, 650, 200, 50, "PASAR NIVEL", self.pantalla, GRIS)
    
    def dibujar(self):
        self.pantalla.fill(VERDE_AGUA)
        
        self.dibujar_texto("PRECIOS", 100, 50)
        self.dibujar_texto(f"PUNTOS: {self.puntos}", 100, 650)
        self.dibujar_texto(f"VIDAS MÁX: {self.jugador.vidas}", 400, 100 + self.boton_vida.alto // 4)
        self.dibujar_texto(f"GOLPE: {self.jugador.golpe}", 400, 300 + self.boton_golpe.alto // 4)
        self.dibujar_texto(f"RANGO: {self.jugador.rango}", 400, 500 + self.boton_rango.alto // 4)
        
        self.boton_vida.dibujar()
        self.boton_golpe.dibujar()
        self.boton_rango.dibujar()
        self.pasar_nivel.dibujar()
       
    def actualizar(self):  # No es necesario actualizar nada en este caso, pero se deja para mantener la estructura
        pass

    def eventos(self, evento):  # Maneja los eventos de los botones (no se necesita evento porque no se tocan las teclas)
        mouse_pos = pg.mouse.get_pos()
        click_izq = pg.mouse.get_pressed()[0] #Click izquierdo
            
        if self.boton_vida.detectar_presionado(mouse_pos, click_izq) and self.puntos >= self.precio_vida:
            self.puntos -= self.precio_vida
            self.precio_vida += 200 #  Incrementa el precio linearmente 200 cada vez
            self.jugador.vidas += 1
            self.jugador.vidas_max += 1 #  Aumenta la vida maxima del jugador
            self.boton_vida.texto = f"VIDA {self.precio_vida}"
                
        elif self.boton_golpe.detectar_presionado(mouse_pos, click_izq) and self.puntos >= self.precio_golpe:
            self.puntos -= self.precio_golpe
            self.precio_golpe += 200 #  Incrementa el precio linearmente 200 cada vez
            self.jugador.golpe += 1
            self.boton_golpe.texto = f"GOLPE {self.precio_golpe}"
                
        elif self.boton_rango.detectar_presionado(mouse_pos, click_izq) and self.puntos >= self.precio_rango:
            self.puntos -= self.precio_rango
            self.precio_rango += 500 #  Incrementa el precio linearmente 500 cada vez
            self.jugador.rango += 1
            self.boton_rango.texto = f"RANGO {self.precio_rango}"
                
        elif self.pasar_nivel.detectar_presionado(mouse_pos, click_izq):
            self.jugar.cambiar_modo(self.jugar)
            self.jugar.pasar_nivel()
            self.jugador.puntaje = self.puntos

class Resultados:
    def __init__(self, game):
        self.game = game  # Acceso al menú del juego
        self.pantalla = self.game.pantalla
        self.musica = self.game.canciones[2]
        self.boton_confirmar = Boton(ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA - 150, 200, 50, "Confirmar", self.pantalla, VERDE, BLANCO)  # Botón para confirmar la personalización
        self.cambiar_modo = self.game.cambiar_modo(self)  # Método para cambiar el modo del juego
        self.fuente = fuente_texto  # Fuente del texto de la información

        self.texto = "Resultados"
        self.texto_renderizado = self.fuente.render(self.texto, True, BLANCO)  # Renderiza el texto de los ajustes

        self.puntaje_mostrado = 0
        self.puntaje_renderizado = self.fuente.render(f"{self.puntaje_mostrado}", True, BLANCO)  # Renderiza el puntaje del jugador

        self.num_skin = self.game.menu.jugar.jugador.num_skin  # Número del skin seleccionado en el menú de personalización
        self.texto_resultado = f"¡Felicidades, {self.game.nombre_jugador}, llegando hasta el nivel {self.game.menu.jugar.manager_niveles.num_nivel} conseguiste un puntaje de:"

        self.imagenes_skins = cargar_skins(self.num_skin, puntos_iniciales_skins_jugador)  # Carga las imágenes de los skins desde la carpeta de personajes
        self.imagen_mostrada = self.imagenes_skins["derecha"][0]  # Imagen que se muestra en la pantalla (por defecto es la imagen de la derecha del skin 1)
        self.imagen_mostrada = pg.transform.scale(self.imagen_mostrada, (128, 128))  # Escala la imagen
        self.lineas = dividir_texto(self.texto_resultado)  # Divide el texto de información del personaje en líneas para que se ajuste a la pantalla
        puntajes.append([self.game.nombre_jugador, self.game.menu.jugar.jugador.puntaje_total])  # Agrega el puntaje del jugador a la lista de puntajes

    def actualizar(self):  
        # Animación del puntaje
        if self.puntaje_mostrado < self.game.menu.jugar.jugador.puntaje_total:
            self.puntaje_mostrado += 3
            self.puntaje_renderizado = self.fuente.render(f"{self.puntaje_mostrado}", True, BLANCO)  # Renderiza el puntaje del jugador
        # Si nos pasamos, lo ajustamos al puntaje del jugador
        elif self.puntaje_mostrado > self.game.menu.jugar.jugador.puntaje_total:
            self.puntaje_mostrado = self.game.menu.jugar.jugador.puntaje_total
            self.puntaje_renderizado = self.fuente.render(f"{self.puntaje_mostrado}", True, AMARILLO)  # Renderiza el puntaje del jugador en amarillo al terminar el conteo
        
    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        self.pantalla.blit(self.texto_renderizado, (ANCHO_PANTALLA // 2 - self.texto_renderizado.get_width() // 2, 30))  # Dibuja el texto centrado en la pantalla
        self.pantalla.blit(self.imagen_mostrada, (ANCHO_PANTALLA//2 - self.imagen_mostrada.get_width()//2 , ALTO_PANTALLA//2 - self.imagen_mostrada.get_height()//2))

        # Impresión del texto
        y = ALTO_PANTALLA//2 + self.imagen_mostrada.get_height()//2 + 32  # 32 es el espacio de separación entre el sprite y el texto
        for linea in self.lineas:
            render = self.fuente.render(linea, True, BLANCO)
            x = (ANCHO_PANTALLA - render.get_width()) // 2  # Centra el texto en la pantalla
            self.pantalla.blit(render, (x, y))
            y += self.fuente.get_height() + 5
        self.pantalla.blit(self.puntaje_renderizado, (ANCHO_PANTALLA//2 - self.puntaje_renderizado.get_width()//2 , ALTO_PANTALLA//2 + self.imagen_mostrada.get_height()//2 + self.fuente.get_height() + 37))
        self.boton_confirmar.dibujar()  # Dibujar el botón de confirmar y volver al menú principal

    def eventos(self, evento):  # evento no se usa realmente, ya que no se escribe nada, pero es por continuidad y para que se pueda usar en el bucle de eventos del juego
        mouse_pos = pg.mouse.get_pos()
        if self.boton_confirmar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            mouse_pos = None  # Resetea la posición del mouse
            self.game.cambiar_modo(self.game.menu)  # Cambia el modo del juego al menú principal

class Menu:
    def __init__(self, game):
        self.game = game
        self.pantalla = game.pantalla  # Pantalla donde se dibuja el menú
        self.volumen = game.volumen
        
        #Opciones del menu
        self.ajustes = Ajustes(self)
        self.info = Informacion(self)
        self.puntajes = Puntajes(self)
        self.personalizacion = Personalizacion(self)
        self.opcion_a_funcion = {"Jugar":self.personalizacion, 
                                 "Ajustes":self.ajustes, 
                                 "Puntajes": self.puntajes,
                                 "Información":self.info, 
                                 "Salir":None} #Mapea el nombre de las opciones a ellas

        self.musica = game.canciones[0]
        self.botones = self.crear_botones()  # Crea los botones del menú
        self.logo = cargar_logo()

    def crear_juego(self):
        self.game.jugar = Jugar(self.game, 2)

    def crear_botones(self):
        botones = []  # Lista de botones del menú
        for i, nombre in enumerate(self.opcion_a_funcion):  # Crea un botón para cada opción del menú
            x = ANCHO_PANTALLA // 2 - 100  # Centra el botón en la pantalla (no cambia para los demás botones, ya que están alineados en el mismo x)
            y = 410 + i * 60  # Espacio entre botones (en este caso, 60 píxeles entre cada botón)
            self.boton = Boton(x, y, ANCHO_BOTON, ALTO_BOTON, nombre, self.pantalla)  # Crea un botón con las dimensiones y texto correspondientes
            botones.append(self.boton)  # Agrega el botón a la lista de botones del menú
        return botones

    def dibujar(self):
        self.pantalla.fill(NEGRO)
        for boton in self.botones:  # Dibuja cada botón en la pantalla
            boton.dibujar()
        self.pantalla.blit(self.logo, (ANCHO_PANTALLA // 2 - self.logo.get_width() // 2, - 20))  # Dibuja el logo del juego en la parte superior de la pantalla

    def actualizar(self):  # El menú no requiere actualizarse, por lo que se deja en pass
        pass

    def eventos(self, evento):  # Como no tiene para presionar teclas, "evento" no es realmente necesario, pero es por continuidad
        mouse_pos = mouse.get_pos()
        for boton in self.botones:  # Recorre la lista de botones del menú
            if boton.detectar_presionado(mouse_pos, mouse.get_pressed()[0]): #Si detecta click izquierdo
                self.game.cambiar_modo(self.opcion_a_funcion[boton.texto]) #Mapea el texto del boton a un modo de juego

# ==========================================================================
#  LÓGICA PARA EL PASO DE NIVELES Y JUEGO
# ==========================================================================

# Clase que maneja los niveles del juego, carga los niveles y sprites, y permite pasar de nivel
class Niveles:
    def __init__(self, jugar):
        self.jugar = jugar
        self.pantalla = jugar.pantalla_juego
        self.niveles = cargar_niveles()
        self.num_nivel = 1
        self.sprites = cargar_bloques(self.num_nivel)
        self.nivel = self.niveles[0]  # Inicia en el nivel 1
            
    def pasar_nivel(self):
        if 1 <= self.num_nivel+1 <= len(self.niveles):
            self.nivel = self.niveles[self.num_nivel]
            self.num_nivel += 1  # Aumenta el numero de nivel
            self.sprites = cargar_bloques(self.num_nivel)  # Carga los sprites del nuevo nivel
            return self.nivel
        #Cambio de nivel falla
    
    def dibujar(self):
        for y in range(1, ALTO_MATRIZ+1):
            for x in range(1, ANCHO_MATRIZ+1):
                ID = self.nivel[y][x]
                self.pantalla.blit(self.sprites[ID], ((x-1)*MEDIDA_BLOQUE, (y-1)*MEDIDA_BLOQUE))
                
        if self.jugar.debug:
            # Dibuja las lineas del grid
            for x in range(1, ANCHO_MATRIZ):
                draw.line(self.pantalla, NEGRO, (x*MEDIDA_BLOQUE, 0), (x*MEDIDA_BLOQUE, ALTO_PANTALLA))
            for y in range(1, ALTO_MATRIZ):
                draw.line(self.pantalla, NEGRO, (0, y*MEDIDA_BLOQUE), (ANCHO_PANTALLA, y*MEDIDA_BLOQUE))
                
    def actualizar(self):
        pass
    
    def cambio_nivel(self, num_nivel):
        if 1 <= num_nivel < len(self.niveles): # Verifica si existe el numero de nivel
            self.num_nivel = num_nivel
            self.nivel = self.niveles[num_nivel-1]
            
        elif num_nivel == len(self.niveles): # Se devuelve al primer nivel al terminar TODO (por que se devuelve? No deberia terminar y ya)
            self.nivel = self.num_niveles[0]

# Clase del juego: crea todo lo relacionado con el jugador y los elementos visuales que lo acompañan
class Jugar:
    def __init__(self, game, num_skin):
        self.game = game
        self.pantalla = game.pantalla  # Pantalla donde se dibuja el juego
        self.pantalla_juego = Surface((ANCHO_PANTALLA - 2*SEPARACION_BORDES_PANTALLA, ALTO_PANTALLA - MEDIDA_HUD - SEPARACION_BORDES_PANTALLA))
        self.cambiar_modo = game.cambiar_modo
        self.musica = game.canciones[1]
        self.sprites_bomba = game.sprites_bomba
        self.dibujar_texto = game.dibujar_texto # Toma el metodo de dibujar texto
        
        self.debug = False  # G para cambiar (muestra hitboxes y gridlines)
        self.manager_niveles = Niveles(self)
        self.nivel = self.manager_niveles.nivel
        self.jugador = Jugador(self, num_skin)  # Crea el jugador con el skin seleccionado
        self.hud = HUD(self)  # Crea el HUD del juego
        self.lista_pegamento = []  # Lista para almacenar los pegamentos que sueltan los enemigos
        self.capas = {
            0:[self.manager_niveles],  # El fondo
            1:self.asignar_extras(),  # Capa para objetos (llave, objetos, etc)
            2:[],  # Capa para bombas y pegamento
            3:self.colocar_enemigos(),  # Capa para enemigos y elementos que dañan al jugador
            4:[self.jugador],
            5:[]}  # Capa para explosiones
        
    def colocar_enemigos(self):
        coords_ocupadas = [(X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR)]
        enemigos = []
        
        while len(enemigos) < CANTIDAD_ENEMIGOS:
            x = randint(5, ANCHO_MATRIZ) # Inicia desde 5 para evitar que aparezcan cerca del jugador
            y = randint(5, ALTO_MATRIZ)  # Inicia desde 5 para evitar que aparezcan cerca del jugador
            
            if (x, y) not in coords_ocupadas and self.nivel[y][x] == 0:
                coords_ocupadas.append((x, y))
                enemigo = Enemigo(self, (x-1) * MEDIDA_BLOQUE, (y-1) * MEDIDA_BLOQUE)
                enemigos.append(enemigo)
        return enemigos
    
    def colocar_venenos(self):
        # Coloca los venenos en posiciones aleatorias del nivel, evitando que aparezcan cerca del jugador, a partir del nivel 2
        coords_ocupadas = [(X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR), (ANCHO_MATRIZ, self.capas[1][0].y_bloque)]  # Evita que aparezcan cerca del jugador y de la puerta
        venenos = []
        while len(venenos) < CANTIDAD_VENENOS:
            x = randint(5, ANCHO_MATRIZ) # Inicia desde 5 para evitar que aparezcan cerca del jugador
            y = randint(5, ALTO_MATRIZ)  # Inicia desde 5 para evitar que aparezcan cerca del jugador
                
            if (x, y) not in coords_ocupadas and self.nivel[y][x] == 0:
                coords_ocupadas.append((x, y))
                veneno = Veneno(self, (x-1) * MEDIDA_BLOQUE, (y-1) * MEDIDA_BLOQUE)
                venenos.append(veneno)
        return venenos

    def pasar_nivel(self):
<<<<<<< HEAD:merge.py
        self.nivel = self.manager_niveles.pasar_nivel()
        self.jugador.pasar_nivel(self.nivel)
        if self.manager_niveles.num_nivel == len(self.manager_niveles.niveles):
            self.iniciar_nivel_jefe()
        else:
            self.iniciar_nivel_jefe() #CAMBIAR
            
    
    def iniciar_nivel_normal(self):
        self.capas[1] = self.asignar_extras()
        self.capas[3] = self.colocar_enemigos() #Pone los enemigos
        self.jugador.invulnerabilidad() #Hace el jugador invulnerable al iniciar el nivel
        # Reinicio de las estadísticas de los caramelos
        for _ in range(self.jugador.contador_rojos):
            self.jugador.golpe -= 1
        for _ in range(self.jugador.contador_azules):
            self.jugador.rango -= 1
        # Reinicio de los contadores de caramelos
        self.jugador.contador_rojos = 0
        self.jugador.contador_azules = 0
    
    def iniciar_nivel_jefe(self):
        self.capas[3] = [Jefe(self, 10, 5)]
        
=======
        if self.manager_niveles.pasar_nivel():
            self.nivel = self.manager_niveles.nivel #Cambia los datos de nivel
            self.jugador.rect.topleft = X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR #Reinicia la pos del jugador
            self.jugador.nivel = self.nivel #Cambia el nivel del jugador
            self.jugador.cantidad_bombas += 1  # Aumenta la cantidad de bombas del jugador al pasar de nivel (+1 por niveldw)
            self.capas[1] = self.asignar_extras()
            self.capas[3] = self.colocar_venenos() + self.colocar_enemigos() # Pone los elementos que dañan al jugador
            self.jugador.invulnerabilidad() #Hace el jugador invulnerable al iniciar el nivel
            # Reinicio de las estadísticas de los caramelos
>>>>>>> d304205670b6bf9c0ebae2994ac1a6dad9ed12dd:main.py
    
    def menu_mejoras(self):
        self.game.modo_previo = self
        self.game.modo = self.mejoras
    
    def obtener_rompibles(self):
        bloques = [] # Guarda los bloques rompibles
        for y in range(1, ALTO_MATRIZ+1):
            for x in range(1, ANCHO_MATRIZ+1):
                if self.nivel[y][x] == 2:
                    bloques.append((x,y))
        return bloques
            
     # Aquí usamos rangos, por lo que debemos sumar 1 para recorrer hasta el final de la zona jugableAdd commentMore actions
    def asignar_llave(self):
        bloques_disponibles = [
            (x, y) for y in range(1, ALTO_MATRIZ + 1) for x in range(1, ANCHO_MATRIZ + 1) if self.nivel[y][x] == 2
        ]  # Encuentra todos los bloques destructibles
        x, y = choice(bloques_disponibles)  # Selecciona un bloque aleatorio de los bloques destructibles
        self.llave = Llave(self, x, y)
        return self.llave  # Retorna la llave generada aleatoriamente en el nivel actual

    def asignar_puerta(self):
        # La puerta es un caso especial, ya que solo vamos a generarla al final del nivel, y debe estar en el borde derecho del nivel
        bloques_disponibles = [
            (ANCHO_MATRIZ, y) for y in range(1, ALTO_MATRIZ + 1) if self.nivel[y][ANCHO_MATRIZ] == 0
        ]  # Encuentra todos los bloques donde se puede colocar la puerta
        _, y = choice(bloques_disponibles)  # Selecciona un bloque aleatorio de los bloques destructibles
        self.puerta = Puerta(self, y)
        return self.puerta
            
    def asignar_consumibles(self):
        pociones = []
        caramelos = []
        # Encuentra todos los bloques destructibles que no sean el de la llave
        bloques_disponibles = [
            (x, y) for y in range(1, ALTO_MATRIZ + 1) for x in range(1, ANCHO_MATRIZ + 1) if self.nivel[y][x] == 2 and not (self.llave.x_bloque == x and self.llave.y_bloque == y)
        ]  # Encuentra todos los bloques destructibles que no sean el de la llave
        # Asegura que no se generen más pociones que bloques disponibles (se puede establecer una cantidad máxima de caramelos con CANTIDAD_CARAMELOS)
        cantidad_pociones = min(CANTIDAD_POCIONES, len(bloques_disponibles))        
        while len(pociones) < cantidad_pociones:  # Genera caramelos hasta alcanzar la cantidad deseada
            x, y = choice(bloques_disponibles)
            pocion = Pociones(self, x, y)
            pociones.append(pocion)
            bloques_disponibles.remove((x, y))  # Elimina el bloque donde se generó el caramelo para evitar duplicados
        cantidad_caramelos = min(CANTIDAD_CARAMELOS, len(bloques_disponibles))  # Asegura que no se generen más caramelos que bloques disponibles
        while len(caramelos) < cantidad_caramelos:  # Genera caramelos hasta alcanzar la cantidad deseada
            x, y = choice(bloques_disponibles)
            caramelo = Caramelos(self, x, y)
            caramelos.append(caramelo)
            bloques_disponibles.remove((x, y))  # Elimina el bloque donde se generó el caramelo para evitar duplicados
        
        return pociones + caramelos  # Retorna una lista de caramelos generados aleatoriamente en el nivel actual

    def asignar_extras(self):
        return [self.asignar_llave(), self.asignar_puerta()] + self.asignar_consumibles()  # Retorna una lista de objetos extras (llave, puerta, caramelos y pociones) generados aleatoriamente en el nivel actual
    
    def matar_entidad(self, entidad):
        for capa in self.capas:
            if entidad in self.capas[capa]:
                self.capas[capa].remove(entidad)
                break
    
    def actualizar(self):
        self.hud.actualizar()
        for capa in sorted(self.capas.keys()): #Actualiza entidades (jugador, enemigos, bombas...)
            for entidad in self.capas[capa]:
                entidad.actualizar()
        # print(self.jugador.golpe)

    def eventos(self, evento):
        self.jugador.eventos(evento)
        if evento.type == KEYDOWN:
            if evento.key == K_g:
                if not self.debug:
                    self.debug = True
                    self.jugador.vidas = float('inf')
                    self.jugador.bombas = float('inf')
                else:
                    self.debug = False
                    self.jugador.vidas = VIDAS
                    self.jugador.cantidad_bombas = CANTIDAD_BOMBAS + self.manager_niveles.num_nivel  # Reinicia las bombas al salir del modo debug
            
            elif evento.key == K_p:
                self.pasar_nivel()

    def dibujar(self):
        #Juego
        if not hasattr(self.jugador,"game_over"):  # Si el jugador ha perdido, dibuja la pantalla de Game Over
            self.pantalla_juego.fill(BLANCO)
            

            for capa in sorted(self.capas.keys()): #Dibuja entidades (jugador, enemigos, bombas...)
                for entidad in self.capas[capa]:  # Recorre cada capa y dibuja las entidades
                    entidad.dibujar()
                if capa == 1:  # Después de dibujar los elementos de la capa 1, dibuja el pegamento
                    for pegamento in self.lista_pegamento:  # Dibuja los pegamentos que sueltan los enemigos
                        pegamento.dibujar()
            
            #Dibuja la pantalla de juego en la principal
            self.pantalla.blit(self.pantalla_juego, (SEPARACION_BORDES_PANTALLA, MEDIDA_HUD))
            self.hud.dibujar()  # Dibuja el HUD del juego
        else:
            self.jugador.game_over.dibujar()

# ==========================================================================
#  CLASE MAESTRA DEL JUEGO
# ==========================================================================

# Clase game que maneja a todas las otras clases
class Game: 
    def __init__(self):
        init()  # Inicializamos Pygame
        self.pantalla = display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))  # Configura la ventana
        display.set_caption("Wooly Warfare")  # Título de la ventana
        self.clock = time.Clock()  # Crea un objeto de reloj para controlar la tasa de refresco, necesario para la física y el movimiento
        self.running = True  # Variable para controlar el bucle del juego
        self.dt = 0  # Delta time, tiempo entre frames
        
        # Configuraciones de la música
        self.canciones = cargar_canciones()
        self.musica = None  # Espera a tener una instancia de música
        self.volumen = VALOR_INCIAL_VOLUMEN  # Volumen inicial del juego
        
        self.sprites_bomba = cargar_bomba()
        self.nombre_jugador = None  # Nombre del jugador, se puede cambiar en el menú de personalización

        self.menu = Menu(self)  # Crea una instancia del menú

        self.modo = self.menu #Inicia en el modo menu
        self.modo_previo = None #Guarda el modo previo, permite devolverse en el menu

        self.administrar_musica()  # Llama a la función para administrar la música del juego

    def dibujar_texto(self, texto, x, y, fuente=fuente_texto, color=NEGRO):
        img = fuente.render(texto, True, color)
        self.pantalla.blit(img, (x, y))
    
    def administrar_musica(self):
        if self.musica != self.modo.musica:
            if self.musica is not None:  # Si es la primera vez que se llama, no hay música, entonces no haríamos nada
                self.musica.stop()
            self.musica = self.modo.musica
            self.musica.set_volume(self.volumen)  # Establece el volumen de la música
            self.musica.play(-1)  # Reproduce la música en bucle

    def cambiar_modo(self, modo):
        if modo == None:
            guardar_archivo(ARCHIVO_PUNTAJES, str(puntajes))  # Guarda los puntajes en el archivo antes de salir
            self.running = False
        else:
            self.modo_previo = modo
            self.modo = modo
            self.administrar_musica() #Cambia a la musica del modo respectivo
    
    def eventos(self):
        for evento in event.get():
            if evento.type == QUIT:
                guardar_archivo(ARCHIVO_PUNTAJES, str(puntajes))  # Guarda los puntajes en el archivo antes de salir
                self.running = False
            self.modo.eventos(evento) #Corre los eventos del modo activo
    
    def actualizar(self):
        self.modo.actualizar()

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        self.modo.dibujar()
        
    def run(self):
        while self.running:  # Bucle principal del juego
            display.flip()  # Actualiza la pantalla
            self.dt = self.clock.tick(FPS) / 1000  # Controla la tasa de refresco del juego
            self.eventos() #Toma input del usuario
            self.actualizar()  # Actualiza el estado del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)
            self.dibujar()  # Dibuja los elementos del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)

                
# Ejecutar el juego
if __name__ == "__main__": #solo se ejecuta si se hace run, no si es import
    game = Game()
    game.run()



"""
# TODO:
# 4. Implementar la clase Jefe con sus mecánicas de ataque y vida.
"""