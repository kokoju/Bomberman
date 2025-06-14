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
skin1Izq1 = pg.transform.flip(skin1Der1, True, False)  
skin1Izq2 = pg.transform.flip(skin1Der2, True, False)
skin1Izq3 = pg.transform.flip(skin1Der3, True, False)
skin1Izq4 = pg.transform.flip(skin1Der4, True, False)

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


# Skin 2 (Gaviota volando)
# Sprites de derecha
skin2Der1 = hoja_sprites.getSprite(12*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Der2 = hoja_sprites.getSprite(13*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Der3 = hoja_sprites.getSprite(14*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Der4 = hoja_sprites.getSprite(15*PIXELES_SPRITES, 15*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)

# Sprites de izquierda (imagenes de la derecha giradas 180 grados)
# El True hace que se invierta horizontalmente (el eje X), mientras que el False no invierte verticalmente (el eje Y)
skin2Izq1 = pg.transform.flip(skin2Der1, True, False)  
skin2Izq2 = pg.transform.flip(skin2Der2, True, False)
skin2Izq3 = pg.transform.flip(skin2Der3, True, False)
skin2Izq4 = pg.transform.flip(skin2Der4, True, False)

# Sprites de abajo
skin2Down1 = hoja_sprites.getSprite(12*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Down2 = hoja_sprites.getSprite(13*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Down3 = hoja_sprites.getSprite(14*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Down4 = hoja_sprites.getSprite(15*PIXELES_SPRITES, 16*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)

# Sprites de arriba
skin2Up1 = hoja_sprites.getSprite(12*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Up2 = hoja_sprites.getSprite(13*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Up3 = hoja_sprites.getSprite(14*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)
skin2Up4 = hoja_sprites.getSprite(15*PIXELES_SPRITES, 17*PIXELES_SPRITES, PIXELES_SPRITES, PIXELES_SPRITES, 3)


def player_skins():
    skin1 = {
        "derecha": [skin1Der1, skin1Der2, skin1Der3, skin1Der4],
        "izquierda": [skin1Izq1, skin1Izq2, skin1Izq3, skin1Izq4],
        "abajo": [skin1Down1, skin1Down2, skin1Down3, skin1Down4],
        "arriba": [skin1Up1, skin1Up2, skin1Up3, skin1Up4]
    }

    skin2 = {
        "derecha": [skin2Der1, skin2Der2, skin2Der3, skin2Der4],
        "izquierda": [skin2Izq1, skin2Izq2, skin2Izq3, skin2Izq4],
        "abajo": [skin2Down1, skin2Down2, skin2Down3, skin2Down4],
        "arriba": [skin2Up1, skin2Up2, skin2Up3, skin2Up4]
    }

    for direccion in skin1.values():
        for elemento in direccion:
            elemento.set_colorkey((0, 0, 0))
    
    return [skin1, skin2] #, etc. si se agregan más skins
