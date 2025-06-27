import pygame as pg
from config import *

class Spritesheet:
    def __init__(self, path):
        self.sheet = pg.image.load(path).convert_alpha()
    
    def cargar_sprite(self, x, y, ancho, alto, nuevo_ancho=None, nuevo_alto=None):
        nuevo_ancho = ancho if nuevo_ancho == None else nuevo_alto #Verifica si se inserto un nuevo anco, si no lo deja igual
        nuevo_alto = alto if nuevo_alto == None else nuevo_alto #Verica si se inserto un nuevo alto, si no, lo deja igual
        sprite = pg.Surface((ancho, alto), pg.SRCALPHA).convert_alpha() #Crea una pantalla para poner el sprite
        sprite.blit(self.sheet, (0,0), (x, y, ancho, alto)) #Dibuja el sprite en la pantalla creada
        sprite = pg.transform.scale(sprite, (nuevo_ancho, nuevo_alto))
        return sprite
    
# Diccionario con los puntos iniciales de cada skin en la hoja de sprites (x, y)
puntos_iniciales_skins_jugador = {1 : (0, 21), 2 : (4, 21), 3 : (8, 21)}
puntos_inciales_skins_enemigos = {1 : (0, 24), 2 : (4, 24), 3 : (8, 24), 4 : (12, 24), 5 : (0, 27), 6 : (4, 27)}

# Carga una skin completa a partir de su número, devolviendo una lista de sprites (derecha, abajo, arriba, izquierda)
def cargar_skins(numero_skin, dict):
    sprites_jugador = Spritesheet("assets/spritesheet.png")
    inicio_x, inicio_y = dict[numero_skin]
    skin = {"derecha": [], "abajo": [], "arriba": [], "izquierda": []}
    
    direcciones = ["derecha", "abajo", "arriba"]
    
    # Por cada dirección (en orden), tomamos una fila de 4 sprites
    for idx, direccion in enumerate(direcciones):
        for i in range(4):  # 4, ya que cada dirección tiene 4 sprites
            # Sacamos el (x, y) de la hoja de sprites
            x = (inicio_x + i) * PIXELES_SPRITES
            y = (inicio_y + idx) * PIXELES_SPRITES
            # y = ((inicio_y + idx) * PIXELES_SPRITES) if dict == puntos_inciales_skins_enemigos or direccion == "arriba" else ((inicio_y + idx) * PIXELES_SPRITES + 2)  # Si se quiere algo más preciso
            sprite = sprites_jugador.cargar_sprite(x, y, PIXELES_SPRITES, PIXELES_SPRITES, MEDIDA_BLOQUE, MEDIDA_BLOQUE)        
            sprite.set_colorkey((0, 0, 0))
            skin[direccion].append(sprite)

    # Para la izquierda, sacamos el reflejo horizontal de derecha
    for sprite_derecha in skin["derecha"]:
        sprite_izquierda = pg.transform.flip(sprite_derecha, True, False)
        skin["izquierda"].append(sprite_izquierda)

    return skin


def cargar_bloques(nivel):
    niveles = {1: "assets/niveles/spritesheet_normal.png",
              2: "assets/niveles/spritesheet_playa.png",
              3: "assets/niveles/spritesheet_hielo.png",
              4: "assets/niveles/spritesheet_castillo.png"}

    sprites_niveles = Spritesheet(niveles[nivel])  # Los bloques del nivel 1 son de 160x160 y los del nivel 2 en adelante son de 32x32
    medida = (160 if nivel == 1 else 32)  # Usamos 1 para el primer nivel y 2 para los demás
    vacio = sprites_niveles.cargar_sprite(2*medida, 0, medida, medida, MEDIDA_BLOQUE, MEDIDA_BLOQUE) # Bloque vacío
    return {
        0:vacio,  # Bloque vacío
        1:sprites_niveles.cargar_sprite(1*medida, 0, medida, medida, MEDIDA_BLOQUE, MEDIDA_BLOQUE),  # Bloque solido
        2:sprites_niveles.cargar_sprite(0, 0, medida, medida, MEDIDA_BLOQUE, MEDIDA_BLOQUE),  # Ladrilo rompible
        3:vacio  # Bloque vacío pero con hitbox, usado para que la bomba tenga colision
    }

