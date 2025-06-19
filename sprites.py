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
    

"""
def player_skins():
    player1 = {
        "arriba": [sprite1, sprite2, sprite3...],
        "abajo": [sprite1, sprite2, sprite3...],
        "izquierda": [sprite1, sprite2, sprite3...],
        "derecha": [sprite1, sprite2, sprite3...]
    },
    
    player1 = {
        "arriba": [sprite1, sprite2, sprite3...],
        "abajo": [sprite1, sprite2, sprite3...],
        "izquierda": [sprite1, sprite2, sprite3...],
        "derecha": [sprite1, sprite2, sprite3...]
    },
    player3 = {
        "arriba": [sprite1, sprite2, sprite3...],
        "abajo": [sprite1, sprite2, sprite3...],
        "izquierda": [sprite1, sprite2, sprite3...],
        "derecha": [sprite1, sprite2, sprite3...]
    },
    player4 = {
        "arriba": [sprite1, sprite2, sprite3...],
        "abajo": [sprite1, sprite2, sprite3...],
        "izquierda": [sprite1, sprite2, sprite3...],
        "derecha": [sprite1, sprite2, sprite3...]
    }
"""
# SE PUEDE AUTOMATIZAR LA CARGA DE SPRITES: SI SE DA CUENTA, SIGUEN UN PATRON COMO RECORRER CON 2 FORs, HACER UN DICCIONARIO CON LAS COSAS INICIALES DE CADA SKIN, Y SUMARLE HASTA 4 EN LA I

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
            sprite = sprites_jugador.cargar_sprite(x, y, PIXELES_SPRITES, PIXELES_SPRITES, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
            sprite.set_colorkey((0, 0, 0))
            skin[direccion].append(sprite)

    # Para la izquierda, sacamos el reflejo horizontal de derecha
    for sprite_derecha in skin["derecha"]:
        sprite_izquierda = pg.transform.flip(sprite_derecha, True, False)
        skin["izquierda"].append(sprite_izquierda)

    return skin


def cargar_bloques():
    sprites_niveles = Spritesheet("assets/tiles_niveles.png")
    return {
        0:sprites_niveles.cargar_sprite(5*160, 160, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE), #Zacate
        1:sprites_niveles.cargar_sprite(2*160, 0, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE), #Bloque solido
        2:sprites_niveles.cargar_sprite(0, 0, 160, 160, MEDIDA_BLOQUE, MEDIDA_BLOQUE) #Ladrilo rompible
    }
