import pygame as pg
from config import *

class Spritesheet:
    def __init__(self, path):
        self.sheet = pg.image.load(path)
    
    def getSprite(self, x, y, ancho, alto, escala=1):
        sprite = pg.Surface((ancho, alto))
        sprite.blit(self.sheet, (0, 0), (x, y, (x + PIXELES_SPRITES), (y + PIXELES_SPRITES)))
        sprite = pg.transform.scale(sprite, (ancho * escala, alto * escala))
        return sprite
    
hoja_sprites = Spritesheet("assets/spritesheet.png")

<<<<<<< HEAD
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
    
    player2 = {}
    player3 = {}
    player4 = {}
=======
# SE PUEDE AUTOMATIZAR LA CARGA DE SPRITES: SI SE DA CUENTA, SIGUEN UN PATRON COMO RECORRER CON 2 FORs, HACER UN DICCIONARIO CON LAS COSAS INICIALES DE CADA SKIN, Y SUMARLE HASTA 4 EN LA I

# Diccionario con los puntos iniciales de cada skin en la hoja de sprites (x, y)
puntos_iniciales_skins_jugador = {1 : (0, 21), 2 : (4, 21), 3 : (8, 21)}
puntos_inciales_skins_enemigos = {1 : (0, 24), 2 : (4, 24), 3 : (8, 24), 4 : (12, 24), 5 : (0, 27), 6 : (4, 27)}

# Carga una skin completa a partir de su número, devolviendo una lista de sprites (derecha, abajo, arriba, izquierda)
def cargar_skins(numero_skin, dict):
    inicio_x, inicio_y = dict[numero_skin]
    skin = {"derecha": [], "abajo": [], "arriba": [], "izquierda": []}
    
    direcciones = ["derecha", "abajo", "arriba"]
>>>>>>> 297755588a32d96c71bfb4234ede4d311924a500
    
    # Por cada dirección (en orden), tomamos una fila de 4 sprites
    for idx, direccion in enumerate(direcciones):
        for i in range(4):  # 4, ya que cada dirección tiene 4 sprites
            # Sacamos el (x, y) de la hoja de sprites
            x = (inicio_x + i) * PIXELES_SPRITES
            y = (inicio_y + idx) * PIXELES_SPRITES
            sprite = hoja_sprites.getSprite(x, y, PIXELES_SPRITES, PIXELES_SPRITES, 3)
            sprite.set_colorkey((0, 0, 0))
            skin[direccion].append(sprite)

    # Para la izquierda, sacamos el reflejo horizontal de derecha
    for sprite_derecha in skin["derecha"]:
        sprite_izquierda = pg.transform.flip(sprite_derecha, True, False)
        skin["izquierda"].append(sprite_izquierda)

    return skin
