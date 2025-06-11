# Módulos necesarios 
from pygame import *
from time import sleep

# Usaremos una definición HD (1280x720p)
# En la parte superior de la pantalla, dejaremos una HUD de tamaño 1280x192 
# Abajo del HUD, haremos matrices de 26x11 (siendo cada bloque de 48x48): esto nos dejará con 32 pixeles sobrantes, repartidos en 16 pixeles en la parte izquierda y 16 pixeles en la parte derecha de la pantalla
# Haremos los niveles con matrices (26x11), y como no se requiere crear nuevos, podemos ponerlos dentro del archivo de código

MEDIDAS_PANTALLA = (1280, 720)  # Definimos el tamaño de la pantalla
ANCHO_BLOQUE = 48  # Ancho de cada bloque en píxeles
ANCHO_MATRIZ = 26  # Ancho de la matriz en bloques
ALTO_MATRIZ = 11  # Alto de la matriz en bloques

# pinga
#  fuente_texto = font.Font("assets/FUENTEJUEGO.TTF", 30)  # USAR PARA EL TEXTO DEL JUEGO


# Definiremos lo que significa cada bloque de la matriz:
# 0 = vacío
# 1 = bloque indestructible
# 2 = bloque destructible
 
# Las demás cosas que se colocan en la matriz son objetos que se generan aleatoriamente, y no se colocan en la matriz, sino que se generan en el momento de crear el nivel




nivel1 = "xd"



# Clase Jugador
class Jugador:
    def __init__(self, x, y, pantalla, skin):
        self.x = x  # Posición x del jugador
        self.y = y  # Posición y del jugador
        self.pantalla = pantalla  # Pantalla donde se dibuja el jugador
        self.skin = skin  # Skin del jugador (variable para personalización)
        self.bombas = 5  # Cantidad de bombas que el jugador puede colocar
        self.vidas = 3  # Cantidad de vidas del jugador
        self.velocidad = 5  # Velocidad de movimiento del jugador
        self.direccion = 'abajo'  # Dirección inicial del jugador (y a la que está mirando)
        self.hit = 1  # Daño que el jugador inflige (evitamos el uso de ñ)
        self.rect = Rect(self.x, self.y, 50, 50)  # Rectángulo que representa al jugador en el canvas (TEMPORAL, BORRAR DESPUÉS)

    def mover(self, dx, dy):
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad
        self.rect.topleft = (self.x, self.y)

    def dibujar_jugador(self, pantalla):
        draw.rect(pantalla, self.color, self.rect)



class Enemigo:
    pass



class Bomba:
    pass


class Obstaculos:
    pass


class Jefe:
    pass


class Objetos:
    pass




# Creamos una clase para el juego: esta llamará todas las opciones anteriores y las ejecutará en el orden correcto
class Game: 
    def __init__(self):
        init()  # Inicializamos Pygame
        self.pantalla = display.set_mode((MEDIDAS_PANTALLA[0], MEDIDAS_PANTALLA[1]))  # Configura la ventana
        display.set_caption("Bomberman")  # Título de la ventana
        self.clock = time.Clock()  # Crea un objeto de reloj para controlar la tasa de refresco, necesario para la física y el movimiento
        self.running = True  # Variable para controlar el bucle del juego


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


    def run(self):
        while self.running:  # Bucle principal del juego
            self.hadle_events()  # Maneja los eventos del juego (HACER)
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
