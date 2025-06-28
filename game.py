# Módulos necesarios 
import pygame as pg
from jugar import Jugar
from menu import Menu
from ajustes import Ajustes
from info import Informacion
from puntajes import Puntajes
from config import *
from assets import cargar_canciones, cargar_fuentes

class Game: 
    def __init__(self):
        pg.init()  # Inicializamos Pygame
        
        self.pantalla = pg.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))  # Configura la ventana
        pg.display.set_caption("Wooly Warfare")  # Título de la ventana
        self.clock = pg.time.Clock()  # Crea un objeto de reloj para controlar la tasa de refresco, necesario para la física y el movimiento
        self.running = True  # Variable para controlar el bucle del juego
        self.dt = 0  # Delta time, tiempo entre frames
        
        # Configuraciones de la música
        self.canciones = cargar_canciones()
        self.musica = None  # Espera a tener una instancia de música
        self.volumen = VALOR_INCIAL_VOLUMEN  # Volumen inicial del juego
        
        self.fuentes = cargar_fuentes()
        self.fuente = self.fuentes[30]
        
        self.jugar = Jugar(self) #Crea una instancia del juego
        self.menu = Menu(self)  # Crea una instancia del menú
        self.ajustes = Ajustes(self)
        self.info = Informacion(self)
        self.puntajes = Puntajes(self)

        self.modo = self.menu #Inicia en el modo menu
        self.modo_previo = None #Guarda el modo previo, permite devolverse en el menu

        self.administrar_musica()  # Llama a la función para administrar la música del juego

    def dibujar_texto(self, texto, x, y, fuente, color=NEGRO):
        img = fuente.render(texto, True, color)
        self.pantalla.blit(img, (x, y))
    
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

    def administrar_musica(self):
        if self.musica != self.modo.musica:
            if self.musica is not None:  # Si es la primera vez que se llama, no hay música, entonces no haríamos nada
                self.musica.stop()
            self.musica = self.modo.musica
            self.musica.set_volume(self.volumen)  # Establece el volumen de la música
            self.musica.play(-1)  # Reproduce la música en bucle

    def cambiar_modo(self, modo):
        if modo == None:
            self.running = False
        else:
            self.modo_previo = modo
            self.modo = modo
            self.administrar_musica() #Cambia a la musica del modo respectivo
        
    
    def eventos(self):
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                self.running = False
            self.modo.eventos(evento) #Corre los eventos del modo activo
    
    def actualizar(self):
        self.modo.actualizar()


    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        self.modo.dibujar()
        
    def run(self):
        while self.running:  # Bucle principal del juego
            pg.display.flip()  # Actualiza la pantalla
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
# 1. Implementar la clase Enemigo con sus métodos de movimiento y ataque.
# 4. Implementar la clase Jefe con sus mecánicas de ataque y vida.
# 7. Implementar un sistema de HUD para mostrar la vida del jugador, bombas restantes y puntaje.
# 9. Implementar un sistema de guardados y almacenamiento de puntajes
# 11. Implementar un sistema de personalización del jugador (skins)
# 12. Implementar pantallas de fin de juego. 
# 13. Revisar todo lo que diga todo o pass
"""