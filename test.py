from pygame import *
from config import *  # Importa las configuraciones del juego, como dimensiones y FPS
from sprites import *  # Importa los sprites del jugador y otros elementos visuales
from niveles import *
from threading import Thread
from random import randint, choice
from time import sleep


class Bomba:
    bombas = [] #Guarda las bombas activas
    def __init__(self, pantalla, bloque_x, bloque_y):
        self.pantalla = pantalla #Pantalla para dibujar la bomba
        self.rect = Rect(bloque_x*MEDIDA_BLOQUE, bloque_y*MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
        self.tiempo_detonar = 2  # Tiempo en segundos para que la bomba explote
        self.hit = 1 # Daño que causa la bomba al explotar
        self.activa = True
        Bomba.bombas.append(self)
        hilo = Thread(target=self.detonar) #Crea un hilo para la bomba
        hilo.daemon = True
        hilo.start()

    def detonar(self):
        sleep(self.tiempo_detonar)
        self.active = False #Explota
        #TODO
        Bomba.bombas = [b for b in Bomba.bombas if b != self] #Quita la bomba
    
    def actualizar(self):
        pass #TODO
    
    def dibujar(self, pantalla):
        if self.activa:
            draw.rect(pantalla, NEGRO, self.rect)

class Jugador:
    def __init__(self, juego, skin=None):
        self.pantalla = juego.pantalla_juego  # Pantalla donde se dibuja el jugador
        self.nivel = juego.nivel

        self.frame = 0  # Frame actual del sprite del jugador
        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = 3  # Número de skin del jugador (se puede cambiar para personalizar el jugador)
        self.direccion = "abajo"  # Dirección inicial del jugador (y a la que está mirando)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_iniciales_skins_jugador)  # Carga la skin del jugador desde la hoja de sprites
        self.moviendose = False  # Indica si el jugador se está moviendo o no
        
        self.vidas = 3  # Cantidad de vidas del jugador
        self.velocidad = 5  # Velocidad de movimiento del jugador (en pixeles)
        
        self.rect = Rect(MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE) #Rectangulo del jugador para posicion y colision
        
        self.movimientos_posibles = {
            K_w: (0, -(self.velocidad), "arriba"),  # Arriba
            K_s: (0, self.velocidad, "abajo"),     # Abajo
            K_a: (-(self.velocidad), 0, "izquierda"), # Izquierda
            K_d: (self.velocidad, 0, "derecha")     # Derecha
        }

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
            if self.nivel[y][x] != 0:
                return False
        return True
    
    def actualizar(self, keys):
        dx, dy = 0, 0

        #Saca el input del usuario
        self.moviendose = False
        for tecla in self.movimientos_posibles.keys():
            if keys[tecla]:
                self.moviendose = True
                dx, dy, self.direccion = self.movimientos_posibles[tecla]        
        
        #Movimiento del jugador
        # Si está dentro de los límites del mapa y camina en aire
        rect_dx, rect_dy = self.rect.move(dx, 0), self.rect.move(0, dy)
        #Verifica los ejes independientemente para mantener deslizamiento en muros con movimiento diagonal
        if self.verificar_colision(rect_dx):
            self.rect = self.rect.move(dx, 0)
        if self.verificar_colision(rect_dy):
            self.rect = self.rect.move(0, dy)
    
        #Animacion
        if time.get_ticks() - self.ultima_actualizacion_frame > 150:  # Si el jugador se está moviendo y han pasado 150ms
            self.actualizar_frame_sprite()  # Actualiza el frame del sprite del jugador
            self.ultima_actualizacion_frame = time.get_ticks()  # Reinicia el tiempo de la última actualización del sprite
                   

    
    def actualizar_frame_sprite(self):
        if self.moviendose: #Jugador se mueve
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.skin_hoja_sprites) # Frame ciclico, se reinicia cuando llega al final
        else: #Jugador no se mueve
            self.frame = 0 #Reinicia

    #  Dibuja al jugador en la pantalla
    def dibujar(self):
        self.pantalla.blit(self.skin_hoja_sprites[self.direccion][self.frame], (self.rect.x, self.rect.y))  # Dibuja el sprite del jugador en la pantalla

    def poner_bomba(self):
        Bomba(self.pantalla, self.rect.centerx//MEDIDA_BLOQUE, self.rect.centery//MEDIDA_BLOQUE) # Pone una bomba en el jugador y la guarda en la lista de bombas

    def habilidad1(self):
        pass
    
    def habilidad2(self):
        pass
    
    def eventos(self, evento):
        if evento.type == KEYDOWN:
            if evento.key == K_SPACE: #Si le da a espacio
                self.poner_bomba()

            if evento.key == K_1: #Si le da a 1
                self.habilidad1()
                
            elif evento.key == K_2: #O si le da a 2
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
        self.pantalla_juego = Surface((ANCHO_PANTALLA - 2*SEPARACION_BORDES_PANTALLA, ALTO_PANTALLA - MEDIDA_HUD - SEPARACION_BORDES_PANTALLA))
        self.debug = True
        
        self.niveles = game.niveles
        self.num_nivel = 1 #Inicia en el nivel 1
        self.nivel = self.niveles[0] #Contiene la posicion de enemigos y obstaculos
        
        
        self.bombas = []  # Lista con bombas que el jugador pone, se borran al explotar
        self.jugador = Jugador(self) #TODO Falta la skin
    
    def dibujar_nivel(self):
        for y in range(1, ALTO_MATRIZ-1): #Por cada fila
            for x in range(1, ANCHO_MATRIZ-1): #Por cada bloque
                if self.nivel[y][x] != 0: #Si no es aire, lo dibuja
                    draw.rect(self.pantalla_juego, GRIS, Rect((x-1)*MEDIDA_BLOQUE, (y-1)*MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE))
                    
        if self.debug:
            #Dibuja las lineas del grid
            for x in range(1, ANCHO_MATRIZ):
                draw.line(self.pantalla_juego, NEGRO, (x*MEDIDA_BLOQUE, 0), (x*MEDIDA_BLOQUE, ALTO_PANTALLA))
            for y in range(1, ALTO_MATRIZ):
                draw.line(self.pantalla_juego, NEGRO, (0, y*MEDIDA_BLOQUE), (ANCHO_PANTALLA, y*MEDIDA_BLOQUE))


    def actualizar(self):
        keys = key.get_pressed()
        for bomba in Bomba.bombas:
            bomba.actualizar()
        print(Bomba.bombas)
        self.jugador.actualizar(keys)

        

    def eventos(self, evento):
        self.jugador.eventos(evento)
        if evento.type == KEYDOWN:
            if evento.key == K_g:
                self.debug = not self.debug

        
    def dibujar(self):
        self.pantalla_juego.fill(BLANCO) #Fondo blanco
        self.dibujar_nivel()
        
        #Entidades
        for bomba in Bomba.bombas:
            bomba.dibujar(self.pantalla_juego)
        self.jugador.dibujar()
        
        #Dibuja la pantalla de juego en la principal
        self.pantalla.blit(self.pantalla_juego, (SEPARACION_BORDES_PANTALLA, MEDIDA_HUD))

        
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
        self.modo = self.jugar # Inicia en jugar TODO (esto es temporal, deberia iniciar en el menu principal)

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
            x = randint(0, ANCHO_MATRIZ + 1) * MEDIDA_BLOQUE + SEPARACION_BORDES_PANTALLA  # Genera una coordenada x aleatoria dentro del mapa
            y = randint(0, ALTO_MATRIZ + 1) * MEDIDA_BLOQUE + MEDIDA_HUD  # Genera una coordenada y aleatoria dentro del mapa
            
            #Revisa que no ponga un enemigo encima de otro
            if (x, y) not in enemigos_coords:
                enemigo = Enemigo(x, y, self.pantalla)  # Crea una instancia del enemigo en la posición aleatoria
                self.enemigos.append(enemigo)  # Agrega el enemigo a la lista de enemigos
                enemigos_puestos += 1
    

    def actualizar(self):
        for evento in event.get():
            if evento.type == QUIT:
                self.running = False
            self.modo.eventos(evento)
            
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