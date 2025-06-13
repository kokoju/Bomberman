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

# Skin 1 (Paloma volando)
# Se escala por 3 cada sprite (si son de 16x16, quedan como 48x48, las medidas de un bloque)
# Sprites de derecha
skin1Der1 = hoja_sprites.getSprite(4*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Der2 = hoja_sprites.getSprite(5*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Der3 = hoja_sprites.getSprite(6*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Der4 = hoja_sprites.getSprite(7*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)

# Sprites de izquierda (imagenes de la derecha giradas 180 grados)
# El True hace que se invierta horizontalmente (el eje X), mientras que el False no invierte verticalmente (el eje Y)
skinIzq1 = pg.transform.flip(skin1Der1, True, False)  
skinIzq2 = pg.transform.flip(skin1Der2, True, False)
skinIzq3 = pg.transform.flip(skin1Der3, True, False)
skinIzq4 = pg.transform.flip(skin1Der4, True, False)

# Sprites de abajo
skin1Down1 = hoja_sprites.getSprite(4*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Down2 = hoja_sprites.getSprite(5*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Down3 = hoja_sprites.getSprite(6*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Down4 = hoja_sprites.getSprite(7*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)

# Sprites de arriba
skin1Up1 = hoja_sprites.getSprite(4*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Up2 = hoja_sprites.getSprite(5*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Up3 = hoja_sprites.getSprite(6*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin1Up4 = hoja_sprites.getSprite(7*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)


def player_skins():
    skin1 = {
        "derecha": [skin1Der1, skin1Der2, skin1Der3, skin1Der4],
        "izquierda": [skinIzq1, skinIzq2, skinIzq3, skinIzq4],
        "abajo": [skin1Down1, skin1Down2, skin1Down3, skin1Down4],
        "arriba": [skin1Up1, skin1Up2, skin1Up3, skin1Up4]
    }
    
    # skin2 = 
    
    return skin1  #, skin2, etc. si se agregan más skins
