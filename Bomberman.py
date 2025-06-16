# Módulos necesarios 
from pygame import *  # Importa todos los módulos de Pygame necesarios para el juego
from time import sleep  # Importa sleep para manejar los Threads
from random import choice  # Importa choice para seleccionar elementos aleatorios de listas (movimiento enemigo)
from threading import Thread  # Importa los Threads para el manejo de entidades en paralelo
from config import *  # Importa las configuraciones del juego, como dimensiones y FPS
from sprites import *  # Importa los sprites del jugador y otros elementos visuales

# Usaremos una definición HD (1280x720p)
# En la parte superior de la pantalla, dejaremos una HUD de tamaño 1280x176 
# Abajo del HUD, haremos matrices de 11x26 (siendo cada bloque de 48x48): esto nos dejará con 32 pixeles sobrantes, repartidos en 16 pixeles en la parte izquierda y 16 pixeles en la parte derecha de la pantalla
# Además, dejé un espacio de 16 pixeles entre la matriz y el borde inferior, para que no se vea tan pegado
# Haremos los niveles con matrices (11x26), y como no se requiere crear nuevos, podemos ponerlos dentro del archivo de código

#  fuente_texto = font.Font("assets/FUENTEJUEGO.TTF", 30)  # USAR PARA EL TEXTO DEL JUEGO


# Definiremos lo que significa cada bloque de la matriz:
# 0 = vacío
# 1 = bloque indestructible
# 2 = bloque destructible
 
# Las demás cosas que se colocan en la matriz son objetos que se generan aleatoriamente, y no se colocan en la matriz, sino que se generan en el momento de crear el nivel



nivel1 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

nivel2 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

nivel3 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

nivel4 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]


# Ideas de Items 
# Fantasmal -> Permite al jugador atravesar bloques destructibles/indestructibles por un tiempo limitado 
# Explosivo -> Aumenta el rango de las bombas del jugador por un tiempo limitado, además de no detenerse al contacto de un muro
# Freeze -> Congela a los enemigos por un tiempo limitado

