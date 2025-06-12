# Módulos necesarios 
from pygame import *
from time import sleep
from random import choice
from threading import Thread
from config import *


# Usaremos una definición HD (1280x720p)
# En la parte superior de la pantalla, dejaremos una HUD de tamaño 1280x192 
# Abajo del HUD, haremos matrices de 26x11 (siendo cada bloque de 48x48): esto nos dejará con 32 pixeles sobrantes, repartidos en 16 pixeles en la parte izquierda y 16 pixeles en la parte derecha de la pantalla
# Haremos los niveles con matrices (26x11), y como no se requiere crear nuevos, podemos ponerlos dentro del archivo de código

#  fuente_texto = font.Font("assets/FUENTEJUEGO.TTF", 30)  # USAR PARA EL TEXTO DEL JUEGO


# Definiremos lo que significa cada bloque de la matriz:
# 0 = vacío
# 1 = bloque indestructible
# 2 = bloque destructible
 
# Las demás cosas que se colocan en la matriz son objetos que se generan aleatoriamente, y no se colocan en la matriz, sino que se generan en el momento de crear el nivel



nivel1 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]



# Ideas de Items 
# Fantasmal -> Permite al jugador atravesar bloques destructibles/indestructibles por un tiempo limitado 
# Explosivo -> Aumenta el rango de las bombas del jugador por un tiempo limitado, además de no detenerse al contacto de un muro
# Freeze -> Congela a los enemigos por un tiempo limitado

# Clase Jugador
class Jugador:
    def __init__(self, x, y, pantalla, skin):
        self.x = x  # Posición x del jugador
        self.y = y  # Posición y del jugador
        self.pantalla = pantalla  # Pantalla donde se dibuja el jugador
        self.skin = skin  # Skin del jugador (variable para personalización)
        self.bombas = 5  # Cantidad de bombas que el jugador puede colocar
        self.vidas = 3  # Cantidad de vidas del jugador
        self.velocidad = 1  # Velocidad de movimiento del jugador (en bloques)
        self.direccion = 'abajo'  # Dirección inicial del jugador (y a la que está mirando)
        self.rect = Rect(self.x, self.y, 50, 50)  # Rectángulo que representa al jugador en el canvas (TEMPORAL, BORRAR DESPUÉS)

    #  Mueve al jugador en la dirección especificada
    def mover(self, dx, dy):
        # Cambia sus coords x y y
        self.x += dx 
        self.y += dy
        self.rect.topleft = (self.x, self.y)  # Actualiza la posición del rectángulo del jugador

    #  Dibuja al jugador en la pantalla
    def dibujar_jugador(self, pantalla):
        draw.rect(pantalla, self.color, self.rect)


# Clase Enemigo
class Enemigo:
    def __init__(self, x, y, pantalla):
        self.x = x
        self.y = y
        self.pantalla = pantalla
        self.vida = 1
        self.velocidad = 1
        self.direccion = 'abajo'
        self.rect = Rect(self.x, self.y, 50, 50)  # Rectángulo que representa al enemigo en el canvas (TEMPORAL, BORRAR DESPUÉS)

    # Mueve al enemigo en una dirección aleatoria
    def movimiento(self, obstaculos):
        # Genera un movimiento aleatorio
        movimientos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = choice(movimientos)
        new_x = self.x + dx  # Se calcula la nueva posición x
        new_y = self.y + dy  # Se calcula la nueva posición y
        if ANCHO_MATRIZ > new_x >= 0 and ALTO_MATRIZ > new_y >= 0:  # Si está dentro de los límites del mapa
            # Verifica si no hay obstáculos en la nueva posición
            if (new_x, new_y) not in [(obs.x, obs.y) for obs in obstaculos]:
                self.x = new_x
                self.y = new_y

        

class Bomba:
    def __init__(self, x, y):
        self.x = x  # Posición x de la bomba
        self.y = y  # Posición y de la bomba
        self.tiempo_detonar = 2  # Tiempo en segundos para que la bomba explote
        self.hit = 1 # Daño que causa la bomba al explotar
        Thread(target=self.detonar, args=([], [])).start()  # Inicia el temporizador de la bomba en un hilo separado

    def detonar(self, lista_obstaculos, enemigos):
        sleep(self.tiempo_detonar)
        



class Obstaculo:
    def __init__(self, x, y, destructible=False):
        self.x = x  # Posición x del obstáculo
        self.y = y  # Posición y del obstáculo
        self.destructible = destructible  # Si es destructible, puede ser destruido por una bomba

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
        
        self.jugador = Jugador(0, 0, self.pantalla)


    def key_pressed(self, event):
        #  Usa un diccionario para determinar si sube, baja, der, izq
        movimientos_posibles = {
            "K_w": (0, -1),
            "K_s": (0, 1),
            "K_a": (-1, 0),
            "K_d": (1, 0)
        }
        #  Si la tecla presionada está en el diccionario de movimientos posibles, se mueve el jugador
        if event.key in movimientos_posibles:
            dx, dy = movimientos_posibles[event.key]
            self.jugador.mover(dx, dy)
    
    def update(self):
        pass
    
    def draw(self):
        pass
    
    def run(self):
        while self.running:  # Bucle principal del juego
            self.update()  # Actualiza el estado del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)
            self.draw()  # Dibuja los elementos del juego (HACER, AGARRA LAS FUNCIONES DE CADA OBJETO Y LAS APLICA)

        

                
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
