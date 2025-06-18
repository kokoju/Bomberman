from pygame import *
from config import *  # Importa las configuraciones del juego, como dimensiones y FPS
from sprites import *  # Importa los sprites del jugador y otros elementos visuales
from niveles import *
from threading import Thread
from random import randint, choice
from time import sleep


class Bomba:
    def __init__(self, pantalla, x, y):
        self.pantalla = pantalla #Pantalla para dibujar la bomba
        self.x = x  # Posición x de la bomba
        self.y = y  # Posición y de la bomba
        self.rect = Rect(x, y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
        self.tiempo_detonar = 2  # Tiempo en segundos para que la bomba explote
        self.hit = 1 # Daño que causa la bomba al explotar
        hilo = Thread(target=self.detonar) #Crea un hilo para la bomba
        hilo.daemon = True
        hilo.start()

    def detonar(self):
        #Dibuja la bomba
        draw.rect(self.pantalla, "black", self.rect)
        sleep(self.tiempo_detonar)
        

class Jugador:
    def __init__(self, juego, skin=None):
        self.pantalla = juego.pantalla  # Pantalla donde se dibuja el jugador
        
        self.x = 0  # Posición x del jugador
        self.y = 0  # Posición y del jugador

        self.frame = 0  # Frame actual del sprite del jugador
        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = 3  # Número de skin del jugador (se puede cambiar para personalizar el jugador)
        self.direccion = "abajo"  # Dirección inicial del jugador (y a la que está mirando)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_iniciales_skins_jugador)  # Carga la skin del jugador desde la hoja de sprites
        self.moviendose = False  # Indica si el jugador se está moviendo o no
        
        self.bombas = 5  # Cantidad de bombas que el jugador puede colocar
        self.vidas = 3  # Cantidad de vidas del jugador
        self.velocidad = 5  # Velocidad de movimiento del jugador (en pixeles)
        
        self.rect = Rect(self.x, self.y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al jugador en el canvas (SE USA EN COLISIONES)
        
        self.movimientos_posibles = {
            K_w: (0, -(self.velocidad), "arriba"),  # Arriba
            K_s: (0, self.velocidad, "abajo"),     # Abajo
            K_a: (-(self.velocidad), 0, "izquierda"), # Izquierda
            K_d: (self.velocidad, 0, "derecha")     # Derecha
        }

    #  Mueve al jugador en la dirección especificada
    def actualizar(self):
        keys = key.get_pressed()
        
        #Saca el input del usuario
        self.moviendose = False
        for tecla in self.movimientos_posibles.keys():
            if keys[tecla]:
                self.moviendose = True
                print(tecla)
                dx, dy, direccion = self.movimientos_posibles[tecla]
        
        #Mueve al jugador basado en el input
        new_x = self.x + dx  # Se calcula la nueva posición x
        new_y = self.y + dy
        rectangulo_verif = Rect(new_x, new_y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa la nueva posición del jugador
        
        # Si está dentro de los límites del mapa
        if ((ANCHO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_x > SEPARACION_BORDES_PANTALLA and
            (ALTO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_y > MEDIDA_HUD):
            
            self.y = new_y
            self.x = new_x
            self.direccion = direccion  # Actualiza la dirección del jugador
            self.rect = rectangulo_verif  # Actualiza el rectángulo del jugador a la nueva posición
        
        self.actualizar_frame_sprite()

    def poner_bomba(self):
        if self.bombas > 0: # Si le quedan bombas
            self.bombas -= 1
            Bomba(self.pantalla, self.x, self.y)  # Pone una bomba en el jugador

    
    def actualizar_frame_sprite(self):
        if self.moviendose:  # Si el jugador se está moviendo
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = 1  (self.frames + 1) % len(self.skin_hoja_sprites) # Frame ciclico, se reinicia cuando llega al final
            
        else: #Jugador no se mueve
            self.frame = 0 #Reinicia

    #  Dibuja al jugador en la pantalla
    def dibujar(self):
        self.pantalla.blit(self.skin_hoja_sprites[self.direccion][self.frame], (self.x, self.y))  # Dibuja el sprite del jugador en la pantalla

    def habilidad1(self):
        pass
    
    def habilidad2(self):
        pass
    
    def actualizar(self, keys):
        if keys[K_SPACE]: #Si le da a espacio
            self.poner_bomba()

        if keys[K_1]: #Si le da a 1
            self.habilidad1()
            
        elif keys[K_2]: #Si le da a 2
            self.habilidad2()

class Enemigo:
    def __init__(self, x, y, pantalla):
        self.x = x
        self.y = y
        self.pantalla = pantalla
        self.frame = 0
        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = 1  # Número de skin del enemigo (se puede cambiar para hacerlo más complicado)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_inciales_skins_enemigos)  # Carga la skin del enemigo desde la hoja de sprites
        self.direccion = 'abajo'  # Dirección inicial del enemigo (y a la que está mirando)
        self.vida = 1
        self.velocidad = 5
        self.rect = Rect(self.x, self.y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al enemigo en el canvas (uso para colisiones)

    # Mueve al enemigo en una dirección aleatoria
    def movimiento(self, obstaculos):
        # Genera un movimiento aleatorio
        movimientos = {"arriba" : (0, -self.velocidad), "abajo" : (0, self.velocidad), "izquierda" : (-self.velocidad, 0), "derecha" : (self.velocidad, 0)}  # Diccionario con los movimientos posibles
        movimiento_elegido = choice(list(movimientos.keys()))  # Elige un movimiento aleatorio del diccionario
        dx, dy = movimientos[movimiento_elegido]  # Obtiene el desplazamiento correspondiente al movimiento elegido
        # Cambia sus coords x y y
        new_x = self.x + dx  # Se calcula la nueva posición x
        new_y = self.y + dy
        rectangulo_verif = Rect(new_x, new_y, MEDIDA_BLOQUE, MEDIDA_BLOQUE, "red")  # Rectángulo que representa la nueva posición del jugador
        # Se hace una resta de MEDIDA_BLOQUE para que no se salga, ya que recordamos que las coords marcan la esquina superior izquierda del rectángulo
        if (ANCHO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_x > SEPARACION_BORDES_PANTALLA and (ALTO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_y > MEDIDA_HUD:  # Si está dentro de los límites del mapa
            # Verifica si no hay obstáculos en la nueva posición
            if all(not rectangulo_verif.colliderect(obs.rect) for obs in obstaculos):  # Si el rectángulo del enemigo no colisiona con NINGÚN obstáculo
                self.y = new_y
                self.x = new_x
                self.direccion = movimiento_elegido  # Actualiza la dirección del enemigo
                self.rect = rectangulo_verif  # Actualiza el rectángulo del enemigo a la nueva posición

    def actualizar_frame_sprite(self):
        self.ultima_actualizacion_frame = time.get_ticks()  # Reinicia el tiempo de la última actualización del sprite
        self.frame += 1  # Incrementa el frame actual del sprite
        if self.frame >= len(self.skin_hoja_sprites):  # Si el frame actual es mayor o igual al número de frames del sprite en la dirección actual
            self.frame = 0  # Reinicia el frame a 0 para que vuelva al primer sprite de la animación

    #  Dibuja al enemigo en la pantalla
    def dibujar(self):
        self.pantalla.blit(self.skin_hoja_sprites[self.direccion][self.frame], (self.x, self.y))  # Dibuja el sprite del jugador en la pantalla

class Jugar:
    def __init__(self, game):
        self.pantalla = game.pantalla
        self.pantalla_juego = Surface((ANCHO_PANTALLA - 2*SEPARACION_BORDES_PANTALLA, ALTO_PANTALLA - MEDIDA_HUD))
        self.debug = False
        
        self.niveles = game.niveles
        self.num_nivel = 1 #Inicia en el nivel 1
        self.nivel = self.niveles[0] #Contiene la posicion de enemigos y obstaculos
        
        self.jugador = Jugador(self) #TODO Falta la skin
        
    def actualizar(self):
        self.jugador.actualizar()
        
    def dibujar(self):
        self.pantalla.fill(BLANCO) #Fondo blanco
        self.pantalla_juego.blit(self.pantalla, (SEPARACION_BORDES_PANTALLA, MEDIDA_HUD))
        
        #Dibuja el mapa
        for i in range(ANCHO_MATRIZ): #Por cada fila
            for j in range(ALTO_MATRIZ): #Por cada tile
                if self.nivel[j][i] != 0: #Si no es aire
                    draw.rect(self.pantalla_juego, "brown", Rect(j*MEDIDA_BLOQUE, i*MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE))
        
        self.jugador.dibujar()
                    

class Game: 
    def __init__(self):
        init()  # Inicializa Pygame
        
        self.pantalla = display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))  # Configura la ventana
        display.set_caption("Bomberman")  # Título de la ventana
        self.clock = time.Clock()  # Crea un objeto de reloj para controlar la tasa de refresco, necesario para la física y el movimiento
        self.running = True  # Variable para controlar el bucle del juego
        self.dt = 0  # Delta time, tiempo entre frames
        
        self.niveles = cargar_niveles()
        self.jugar = Jugar(self)
        self.modo = self.jugar # Inicia en jugar TODO (esto es temporal)

        self.enemigos = []  # Lista de enemigos en el juego
        self.obstaculos = []  # Lista de obstáculos en el juego
        self.colocar_enemigos()


    def cambio_nivel(self):
        self.nivel += 1  # Incrementa el nivel actual del juego
        if self.nivel > len(self.lista_niveles):
            self.nivel = 0

    def colocar_enemigos(self):
        enemigos_puestos = 0
        enemigos_coords = []
        while enemigos_puestos < CANTIDAD_ENEMIGOS:
            x = randint(0, ANCHO_MATRIZ - 1) * MEDIDA_BLOQUE + SEPARACION_BORDES_PANTALLA  # Genera una coordenada x aleatoria dentro del mapa
            y = randint(0, ALTO_MATRIZ - 1) * MEDIDA_BLOQUE + MEDIDA_HUD  # Genera una coordenada y aleatoria dentro del mapa
            
            #Revisa que no ponga un enemigo encima de otro
            if (x, y) not in enemigos_coords:
                enemigo = Enemigo(x, y, self.pantalla)  # Crea una instancia del enemigo en la posición aleatoria
                self.enemigos.append(enemigo)  # Agrega el enemigo a la lista de enemigos
                enemigos_puestos += 1


    def actualizar(self):
        for evento in event.get():
            if evento.type == QUIT:
                self.running = False
            
            self.modo.actualizar()
    
    def dibujar(self):
        self.modo.dibujar()
        
    
    def run(self):
        while self.running:  # Bucle principal del juego
            display.flip()  # Actualiza la pantalla
            self.dt = self.clock.tick(FPS) / 1000  # Controla la tasa de refresco del juego

            self.actualizar()  # Actualiza el estado del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)
            self.dibujar()  # Dibuja los elementos del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)
        

if __name__ == "__main__": #solo se ejecuta si se hace run, no si es import
    game = Game()
    game.run()