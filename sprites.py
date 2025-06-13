import pygame as pg
from config import *

class Spritesheet:
    def __init__(self, path):
        self.sheet = pg.image.load(path)
    
    def getSprite(self, x, y, ancho, alto, escala=1):
        sprite = pg.Surface((ancho*escala, alto*escala)).convert_alpha()
        sprite.blit(self.sheet, (0, 0), (x, y, (x + ancho * escala), (y + alto * escala)))
        return sprite
    
hoja_sprites = Spritesheet("assets/spritesheet.png")

# Skin 1 (Paloma volando)
# Se escala por 3 cada sprite (si son de 16x16, quedan como 48x48, las medidas de un bloque)
# Sprites de arriba
skin1Up1 = hoja_sprites.getSprite(4*PIXELES_SPRITES, 17*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Up2 = hoja_sprites.getSprite(5*PIXELES_SPRITES, 17*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Up3 = hoja_sprites.getSprite(6*PIXELES_SPRITES, 17*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Up4 = hoja_sprites.getSprite(7*PIXELES_SPRITES, 17*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)

# Sprites de derecha
skin1Der1 = hoja_sprites.getSprite(4*PIXELES_SPRITES, 15*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Der2 = hoja_sprites.getSprite(5*PIXELES_SPRITES, 15*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Der3 = hoja_sprites.getSprite(6*PIXELES_SPRITES, 15*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Der4 = hoja_sprites.getSprite(7*PIXELES_SPRITES, 15*PIXELES_SPRITES, 3, PIXELES_SPRITES, PIXELES_SPRITES, 3)

"""
def player_skins():
    player1 = {
        "arriba": [sprite1, sprite2, sprite3, ...]
        "abajo": [sprite1, sprite2, sprite3, ...]
        "izquierda": [sprite1, sprite2, sprite3, ...]
        "derecha": [sprite1, sprite2, sprite3, ...]
    }
    
    player2 = 
    
    return player1, player2, player3, player4
"""