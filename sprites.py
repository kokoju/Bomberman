import pygame as pg

class Spritesheet:
    def __init__(self, path):
        self.sheet = pg.image.load(path).convert_alpha()
    
    def getSprite(self, x, y, width, height, scale=1):
        sprite = pg.Surface((width*scale, height*scale))
        sprite.blit(self.sheet, (0, 0), (x, y, width*scale, height*scale))
        return sprite
    
spritesheet_jugadores = Spritesheet("assets/jugadores")

def player_skins():
    player1 = {
        "arriba": [sprite1, sprite2, sprite3...]
        "abajo": [sprite1, sprite2, sprite3...]
        "izquierda": [sprite1, sprite2, sprite3...]
        "derecha": [sprite1, sprite2, sprite3...]
    }
    
    player2 = 
    
    return player1, player2, player3, player4