# Módulos necesarios 
from pygame import *
from time import sleep

# Usaremos una definición HD (1280x720p)
# En la parte superior de la pantalla, dejaremos una HUD de tamaño 1280x192 
# Abajo del HUD, haremos matrices de 26x11 (siendo cada bloque de 48x48): esto nos dejará con 32 pixeles sobrantes, repartidos en 16 pixeles en la parte izquierda y 16 pixeles en la parte derecha de la pantalla
# Haremos los niveles con matrices (26x11), y como no se requiere crear nuevos, podemos ponerlos dentro del archivo de código

# Clase Jugador
class Jugador:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.bombas = 5
        self.vidas = 3
        self.velocidad = 5
        self.direccion = 'abajo'
        self.dano = 1
        self.rect = Rect(self.x, self.y, 50, 50)

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
    pass





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