def cargar_bomba():
    sprites_bomba = Spritesheet("assets/spritesheet_bomba.png")
    return {
        "bomba":[sprites_bomba.cargar_sprite(0, 0, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                 sprites_bomba.cargar_sprite(0, 160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                 sprites_bomba.cargar_sprite(0, 2*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE)],
        
        "centro":[sprites_bomba.cargar_sprite(3*160, 5*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                  sprites_bomba.cargar_sprite(3*160, 4*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                  sprites_bomba.cargar_sprite(3*160, 3*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                  sprites_bomba.cargar_sprite(3*160, 2*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                  sprites_bomba.cargar_sprite(3*160, 160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                  sprites_bomba.cargar_sprite(3*160, 0, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE)],
        
        "izquierda":[a0 := sprites_bomba.cargar_sprite(2*160, 3*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                     a1 := sprites_bomba.cargar_sprite(2*160, 2*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                     a2 := sprites_bomba.cargar_sprite(2*160, 160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                     a3 := sprites_bomba.cargar_sprite(2*160, 0, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE)],
        
        "derecha":[pg.transform.rotate(a0, 180),
                   pg.transform.rotate(a1, 180),
                   pg.transform.rotate(a2, 180),
                   pg.transform.rotate(a3, 180)],
        
        "arriba":[pg.transform.rotate(a0, 90),
                  pg.transform.rotate(a1, 90),
                  pg.transform.rotate(a2, 90),
                  pg.transform.rotate(a3, 90)],
        
        "abajo":[pg.transform.rotate(a0, -90),
                 pg.transform.rotate(a1, -90),
                 pg.transform.rotate(a2, -90),
                 pg.transform.rotate(a3, -90)],
        
        "punta_izquierda":[b0 := sprites_bomba.cargar_sprite(160, 3*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                           b1 := sprites_bomba.cargar_sprite(160, 2*160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                           b2 := sprites_bomba.cargar_sprite(160, 160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
                           b3 := sprites_bomba.cargar_sprite(160, 0, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE)],
        
        "punta_derecha":[pg.transform.rotate(b0, 180),
                         pg.transform.rotate(b1, 180),
                         pg.transform.rotate(b2, 180),
                         pg.transform.rotate(b3, 180)],
        
        "punta_arriba":[pg.transform.rotate(b0, -90),
                        pg.transform.rotate(b1, -90),
                        pg.transform.rotate(b2, -90),
                        pg.transform.rotate(b3, -90)],
        
        "punta_abajo":[pg.transform.rotate(b0, 90),
                       pg.transform.rotate(b1, 90),
                       pg.transform.rotate(b2, 90),
                       pg.transform.rotate(b3, 90)],
    }
    
def cargar_pociones():
    sprites_pociones = Spritesheet("assets/spritesheet_pociones.png")
    return {
        "velocidad": sprites_pociones.cargar_sprite(0, 0, 16, 16, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
        "invulnerabilidad": sprites_pociones.cargar_sprite(16, 0, 16, 16, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
    }

def cargar_caramelos():
    sprites_caramelos = Spritesheet("assets/spritesheet_caramelos.png")
    return {
        "daño": sprites_caramelos.cargar_sprite(0, 0, 16, 16, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
        "rango": sprites_caramelos.cargar_sprite(16, 0, 16, 16, MEDIDA_BLOQUE, MEDIDA_BLOQUE),
        "vida": sprites_caramelos.cargar_sprite(32, 0, 16, 16, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
    }

def cargar_logo():
    return pg.transform.scale(pg.image.load("assets/logo.png").convert_alpha(),
                              (448, 448)) #512x512 pixeles
def cargar_canciones():
    return [
        pg.mixer.Sound("assets/musica/MusicaMenu.mp3"),  # Carga la música del menú
        pg.mixer.Sound("assets/musica/MusicaJuego.mp3"),  # Carga la música del juego
        pg.mixer.Sound("assets/musica/MusicaResultados.mp3")  # Carga la música de los resultados
    ]

def cargar_gameover():
    return pg.transform.scale(pg.image.load("assets/gameover.jpg").convert_alpha(),
                              (ANCHO_PANTALLA, ALTO_PANTALLA))  # Ajusta el tamaño a la pantalla del juego

def cargar_llave():
    return pg.transform.scale(pg.image.load("assets/llave.png").convert_alpha(),
                                (MEDIDA_BLOQUE, MEDIDA_BLOQUE))  # Ajusta el tamaño de la llave

def cargar_puerta():
    return pg.transform.scale(pg.image.load("assets/puerta.png").convert_alpha(),
                                (MEDIDA_BLOQUE, MEDIDA_BLOQUE))  # Ajusta el tamaño de la puerta

def cargar_pegamento():
    return pg.transform.scale(pg.image.load("assets/pegamento.png").convert_alpha(),
                                (MEDIDA_BLOQUE, MEDIDA_BLOQUE))  # Ajusta el tamaño del pegamento

def cargar_veneno():
    return pg.transform.scale(pg.image.load("assets/veneno.png").convert_alpha(),
                                (MEDIDA_BLOQUE, MEDIDA_BLOQUE))  # Ajusta el tamaño del veneno