# Clase Jugador
class Jugador:
    def __init__(self, x, y, pantalla, skin=None):
        self.x = x  # Posición x del jugador
        self.y = y  # Posición y del jugador
        self.pantalla = pantalla  # Pantalla donde se dibuja el jugador
        self.frame = 0  # Frame actual del sprite del jugador
        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = 3  # Número de skin del jugador (se puede cambiar para personalizar el jugador)
        self.direccion = "abajo"  # Dirección inicial del jugador (y a la que está mirando)
        self.skin_hoja_sprites = cargar_skin(self.numero_skin)  # Carga la skin del jugador desde la hoja de sprites
        self.bombas = 5  # Cantidad de bombas que el jugador puede colocar
        self.vidas = 3  # Cantidad de vidas del jugador
        self.velocidad = 5  # Velocidad de movimiento del jugador (en pixeles)
        self.rect = Rect(self.x, self.y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al jugador en el canvas (SE USA EN COLISIONES)

    #  Mueve al jugador en la dirección especificada
    def movimiento(self, dx, dy, obstaculos, direccion):
        # Cambia sus coords x y y
        new_x = self.x + dx  # Se calcula la nueva posición x
        new_y = self.y + dy
        rectangulo_verif = Rect(new_x, new_y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa la nueva posición del jugador
        # Se hace una resta de MEDIDA_BLOQUE para que no se salga, ya que recordamos que las coords marcan la esquina superior izquierda del rectángulo
        if (ANCHO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_x > SEPARACION_BORDES_PANTALLA and (ALTO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_y > MEDIDA_HUD:  # Si está dentro de los límites del mapa
            # Verifica si no hay obstáculos en la nueva posición
            if all(not rectangulo_verif.colliderect(obs.rect) for obs in obstaculos):  # Si el rectángulo del jugador no colisiona con NINGÚN obstáculo
                self.y = new_y
                self.x = new_x
                self.direccion = direccion  # Actualiza la dirección del jugador
                self.rect = rectangulo_verif  # Actualiza el rectángulo del jugador a la nueva posición

    def actualizar_frame_sprite(self):
        self.ultima_actualizacion_frame = time.get_ticks()  # Reinicia el tiempo de la última actualización del sprite
        self.frame += 1  # Incrementa el frame actual del sprite
        if self.frame >= len(self.skin_hoja_sprites):  # Si el frame actual es mayor o igual al número de frames del sprite en la dirección actual
            self.frame = 0  # Reinicia el frame a 0 para que vuelva al primer sprite de la animación


    #  Dibuja al jugador en la pantalla
    def dibujar_jugador(self, pantalla):
        pantalla.blit(self.skin_hoja_sprites[self.direccion][self.frame], (self.x, self.y))  # Dibuja el sprite del jugador en la pantalla

    def habilidad1(self):
        pass
    
    def habilidad2(self):
        pass
    
    def actualizar(self, event):  
        pass  # REVISAR, LO DE PRESIONAR UNA TECLA DEBERÍA ESTAR EN GAME, NO AQUÍ: ESTO DEBERÍA SER PARA LLAMAR A LAS FUNCIONES
        """
        if event.type == KEYDOWN: #Si presiona una tecla
            
            if event.key == K_SPACE: #Si le da a espacio
                Bomba(self.x, self.y) #Pone una bomba
                
            elif event.key == K_1: #Si le da a 1
                self.habilidad1
                
            elif event.key == K_2:
                self.habilidad2
        """

# Clase Enemigo
class Enemigo:
    def __init__(self, x, y, pantalla):
        self.x = x
        self.y = y
        self.pantalla = pantalla
        self.vida = 1
        self.velocidad = 5
        self.direccion = 'abajo'
        self.rect = Rect(self.x, self.y, 50, 50)  # Rectángulo que representa al enemigo en el canvas (TEMPORAL, BORRAR DESPUÉS)

    # Mueve al enemigo en una dirección aleatoria
    def movimiento(self, obstaculos):
        # Genera un movimiento aleatorio
        movimientos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = choice(movimientos)
        new_x = self.x + dx  # Se calcula la nueva posición x
        new_y = self.y + dy  # Se calcula la nueva posición y
        if (ANCHO_PANTALLA - SEPARACION_BORDES_PANTALLA) > new_x > SEPARACION_BORDES_PANTALLA and (ALTO_PANTALLA - SEPARACION_BORDES_PANTALLA) > new_y > MEDIDA_HUD:  # Si está dentro de los límites del mapa
            # Verifica si no hay obstáculos en la nueva posición
            if (new_x, new_y) not in [(obs.x, obs.y) for obs in obstaculos]:
                self.x = new_x
                self.y = new_y


    def poner_bomba(self, lista_obstaculos):
        pass

        

class Bomba:
    def __init__(self, pantalla, x, y):
        self.pantalla = pantalla #Pantalla para dibujar la bomba
        self.x = x  # Posición x de la bomba
        self.y = y  # Posición y de la bomba
        self.rect = Rect(x, y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
        self.tiempo_detonar = 2  # Tiempo en segundos para que la bomba explote
        self.hit = 1 # Daño que causa la bomba al explotar
        Thread(target=self.detonar, args=([], [])).start()  # Inicia el temporizador de la bomba en un hilo separado

    def detonar(self, lista_obstaculos, enemigos):
        sleep(self.tiempo_detonar)
        # CONTINUAR AQUÍ: Lógica de explosión de la bomba, que afectará a enemigos y obstáculos
        #TODO
        draw.rect(self.pantalla, "black", self.rect)
    
class Explosion:
    pass


class Obstaculo:
    def __init__(self, x, y, destructible=False):
        self.x = x  # Posición x del obstáculo
        self.y = y  # Posición y del obstáculo
        self.destructible = destructible  # Si es destructible, puede ser destruido por una bomba
        self.rect = Rect(x, y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al obstáculo en el canvas (SE USA EN COLISIONES)

    def colocar(self, pantalla):
        draw.rect(pantalla, "brown" if self.destructible else "gray", self.rect)  # Dibuja el obstáculo en la pantalla, con un color diferente si es destructible

    # Destruye el obstáculo si es destructible (se le pasa la lista de obstáculos y se saca solo)
    def destruir(self, lista_obstaculos):
        if self.destructible:
            lista_obstaculos.remove(self)


class Jefe:
    pass


class Objetos:
    pass



class Menu:
    pass


class In_Game:
    pass


    

# Creamos una clase para el juego: esta llamará todas las opciones anteriores y las ejecutará en el orden correcto
class Game: 
    def __init__(self):
        init()  # Inicializamos Pygame
        self.pantalla = display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))  # Configura la ventana
        display.set_caption("Bomberman")  # Título de la ventana
        self.clock = time.Clock()  # Crea un objeto de reloj para controlar la tasa de refresco, necesario para la física y el movimiento
        self.running = True  # Variable para controlar el bucle del juego
        self.dt = 0  # Delta time, tiempo entre frames
        self.modos = {"menu":False, "jugar":True, "editor":False} #Fases de juego
        self.nivel = 0  # Nivel actual del juego (self.nivel = 0 significa que estamos en el primer nivel)
        self.lista_niveles = [nivel1, nivel2, nivel3, nivel4]  # Lista de niveles del juego (se pueden cargar desde un archivo o definirlos aquí)
        
        self.jugador = Jugador(ANCHO_PANTALLA//2, ALTO_PANTALLA//2, self.pantalla)  # Crea una instancia del jugador en la posición (0, 0) en la pantalla jugable
        self.lista_obstaculos = []  # Lista de obstáculos en el juego

    def cambio_modo(self, modo):
        pass

    def cambio_nivel(self):
        self.nivel += 1  # Incrementa el nivel actual del juego
        if self.nivel > len(self.lista_niveles):
            self.nivel = 0

    def teclas_presionadas(self):
        #  Usa un diccionario para determinar si sube, baja, si va para la derecha o izquierda
        movimientos_posibles = {
            K_w: (0, -(self.jugador.velocidad), "arriba"),  # Arriba
            K_s: (0, self.jugador.velocidad, "abajo"),     # Abajo
            K_a: (-(self.jugador.velocidad), 0, "izquierda"), # Izquierda
            K_d: (self.jugador.velocidad, 0, "derecha")     # Derecha
        }

        keys = key.get_pressed()
        for tecla in movimientos_posibles.keys():
            if keys[tecla]:  # Si la tecla está presionada
                dx, dy, direccion = movimientos_posibles[tecla]  # Obtiene el desplazamiento correspondiente
                self.jugador.movimiento(dx, dy, self.lista_obstaculos, direccion)  # Mueve al jugador en la dirección correspondiente

    def poner_bombas(self):
        if self.jugador.bombas > 0:  # Si se presiona espacio y el jugador tiene bombas
            self.jugador.bombas -= 1
            self.jugador.poner_bomba(self.lista_obstaculos)  # Lógica para colocar una bomba (debe implementarse en la clase Jugador)

    def actualizar(self):
        for evento in event.get():
            if evento.type == QUIT:
                self.running = False
            if evento.type == KEYDOWN:
                if evento.key == K_SPACE:
                    self.poner_bombas()
        self.teclas_presionadas()
        if time.get_ticks() - self.jugador.ultima_actualizacion_frame > 150:  # Si han pasado más de 100 ms desde la última actualización del sprite
            self.jugador.actualizar_frame_sprite()  # Actualiza el frame del sprite del jugador
            self.jugador.ultima_actualizacion_frame = time.get_ticks()  # Reinicia el tiempo de la última actualización del sprite
    
    def dibujar(self):
        if self.modos["jugar"]:  # Si estamos en el modo de juego
            for i in range(ANCHO_MATRIZ):
                for j in range(ALTO_MATRIZ):
                    # Dibuja el fondo de la pantalla
                    # Pantalla, color, posición (x, y), tamaño (ancho, alto)
                    if nivel1[j][i] == 0:  # Si el bloque es vacío
                        draw.rect(self.pantalla, (0, 255, 255), (16 + (i * MEDIDA_BLOQUE), MEDIDA_HUD + (j * MEDIDA_BLOQUE), MEDIDA_BLOQUE, MEDIDA_BLOQUE)) 
                    else:
                        # La comparación de la casilla con un número nos dice qué tipo de bloque es (destructible o indestructible)
                        obs = Obstaculo(16 + (i * MEDIDA_BLOQUE), MEDIDA_HUD + (j * MEDIDA_BLOQUE), nivel1[j][i] == 2)
                        self.lista_obstaculos.append(obs)  # Agrega el obstáculo a la lista de obstáculos
                        obs.colocar(self.pantalla)  # Dibuja el obstáculo en la pantalla

            self.jugador.dibujar_jugador(self.pantalla)  # Dibuja al jugador en la pantalla

        
    
    def run(self):
        while self.running:  # Bucle principal del juego
            display.flip()  # Actualiza la pantalla
            self.dt = self.clock.tick(FPS) / 1000  # Controla la tasa de refresco del juego

            self.actualizar()  # Actualiza el estado del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)
            self.dibujar()  # Dibuja los elementos del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)

                
# Ejecutar el juego
if __name__ == "__main__": #solo se ejecuta si se hace run, no si es import
    game = Game()
    game.run()





"""
# TODO:
# 0. Crear un sistema de Objetos (consumibles) y Power-ups (mejoras de estadisticas temporales)
# 1. Implementar la clase Enemigo con sus métodos de movimiento y ataque.
# 2. Implementar la clase Bomba con su temporizador y explosión.
# 3. Implementar la clase Obstaculos con diferentes tipos de obstáculos.
# 4. Implementar la clase Jefe con sus mecánicas de ataque y vida.
# 5. Implementar la clase Objetos con diferentes tipos de objetos coleccionables.
# 6. Crear un sistema de colisiones entre el jugador, enemigos, bombas y obstáculos.
# 7. Implementar un sistema de HUD para mostrar la vida del jugador, bombas restantes y puntaje.
# 8. Implementar un sistema de niveles
# 9. Implementar un sistema de guardados y almacenamiento de puntajes
# 10. Implementar un sistema de menús y opciones de configuración
# 11. Implementar un sistema de personalización del jugador (skins)
# 12. Implementar el menú principal, opciones, créditos y pantallas de fin de juego. 
"""
