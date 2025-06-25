# Módulos necesarios 
from pygame import *  # Importa todos los módulos de Pygame necesarios para el juego
from time import sleep  # Importa sleep para manejar los Threads
from random import choice, randint  # Importa choice para seleccionar elementos aleatorios de listas (movimiento enemigo)
from threading import Thread  # Importa los Threads para el manejo de entidades en paralelo
from config import *  # Importa las configuraciones del juego, como dimensiones y FPS
from assets import *  # Importa los sprites del jugador y otros elementos visuales
from niveles import *

# Usaremos una definición HD (1280x720p)
# En la parte superior de la pantalla, dejaremos una HUD de tamaño 1280x176 
# Abajo del HUD, haremos matrices de 11x26 (siendo cada bloque de 48x48): esto nos dejará con 32 pixeles sobrantes, repartidos en 16 pixeles en la parte izquierda y 16 pixeles en la parte derecha de la pantalla
# Además, dejé un espacio de 16 pixeles entre la matriz y el borde inferior, para que no se vea tan pegado
# Haremos los niveles con matrices (11x26), y como no se requiere crear nuevos, podemos ponerlos dentro del archivo de código

font.init()  # Inicializa el módulo de fuentes de Pygame
fuente_texto = font.Font("assets/FuenteTexto.ttf", 30)  # Tipografía del texto del juego

# Clase Jugador
class Jugador:
    def __init__(self, jugar, num_skin=1):
        self.jugar = jugar
        self.pantalla = jugar.pantalla_juego  # Pantalla donde se dibuja el jugador
        self.nivel = jugar.nivel  # Nivel actual del jugador (se usa para verificar colisiones)

        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = num_skin  # Número de skin del jugador (se puede cambiar para personalizar el jugador)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_iniciales_skins_jugador)  # Carga la skin del jugador desde la hoja de sprites

        self.direccion = "abajo"  # Dirección inicial del jugador (y a la que está mirando)
        self.frame = 0  # Frame actual del sprite del jugador
        self.sprite = self.skin_hoja_sprites[self.direccion][self.frame] #Sprite inicial del jugador
        
        self.vidas = 10
        self.bombas = 10
        self.velocidad = 5  # Velocidad de movimiento del jugador (en pixeles)
        self.golpe = GOLPE_INICIAL_BOMBA  # Daño que causa el jugador al explotar una bomba
        self.rango = 1 #Rango inicial de la bomba
        self.moviendose = False  # Indica si el jugador se está moviendo o no
        
        self.puntaje = 0  # Puntaje del jugador

        # Habilidades e ítems del jugador
        self.tiene_habilidad = True  # Indica si el jugador tiene la habilidad especial
        self.tiene_item_1 = False  # Indica si el jugador tiene el item 1
        self.tiene_item_2 = False  # Indica si el jugador tiene el item 2

        self.enfriamiento_habilidad = ENFRIAMIENTO_HABILIDAD  # Tiempo de enfriamiento de la habilidad especial (en milisegundos)

        self.tiene_llave = False  # Indica si el jugador tiene la llave para abrir la puerta del siguente nivel

        self.rect = Rect(X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR, ANCHO_JUGADOR, ALTO_JUGADOR) #  Rectangulo del jugador para posicion y colision
        
        self.invulnerable = False
        self.invulnerabilidad() #Inicia invulnerable
        
    def sacar_esquinas(self, rect):
        #Hay un offset de 1 porque hay un borde no visible de bloques solidos
        return (
            (izq := rect.left // MEDIDA_BLOQUE+1, arriba := rect.top // MEDIDA_BLOQUE+1), #Superior izquierda
            (izq, abajo := rect.bottom // MEDIDA_BLOQUE+1), #Inferior izquierda
            (der := rect.right // MEDIDA_BLOQUE+1, arriba), #Superior derecha
            (der, abajo) #Inferior derecha
        )
        
    def verificar_colision(self, rect):
        #Verifica si alguna esquina esta en un tile que no sea aire
        for x, y in self.sacar_esquinas(rect):
            if self.nivel[y][x] != 0:
                return False
        return True
    
    def actualizar(self):
        keys = pg.key.get_pressed()
        dx, dy = 0, 0
        if any(self.rect.colliderect(el.rect) for el in self.jugar.lista_pegamento):  # Si el jugador colisiona con el pegamento
            velocidad = RALENTIZACION_PEGAMENTO * self.velocidad  # Reduce la velocidad del jugador al pisar el pegamento
        else:
            velocidad = self.velocidad  # Velocidad normal del jugador
        # Saca el input del usuario
        self.moviendose = False
        self.movimientos_posibles = {
            K_w: (0, -(velocidad), "arriba"),  # Arriba
            K_s: (0, velocidad, "abajo"),     # Abajo
            K_a: (-(velocidad), 0, "izquierda"), # Izquierda
            K_d: (velocidad, 0, "derecha")     # Derecha
        }

        for tecla in self.movimientos_posibles.keys():
            if keys[tecla]:
                self.moviendose = True
                tx, ty, self.direccion = self.movimientos_posibles[tecla]    
                # Se suman para que no se reemplazen en el for por 0 (en caso de movimiento diagonal)
                dx += tx
                dy += ty  
        
        # Movimiento del jugador
        # Si está dentro de los límites del mapa y camina en aire
        rect_dx, rect_dy = self.rect.move(dx, 0), self.rect.move(0, dy)
        # Verifica los ejes independientemente para mantener deslizamiento en muros con movimiento diagonal
        if self.verificar_colision(rect_dx):
            self.rect = self.rect.move(dx, 0)
        if self.verificar_colision(rect_dy):
            self.rect = self.rect.move(0, dy)
    
        # Animación
        if time.get_ticks() - self.ultima_actualizacion_frame > 150:  # Si el jugador se está moviendo y han pasado 150ms
            self.actualizar_frame_sprite()  # Actualiza el frame del sprite del jugador
            self.ultima_actualizacion_frame = time.get_ticks()  # Reinicia el tiempo de la última actualización del sprite
                   
    def actualizar_frame_sprite(self):
        if self.moviendose: # Jugador se mueve
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.skin_hoja_sprites) # Frame ciclico, se reinicia cuando llega al final
        else: # Jugador no se mueve
            self.frame = 0 # Reinicia
        self.sprite = self.skin_hoja_sprites[self.direccion][self.frame]


    def dibujar(self):
        if self.jugar.debug:
            # Dibuja la hitbox del jugador
            draw.rect(self.pantalla, ROJO, self.rect, 2)
            
        if self.invulnerable and time.get_ticks() % 200 < 100:
            return  # No dibujar el sprite en este frame (parpadeo)
 
        self.pantalla.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))  # Dibuja el sprite del jugador

    def poner_bomba(self):
        if not self.invulnerable and self.bombas > 0:
            bx = self.rect.centerx//MEDIDA_BLOQUE+1
            by = self.rect.centery//MEDIDA_BLOQUE+1
            for bomba in self.jugar.capas[2]: # No poner bombas encima de otras
                if (bomba.bx, bomba.by) == (bx, by):
                    return
                
            self.bombas -= 1
            Bomba(self)

    # TODO
    # Fantasmal (Oveja común) -> Permite al jugador atravesar bloques destructibles/indestructibles por un tiempo limitado 
    # Explosivo (Oveja albina) -> Aumenta el rango de las bombas del jugador por un tiempo limitado, además de no detenerse al contacto de un muro
    # Freeze (Oveja rosada) -> Congela a los enemigos por un tiempo limitado
    def habilidad(self):
        pass

    def item1(self):
        if self.tiene_item_1:
            self.tiene_item_1 = False  # Desactiva la bandera de la habilidad 1
            self.velocidad += 10

            def restaurar():
                sleep(5)  # Espera 5 segundos
                self.velocidad -= 10  # Vuelve a la velocidad normal

            hilo = Thread(target=restaurar)  # Se crea un hilo para restaurar la velocidad
            hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
            hilo.start()  # Inicia el hilo
    
    def item2(self):
        if self.tiene_item_2:
            self.tiene_item_2 = False  # Desactiva la bandera de la habilidad 2
            self.invulnerable = True  # Activa la invulnerabilidad

            def restaurar():
                sleep(5)  # Espera 5 segundos
                self.invulnerable = False  # Vuelve a la normalidad

            hilo = Thread(target=restaurar)  # Se crea un hilo para restaurar la velocidad
            hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
            hilo.start()  # Inicia el hilo
    
    def morir(self):
        if self.vidas > 0:
            self.vidas -= 1  # Cada golpe (de bomba o enemigo) resta uno de vida (hecho así para que castigue menos si la bomba tiene más daño)
            hilo = Thread(target=self.invulnerabilidad)
            hilo.daemon = True
            hilo.start()
        else:
            self.game_over = GameOver(self.jugar.pantalla)  # Si no tiene vidas, se muestra la pantalla de Game Over
    
    def invulnerabilidad(self):
        self.invulnerable = True
        sleep(1.5)
        self.invulnerable = False
    
    def eventos(self, evento):
        if evento.type == KEYDOWN:
            if evento.key == K_SPACE: #Si le da a espacio
                self.poner_bomba()

            if evento.key == K_1: #Si le da a 1
                self.habilidad1()
                
            elif evento.key == K_2: #O si le da a 2
                self.habilidad2()

class GameOver:
    def __init__(self, pantalla):
        self.pantalla = pantalla  # Pantalla donde se dibuja la pantalla de Game Over
        self.imagen = cargar_gameover()

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla con un color
        self.pantalla.blit(self.imagen, (0, 0))  # Dibuja la pantalla de Game Over
        


class Enemigo:
    def __init__(self, jugar, x, y):
        self.jugar = jugar
        self.jugador = jugar.jugador
        self.pantalla = jugar.pantalla_juego
        self.nivel = jugar.nivel
        self.x = x
        self.y = y

        self.frame = 0
        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = 1  # Número de skin del enemigo (se puede cambiar para hacerlo más complicado)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_inciales_skins_enemigos)  # Carga la skin del enemigo desde la hoja de sprites
        self.vidas = 1
        self.velocidad = 2
        self.rect = Rect(self.x, self.y, int(MEDIDA_BLOQUE*0.75), int(MEDIDA_BLOQUE*0.75))  # Rectángulo que representa al enemigo en el canvas (uso para colisiones)
        self.movimientos = {"arriba" : (0, -self.velocidad), "abajo" : (0, self.velocidad), "izquierda" : (-self.velocidad, 0), "derecha" : (self.velocidad, 0)}  # Diccionario con los movimientos posibles
        self.movimiento_elegido = choice(list(self.movimientos.keys()))  # Elige un movimiento aleatorio del diccionario
        self.sprite = self.skin_hoja_sprites[self.movimiento_elegido][self.frame] #Sprite inicial del enemigo
        
        self.moviendose = False

    # Mueve al enemigo en una dirección aleatoria
    def actualizar(self):
        self.soltar_pegamento()  # Si el enemigo puede soltar pegamento, lo hace
        dx, dy = self.movimientos[self.movimiento_elegido]
        # Movimiento en eje X
        rect_dx = self.rect.move(dx, 0)
        if self.verificar_colision(rect_dx):  # Si puede moverse
            self.rect = rect_dx
            self.x = self.rect.x
            self.y = self.rect.y
        else:
            self.movimiento_elegido = choice(list(self.movimientos.keys()))
            return  # Sale para que el nuevo movimiento se intente en el siguiente frame

        # Movimiento en eje Y
        rect_dy = self.rect.move(0, dy)
        if self.verificar_colision(rect_dy):  # Si puede moverse
            self.rect = rect_dy
            self.x = self.rect.x
            self.y = self.rect.y
        else:
            self.movimiento_elegido = choice(list(self.movimientos.keys()))

        self.actualizar_frame_sprite()  # Actualiza el frame del sprite del enemigo
        if not self.jugador.invulnerable and self.rect.colliderect(self.jugador.rect):
            self.jugador.morir()

    
    def verificar_colision(self, rect):
        #Hay un offset de 1 porque hay un borde no visible de bloques solidos
        esquinas = (
            (izq := rect.left // MEDIDA_BLOQUE+1, arriba := rect.top // MEDIDA_BLOQUE+1), #Superior izquierda
            (izq, abajo := rect.bottom // MEDIDA_BLOQUE+1), #Inferior izquierda
            (der := rect.right // MEDIDA_BLOQUE+1, arriba), #Superior derecha
            (der, abajo) #Inferior derecha
        )
        
        #Verifica si alguna esquina esta en un tile que no sea aire
        for x, y in esquinas:
            if self.nivel[y][x] != 0: #Si no es aire
                return False
            for bomba in self.jugar.capas[2]: #Verificar si hay una bomba
                if (x, y) == (bomba.bx, bomba.by):
                    return False
        return True
    
    def actualizar_frame_sprite(self):
        if time.get_ticks() - self.ultima_actualizacion_frame > 150:  # Si el enemigo se está moviendo y han pasado 150ms
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.skin_hoja_sprites) # Frame ciclico, se reinicia cuando llega al final
        self.sprite = self.skin_hoja_sprites[self.movimiento_elegido][self.frame]

    def soltar_pegamento(self):
        pos = (self.rect.centerx // MEDIDA_BLOQUE + 1, self.rect.centery // MEDIDA_BLOQUE + 1)
        posiciones_pegamento = [(el.bx, el.by) for el in self.jugar.lista_pegamento]
        if pos not in posiciones_pegamento:
            print("Soltando pegamento en", pos)
            pegamento = Pegamento(self)  # Crea un pegamento si no hay uno en la misma posición
            self.jugar.lista_pegamento.append(pegamento)
            print(len(self.jugar.lista_pegamento))

    #  Dibuja al enemigo en la pantalla
    def dibujar(self):
        self.pantalla.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))
        

class Pegamento:  # Los enemigos más avanzados sueltan pegamento al moverse, que ralentiza al jugador
    def __init__(self, enemigo):
        self.jugar = enemigo.jugar
        self.pantalla = enemigo.pantalla
        self.bx = enemigo.rect.centerx//MEDIDA_BLOQUE+1 #Bloque en x
        self.by = enemigo.rect.centery//MEDIDA_BLOQUE+1 #Bloque en y
        self.x = (self.bx-1) * MEDIDA_BLOQUE #X en pixeles
        self.y = (self.by-1) * MEDIDA_BLOQUE #Y en pixeles
        self.rect = Rect(self.x, self.y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al pegamento en el canvas
        self.sprite = cargar_pegamento()  # Carga la skin del pegamento desde la hoja de sprites
        self.activo = True  # Indica si el pegamento está activo
        self.tiempo_creacion = pg.time.get_ticks()  # Tiempo de creación del pegamento
        self.hilo = Thread(target=self.duracion)  # Crea un hilo para actualizar el pegamento
        self.hilo.daemon = True  # Daemon para que se cierre al cerrar el juego
        self.hilo.start()

    def actualizar(self):
        pass

    def duracion(self):
        sleep(PEGAMENTO_DURACION / 1000) 
        self.activo = False  # Desactiva el pegamento después de un tiempo
        self.jugar.lista_pegamento.remove(self)

    def dibujar(self):

        self.pantalla.blit(self.sprite, (self.x, self.y)) #Dibuja el sprite


class Bomba:
    def __init__(self, jugador):
        self.rango = jugador.rango
        self.jugar = jugador.jugar
        self.jugador = jugador
        self.pantalla = jugador.pantalla
        self.bx = jugador.rect.centerx//MEDIDA_BLOQUE+1 #Bloque en x
        self.by = jugador.rect.centery//MEDIDA_BLOQUE+1 #Bloque en y
        self.x = (self.bx-1) * MEDIDA_BLOQUE #X en pixeles
        self.y = (self.by-1) * MEDIDA_BLOQUE #Y en pixeles
        self.sprites = self.jugar.sprites_bomba
        
        self.tiempo_creacion = pg.time.get_ticks()
        self.ultima_actualizacion_frame = self.tiempo_creacion
        self.frame = 0
        self.sprite = self.sprites["bomba"][0]
        self.tiempo_detonar = 2000  # Tiempo en ms para que la bomba explote
        self.golpe = jugador.golpe # Daño que causa la bomba al explotar
        self.activa = True
        self.hitbox_activa = False #Se activa cuando el jugador se mueve fuera de la bomba
        
        self.jugar.capas[2].append(self) #  Capa de las bombas
        hilo = Thread(target=self.detonar) #Crea un hilo para la bomba
        hilo.daemon = True
        hilo.start()

    def detonar(self):
        sleep(self.tiempo_detonar/1000) #  Pasa el tiempo a segundos
        self.activa = False #Explota
        self.jugar.nivel[self.by][self.bx] = 0 #  Quita la hitbox
        Explosion(self, self.rango)
        self.jugar.capas[2].remove(self) #Ya no procesa la bomba
        
    
    def actualizar(self):
        if not self.hitbox_activa and (self.bx,self.by) not in self.jugador.sacar_esquinas(self.jugador.rect): #Crea la hitbox de la bomba cuando el jugador se va
            self.hitbox_activa = True
            self.jugar.nivel[self.by][self.bx] = 3 #Pone un bloque invisible
        
        #Acelera que tan rapido cambia el frame de la bomba entre menos tiempo le queda
        tiempo_actual = pg.time.get_ticks()
        intervalo_frame = max(100, (self.tiempo_detonar + self.tiempo_creacion - tiempo_actual)//5) #Cambia cada 1/5 parte del tiempo restante
        
        if tiempo_actual - self.ultima_actualizacion_frame > intervalo_frame: #Si han pasado 200 ms
            #Actualiza el frame a dibujar
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.sprites["bomba"]) # Frame ciclico, se reinicia cuando llega al final
            self.sprite = self.sprites["bomba"][self.frame] # Actualiza self.sprite
    
    def dibujar(self):
        self.pantalla.blit(self.sprite, (self.x, self.y)) #Dibuja el sprite actual

class Explosion:
    def __init__(self, bomba, rango):
        self.jugar = bomba.jugar
        self.jugador = self.jugar.jugador
        self.pantalla = bomba.pantalla
        self.bomba = bomba
        self.x = bomba.x//MEDIDA_BLOQUE+1
        self.y = bomba.y//MEDIDA_BLOQUE+1
        self.sprites = bomba.sprites
        self.nivel = self.jugar.nivel
        
        self.rango = rango
        self.activa = True
        self.frame = 0
        self.disipador = 1 #Variable para subir los frames y devolverlos al final, dando un efecto de que se disipa la bomba
        self.jugar.capas[5].append(self) #  Agrega la explosion para ser procesada
        self.frame_expansion = len(self.sprites["centro"]) - len(self.sprites["izquierda"]) #Cuantos frames pasan del centro antes de la explosion hacia los lados
        self.ultima_actualizacion_frame = time.get_ticks()
        self.bloques_afectados, self.bloques_rotos = self.obtener_bloques_afectados()
        
    
    def obtener_bloques_afectados(self):
        direcciones = (0, -1), (0, 1), (-1, 0), (1, 0) #Arriba, abajo, izq, der
        bloques_afectados = [(self.x, self.y)]
        bloques_rotos = []
        for dx, dy in direcciones: #Por cada direccion
            for i in range(1, self.rango+1): #Por cada bloque en el rango
                bloque_x = self.x + dx*i
                bloque_y = self.y + dy*i
                bloque = self.nivel[bloque_y][bloque_x]
                
                if bloque == 0: #Aire
                    bloques_afectados.append((bloque_x, bloque_y)) #Explosion ocurre en ese tile
                elif bloque == 2: #Bloque rompible
                    bloques_rotos.append((bloque_x, bloque_y))
                    break
                else:
                    break
        return bloques_afectados, bloques_rotos
    

    def matar(self):
        #Destruye bloques
        if self.frame == self.frame_expansion:
            for x, y in self.bloques_rotos:
                self.nivel[y][x] = 0
                self.jugador.puntaje += 20  # Aumenta el puntaje del jugador al destruir un bloque
            
        #Mata entidades
        for x, y in self.bloques_afectados:
            if not self.jugador.invulnerable and (x, y) == (self.jugador.rect.centerx//MEDIDA_BLOQUE+1, self.jugador.rect.centery//MEDIDA_BLOQUE+1): #Si el jugador no esta invulnerable
                self.jugador.morir()
                break
            for enemigo in self.jugar.capas[3]: #Capa donde se guardan los enemigos
                if (x, y) == (enemigo.rect.centerx//MEDIDA_BLOQUE+1, enemigo.rect.centery//MEDIDA_BLOQUE+1):
                    enemigo.vidas -= 1
                    if enemigo.vidas < 1:
                        self.jugar.capas[3].remove(enemigo)
                        self.jugador.puntaje += 100  # Aumenta el puntaje del jugador al matar un enemigo
    
    def actualizar(self):
        ahora = pg.time.get_ticks()
        if ahora - self.ultima_actualizacion_frame < 50: #Si no han pasado 50ms
            return
           
        if self.frame >= self.frame_expansion: #Ocurre la explosion, mata enemigos, el jugador y destruye bloques
            self.matar()

        self.ultima_actualizacion_frame = ahora
        self.frame += self.disipador

        if self.frame >= len(self.sprites["centro"])-1:
            self.disipador = -1
            
        elif self.frame == self.frame_expansion and self.disipador == -1:
            self.jugar.capas[5].remove(self) #En la capa 5 se guardan las explosiones, por tanto se remuve al terminar

    def dibujar(self):
        if self.frame < self.frame_expansion:
            self.pantalla.blit(self.sprites["centro"][self.frame], ((self.x-1)*MEDIDA_BLOQUE, (self.y-1)*MEDIDA_BLOQUE))
            return

        for bx, by in self.bloques_afectados:
            x = bx * MEDIDA_BLOQUE
            y = by * MEDIDA_BLOQUE

            if (bx, by) == (self.x, self.y):
                self.pantalla.blit(self.sprites["centro"][self.frame], (x-MEDIDA_BLOQUE, y-MEDIDA_BLOQUE))
                continue

            subframe = min(self.frame - 2, 2)

            #Vertial
            if bx == self.x:
                #Arriba
                if by < self.y:
                    punta = not (bx, by - 1) in self.bloques_afectados
                    llave = "punta_arriba" if punta else "arriba"
                #Abajo
                else:
                    punta = not (bx, by + 1) in self.bloques_afectados
                    llave = "punta_abajo" if punta else "abajo"
                    
            #Horizontal
            else:
                #Izquierda
                if bx < self.x:
                    punta = not (bx - 1, by) in self.bloques_afectados
                    llave = "punta_izquierda" if punta else "izquierda"
                #Derecha
                else:
                    punta = not (bx + 1, by) in self.bloques_afectados
                    llave = "punta_derecha" if punta else "derecha"

            self.pantalla.blit(self.sprites[llave][subframe], (x-MEDIDA_BLOQUE, y-MEDIDA_BLOQUE))

class Jefe:
    pass

# Función para cargar la llave, es especial, porque es un objeto que se encuentra dentro de un bloque aleatorio del nivel, y aparece al romperlo
class Llave:
    def __init__(self, jugar, x, y):
        self.x_bloque = x  # Posición en el eje X del bloque donde se encuentra la llave
        self.y_bloque = y  # Posición en el eje Y del bloque donde se encuentra la llave
        self.jugar = jugar
        self.nivel = self.jugar.nivel  # Nivel donde se encuentra la llave (se usa para verificar colisiones)
        self.jugador = self.jugar.jugador  # Jugador que recogerá la llave
        self.pantalla = self.jugar.pantalla_juego  # Pantalla donde se dibuja la llave
        self.sprite = cargar_llave()  # Carga el sprite de la llave desde la hoja de sprites
        self.rect = Rect((self.x_bloque - 1)* MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa la llave en el canvas (uso para colisiones)
        self.bloque_roto = False  # Indica si el bloque donde se encuentra la llave ha sido roto

    def actualizar(self):
        if self.nivel[self.y_bloque][self.x_bloque] == 0:
            self.bloque_roto = True
        if self.rect.colliderect(self.jugador.rect):
            self.jugador.tiene_llave = True
            self.jugar.capas[1].remove(self)  # Elimina la llave de la capa de objetos

    def dibujar(self):
        if self.bloque_roto and not self.jugador.tiene_llave:
            self.pantalla.blit(self.sprite, self.rect)  # Dibuja el sprite de la llave en la pantalla


class Puerta:
    def __init__(self, jugar, x, y):
        self.jugar = jugar
        self.x_bloque = x
        self.y_bloque = y
        self.nivel = jugar.nivel  # Nivel donde se encuentra la puerta (se usa para verificar colisiones)
        self.jugador = jugar.jugador  # Jugador que abrirá la puerta
        self.pantalla = jugar.pantalla_juego  # Pantalla donde se dibuja la puerta
        self.sprite = cargar_puerta()  # Carga el sprite de la puerta desde la hoja de sprites
        self.rect = Rect((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa la puerta en el canvas (uso para colisiones)

    def actualizar(self):
        if self.rect.colliderect(self.jugador.rect) and self.jugador.tiene_llave:
            self.jugador.tiene_llave = False
            self.jugar.pasar_nivel()

    def dibujar(self):
        self.pantalla.blit(self.sprite, ((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE))


class Caramelos:  # Los caramelos son un objeto que se encuentra en el nivel, y al recogerlos, el jugador gana estadísticas (daño, rango, vida)
    # Estos, al igual que la llave, se encuentran dentro de un bloque aleatorio del nivel, y aparecen al romperlo
    def __init__(self, x, y, jugar):
        self.x_bloque = x
        self.y_bloque = y
        self.jugar = jugar
        self.nivel = self.jugar.nivel  # Nivel donde se encuentra el caramelo (se usa para verificar colisiones)
        self.jugador = self.jugar.jugador  # Jugador que recogerá el caramelo
        self.pantalla = self.jugar.pantalla_juego  # Pantalla donde se dibuja el caramelo
        self.tipo = choice(["daño", "rango", "vida"])  # Tipo de caramelo (vida, rango o daño)
        self.sprite = cargar_caramelos()[self.tipo]  # Carga el sprite del caramelo desde la hoja de sprites
        self.rect = Rect((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE, MEDIDA_BLOQUE, MEDIDA_BLOQUE)
        self.bloque_roto = False  # Indica si el bloque donde se encuentra el caramelo ha sido roto

    def actualizar(self):
        if self.nivel[self.y_bloque][self.x_bloque] == 0:  # Si el bloque donde se encuentra el caramelo ha sido roto
            self.bloque_roto = True
        if self.rect.colliderect(self.jugador.rect):  # Si el jugador colisiona con el caramelo
            if self.tipo == "daño":
                self.jugador.golpe += 1  # Aumenta el daño del jugador
            elif self.tipo == "rango":
                self.jugador.rango += 1  # Aumenta el rango de la bomba del jugador
            elif self.tipo == "vida":
                self.jugador.vidas += 1  # Aumenta la vida del jugador
            self.jugar.capas[1].remove(self)  # Elimina el caramelo de la capa de objetos

    def dibujar(self):
        if self.bloque_roto:
            self.pantalla.blit(self.sprite, ((self.x_bloque - 1) * MEDIDA_BLOQUE, (self.y_bloque - 1) * MEDIDA_BLOQUE))  # Dibuja el sprite del caramelo en la pantalla
    

# Clase para botones: necesario para los botones del menú
class Boton:
    def __init__(self, x, y, ancho, alto, texto, pantalla, color=BLANCO, color_texto=NEGRO):
        self.x = x  # Posición en el eje X
        self.y = y  # Posición en el eje Y
        self.ancho = ancho  # Ancho del botón
        self.alto = alto  # Alto del botón
        self.texto = texto  # Texto del botón
        self.pantalla = pantalla  # Pantalla donde se dibuja el botón
        self.color = color  # Color del botón (por defecto es blanco)
        self.color_texto = color_texto  # Color del texto del botón (por defecto es negro)
        self.rect = pg.Rect(self.x, self.y, self.ancho, self.alto)  # Rectángulo que representa el botón para colisiones
        self.fuente = fuente_texto
        
        # Permite que no detecta un click todo el tiempo que mantiene click si no solo uno
        self.fue_presionado = False # Pasado
        self.presionado = False  # Presente

    def detectar(self, mouse_pos, *botones):
        if self.rect.collidepoint(mouse_pos) and any(botones) and not self.presionado:
            self.presionado = True
            return True
        else:
            self.presionado = False
        return False
            
        
    def dibujar(self):
        pg.draw.rect(self.pantalla, self.color, self.rect)  # Dibuja el botón en la pantalla
        pg.draw.rect(self.pantalla, NEGRO, self.rect, 2)  # Le crea un borde al botón (eso es lo que indica el 2, que es el grosor del borde)
        texto_renderizado = self.fuente.render(self.texto, True, self.color_texto)  # Renderiza el texto del botón
        self.pantalla.blit(texto_renderizado, (self.rect.x + (self.rect.width - texto_renderizado.get_width()) // 2, self.rect.y + (self.rect.height - texto_renderizado.get_height()) // 2))  # Dibuja el texto centrado en el botón

    def detectar_presionado(self, mouse_pos, *presses):
        ahora_presionado = any(presses) # Si presiono cualquier boton valido
        self.presionado = self.rect.collidepoint(mouse_pos) and ahora_presionado # self.presionado = mouse encima del boton y lo presiona
        presionado = self.presionado and not self.fue_presionado # Si acaba de presionar (no solo esta manteniendo click)
        self.fue_presionado = ahora_presionado #A ctualiza fue_presionado
        return presionado

class Menu:
    def __init__(self, game):
        self.game = game
        self.pantalla = game.pantalla  # Pantalla donde se dibuja el menú
        self.cambiar_modo = game.cambiar_modo
        self.volumen = game.volumen
        
        self.boton_cerrar = Boton(ANCHO_PANTALLA - 70, 20, 50, 50, "X", self.pantalla, ROJO, BLANCO)  # Botón para volver al menu desde alguna opcion
        
        #Opciones del menu
        self.config = Configuracion(self)
        self.info = Informacion(self)
        self.opcion_a_funcion = {"Jugar":game.jugar, "Configuración":self.config, "Información":self.info, "Salir":None} #Mapea el nombre de las opciones a ellas

        self.musica = game.canciones[0]
        self.botones = self.crear_botones()  # Crea los botones del menú
        self.logo = cargar_logo()



    def crear_botones(self):
        botones = []  # Lista de botones del menú
        for i, nombre in enumerate(self.opcion_a_funcion):  # Crea un botón para cada opción del menú
            x = ANCHO_PANTALLA // 2 - 100  # Centra el botón en la pantalla (no cambia para los demás botones, ya que están alineados en el mismo x)
            y = 480 + i * 60  # Espacio entre botones (en este caso, 60 píxeles entre cada botón)
            self.boton = Boton(x, y, ANCHO_BOTON, ALTO_BOTON, nombre, self.pantalla)  # Crea un botón con las dimensiones y texto correspondientes
            botones.append(self.boton)  # Agrega el botón a la lista de botones del menú
        return botones

    def dibujar(self):
        self.pantalla.fill(NEGRO)
        for boton in self.botones:  # Dibuja cada botón en la pantalla
            boton.dibujar()
        self.pantalla.blit(self.logo, (ANCHO_PANTALLA // 2 - self.logo.get_width() // 2, - 20))  # Dibuja el logo del juego en la parte superior de la pantalla
        
    def eventos(self, evento):
        mouse_pos = mouse.get_pos()
        for boton in self.botones:  # Recorre la lista de botones del menú
            if boton.detectar_presionado(mouse_pos, mouse.get_pressed()[0]): #Si detecta click izquierdo
                self.cambiar_modo(self.opcion_a_funcion[boton.texto]) #Mapea el texto del boton a un modo de juego


    def actualizar(self):
        pass
    
class Niveles:
    def __init__(self, jugar):
        self.jugar = jugar
        self.pantalla = jugar.pantalla_juego
        self.niveles = cargar_niveles()
        self.sprites = cargar_bloques()
        self.num_nivel = 1
        self.nivel = self.niveles[0]  # Inicia en el nivel 1
            
    def pasar_nivel(self):
        if 1 <= self.num_nivel+1 <= len(self.niveles):
            self.nivel = self.niveles[self.num_nivel]
            self.num_nivel += 1
            return True #Cambio de nivel exitoso
        #Cambio de nivel falla
    
    def dibujar(self):
        for y in range(1, ALTO_MATRIZ+1):
            for x in range(1, ANCHO_MATRIZ+1):
                ID = self.nivel[y][x]
                self.pantalla.blit(self.sprites[ID], ((x-1)*MEDIDA_BLOQUE, (y-1)*MEDIDA_BLOQUE))
                
        if self.jugar.debug:
            # Dibuja las lineas del grid
            for x in range(1, ANCHO_MATRIZ):
                draw.line(self.pantalla, NEGRO, (x*MEDIDA_BLOQUE, 0), (x*MEDIDA_BLOQUE, ALTO_PANTALLA))
            for y in range(1, ALTO_MATRIZ):
                draw.line(self.pantalla, NEGRO, (0, y*MEDIDA_BLOQUE), (ANCHO_PANTALLA, y*MEDIDA_BLOQUE))
                
    def actualizar(self):
        pass
    
    def cambio_nivel(self, num_nivel):
        if 1 <= num_nivel < len(self.niveles): # Verifica si existe el numero de nivel
            self.num_nivel = num_nivel
            self.nivel = self.niveles[num_nivel-1]
            
        elif num_nivel == len(self.niveles): # Se devuelve al primer nivel al terminar TODO (por que se devuelve? No deberia terminar y ya)
            self.nivel = self.num_niveles[0]
            
        else:
            pass #TODO poner resultados o no se que queria hacer Juan

class DestruyeBloque:
    def __init__(self, jugar, x, y):
        self.jugar = jugar
        self.pantalla = jugar.pantalla
        self.jugar.capas[4].append(self) #Capa del nivel
        self.x = x
        self.y = y
        self.sprite = jugar.manager_niveles.sprites[2]
        self.frames_totales = 10
        self.frame_actual = 0
        self.terminado = False
        
    def actualizar(self):
        self.frame_actual += 1
        if self.frame_actual >= self.frames_totales:
            self.jugar.capas[4].remove(self)

    def dibujar(self):
        # Escala proporcional inversa
        escala = max(1, int(MEDIDA_BLOQUE * max(0.01, 1 - self.frame_actual / self.frames_totales)))
        sprite_escalado = pg.transform.scale(self.sprite, (escala, escala))

        # Para que se mantenga centrado al reducir tamaño
        offset_x = (MEDIDA_BLOQUE - escala) // 2
        offset_y = (MEDIDA_BLOQUE - escala) // 2
        self.pantalla.blit(sprite_escalado, (self.x * MEDIDA_BLOQUE + offset_x, self.y * MEDIDA_BLOQUE + offset_y))



# Clase del juego
class Jugar:
    def __init__(self, game):
        self.pantalla = game.pantalla  # Pantalla donde se dibuja el juego
        self.pantalla_juego = Surface((ANCHO_PANTALLA - 2*SEPARACION_BORDES_PANTALLA, ALTO_PANTALLA - MEDIDA_HUD - SEPARACION_BORDES_PANTALLA))
        self.musica = game.canciones[1]
        self.sprites_bomba = game.sprites_bomba
        self.dibujar_texto = game.dibujar_texto # Toma el metodo de dibujar texto
        
        self.debug = False #G para cambiar (muestra hitboxes y gridlines)
        self.manager_niveles = Niveles(self)
        self.nivel = self.manager_niveles.nivel
        self.jugador = Jugador(self)
        self.lista_pegamento = []  # Lista para almacenar los pegamentos que sueltan los enemigos
        self.capas = {
            0:[self.manager_niveles], #  El fondo
            1:self.asignar_extras(),  #  Capa para objetos (llave, objetos, etc)
            2:[], #  Capa para bomba
            3:self.colocar_enemigos(),
            4:[self.jugador],
            5:[]} #  Capa para explosiones
        
    def colocar_enemigos(self):
        coords_ocupadas = [(X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR)]
        enemigos = []
        
        while len(enemigos) < CANTIDAD_ENEMIGOS:
            x = randint(1, ANCHO_MATRIZ)
            y = randint(1, ALTO_MATRIZ)
            
            if (x, y) not in coords_ocupadas and self.nivel[y][x] == 0:
                coords_ocupadas.append((x, y))
                enemigo = Enemigo(self, (x-1) * MEDIDA_BLOQUE, (y-1) * MEDIDA_BLOQUE)
                enemigos.append(enemigo)
        
        return enemigos

    def pasar_nivel(self):
        if self.manager_niveles.pasar_nivel():
            self.nivel = self.manager_niveles.nivel #Cambia los datos de nivel
            self.jugador.rect.topleft = X_INICIAL_JUGADOR, Y_INICIAL_JUGADOR #Reinicia la pos del jugador
            self.jugador.nivel = self.nivel #Cambia el nivel del jugador
            self.jugador.bombas += BOMBAS_DISPONIBLES
            self.capas[1] = [self.asignar_extras()]
            self.capas[3] = self.colocar_enemigos() #Pone los enemigos
            self.jugador.invulnerabilidad() #Hace el jugador invulnerable al iniciar el nivel
        
    def obtener_rompibles(self):
        bloques = [] #Guarda los bloques rompibles
        for y in range(1, ALTO_MATRIZ+1):
            for x in range(1, ANCHO_MATRIZ+1):
                if self.nivel[y][x] == 2:
                    bloques.append((x,y))
        return bloques
            
    
    def asignar_extras(self):
        bloques = self.obtener_rompibles()
        coords = choice(bloques)
        puerta = Puerta(self, coords[0], coords[1])
        bloques.remove(coords)
        coords = choice(bloques)
        llave = Llave(self, coords[0], coords[1])
        bloques.remove(coords)
        return [puerta, llave]
        
    
    def dibujar_HUD(self):
        pass
    
    def matar_entidad(self, entidad):
        for capa in self.capas:
            if entidad in self.capas[capa]:
                self.capas[capa].remove(entidad)
                break
    
    def actualizar(self):
        for capa in sorted(self.capas.keys()): #Actualiza entidades (jugador, enemigos, bombas...)
            for entidad in self.capas[capa]:
                entidad.actualizar()

    def eventos(self, evento):
        self.jugador.eventos(evento)
        if evento.type == KEYDOWN:
            if evento.key == K_g:
                if not self.debug:
                    self.debug = True
                    self.jugador.vidas = float('inf')
                    self.jugador.bombas = float('inf')
                else:
                    self.debug = False
                    self.jugador.vidas = VIDAS
                    self.jugador.bombas = BOMBAS_DISPONIBLES

    def dibujar(self):
        #Juego
        if not hasattr(self.jugador,"game_over"):  # Si el jugador ha perdido, dibuja la pantalla de Game Over
            self.pantalla_juego.fill(BLANCO)
            

            for capa in sorted(self.capas.keys()): #Dibuja entidades (jugador, enemigos, bombas...)
                for entidad in self.capas[capa]:  # Recorre cada capa y dibuja las entidades
                    entidad.dibujar()
                if capa == 1:  # Después de dibujar los elementos de la capa 1, dibuja el pegamento
                    for pegamento in self.lista_pegamento:  # Dibuja los pegamentos que sueltan los enemigos
                        pegamento.dibujar()
            
            #Dibuja la pantalla de juego en la principal
            self.pantalla.blit(self.pantalla_juego, (SEPARACION_BORDES_PANTALLA, MEDIDA_HUD))
            
            #Hud
            self.dibujar_texto(f"Nivel: {self.manager_niveles.num_nivel}", 0, 0, color=BLANCO)
            self.dibujar_texto(f"Vidas: {self.jugador.vidas}", 0, 25, color=BLANCO)
            self.dibujar_texto(f"Bombas: {self.jugador.bombas}", 0, 50, color=BLANCO)
            self.dibujar_texto(f"Puntaje: {self.jugador.puntaje}", 0, 75, color=BLANCO)
        else:
            self.jugador.game_over.dibujar()

    
class Informacion:
    def __init__(self, menu):
        self.menu = menu
        self.pantalla = menu.pantalla  # Pantalla donde se dibuja la información
        self.musica = menu.game.canciones[0]
        self.boton_cerrar = menu.boton_cerrar
        
        self.texto = "Información del juego"  # Texto de la información del juego
        self.fuente = fuente_texto  # Fuente del texto de la información
        self.foto_juan = pg.image.load("assets/carnets/JuanFoto.png").convert_alpha()  # Carga la imagen de Juan
        self.foto_pablo = pg.image.load("assets/carnets/PabloFoto.jpg").convert_alpha()  # Carga la imagen de Pablo
        self.foto_juan = pg.transform.scale(self.foto_juan, (150, 150))  # Reescala la imagen de Juan a 150x150 píxeles
        self.foto_pablo = pg.transform.scale(self.foto_pablo, (150, 150))  # Reescala la imagen de Pablo a 150x150 píxeles
        
        self.lineas = self.dividir_texto()

    # El texto que pensamos poner en la pantalla de información es medianamente largo, por lo que se dividirá en varias líneas
    def dividir_texto(self):
        self.ancho_max = ANCHO_PANTALLA - 100  # Ancho máximo de cada línea de texto
        self.fuente = fuente_texto  # Fuente del texto
        self.texto = TEXTO_INFO  # Texto a dividir

        bloques = self.texto.split("\n")  # Paso para dividir el texto y que respete los saltos de línea manuales 
        lineas = []  # Lista para almacenar las líneas de texto

        for bloque in bloques:
            palabras = bloque.split(' ')  # "Split" divide el texto en palabras, cada que encuentra un espacio, borrándolo en el proceso
            linea_actual = ""  # Línea actual que se está construyendo
            
            # Recorremos cada palabra y comprobamos para cada linea si cabe en el ancho máximo
            # Si cabe, se agrega a la línea actual y seguimos revisando
            # Si no cabe, se agrega la línea actual a la lista de líneas y se comienza una nueva línea con la palabra actual
            # Añadimos los espacios manualmente
            for palabra in palabras: 
                prueba = linea_actual + palabra + " "
                if self.fuente.size(prueba)[0] <= self.ancho_max:
                    linea_actual = prueba
                else:
                    lineas.append(linea_actual)
                    linea_actual = palabra + " "
            # Si al final hay una línea actual que no está vacía, la agregamos a la lista de líneas
            if linea_actual:
                lineas.append(linea_actual)
            # Devolvemos la lista de líneas

        return lineas  # Devuelve la lista de líneas de texto divididas

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        
        y = 50
        for linea in self.lineas:
            render = self.fuente.render(linea, True, BLANCO)
            x = (ANCHO_PANTALLA - render.get_width()) // 2  # Centra el texto en la pantalla
            self.pantalla.blit(render, (x, y))
            y += self.fuente.get_height() + 5
        self.boton_cerrar.dibujar()  # Dibuja el botón de cerrar la información
        
        self.pantalla.blit(self.foto_juan, (ANCHO_PANTALLA // 2 - self.foto_juan.get_width() - 20, ALTO_PANTALLA // 2 + self.foto_juan.get_height() // 2))  # Dibuja la foto de Juan
        self.pantalla.blit(self.foto_pablo, (ANCHO_PANTALLA // 2 + 20, ALTO_PANTALLA // 2 + self.foto_pablo.get_height() // 2))  # Dibuja la foto de Pablo B)
        
    def actualizar(self):
        pass #No hay que poner nada, pero quitarlo rompe el ciclo del juego
    
    def eventos(self, evento):
        mouse_pos = pg.mouse.get_pos()
        if self.boton_cerrar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            self.menu.cambiar_modo(self.menu)

class Deslizante:
    def __init__(self, pantalla, x, y, ancho, alto, parametro, min_parametro=0, max_parametro=1, radio_control=10):
        self.pantalla = pantalla
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.parametro = parametro #Valor a cambiar cuando se desliza la barra
        self.min_parametro = min_parametro #Minimo valor que puede tomar
        self.max_parametro = max_parametro #Maximo valor que puede tomar
        self.radio = radio_control
        
        self.x_control = self.x + int(self.ancho * self.parametro)  # Posición del control en x
        self.deslizando = False #Indica si se esta deslizando la barra
        
    def eventos(self, evento):
        mouse_pos = pg.mouse.get_pos()
        if evento.type == pg.MOUSEBUTTONDOWN:
            if abs(mouse_pos[0] - self.x_control) <= self.radio and abs(mouse_pos[1] - (self.y) + self.alto // 2) <= self.radio:  # Si el cursor está cerca del control deslizante
                self.deslizando = True  # Indica que se está arrastrando el control de la barra
            
        elif evento.type == pg.MOUSEBUTTONUP:
            self.deslizando = False #Suelta el deslizante
            
    def actualizar(self):
        if self.deslizando:  # Si se está arrastrando la barra de sonido
            self.x_control = self.x + int(self.ancho * self.parametro)  # Posición del control en x
            self.parametro = max(0, min(1, (pg.mouse.get_pos()[0] - self.x) / self.ancho))  # Calcula el nuevo valor del parametro según la posición del mouse
    
    def dibujar(self):
        pg.draw.rect(self.pantalla, GRIS, (self.x, self.y, self.ancho, self.alto))  # Dibuja el fondo de la barra
        pg.draw.rect(self.pantalla, VERDE, (self.x, self.y, self.ancho * self.parametro, self.alto))
        pg.draw.circle(self.pantalla, BLANCO, (self.x_control, self.y + self.alto // 2), self.radio)  # Dibuja el control deslizante en la barra de sonido

# Clase Configuracion: aquí se pueden agregar las configuraciones del juego, como el volumen
class Configuracion:
    def __init__(self, menu):
        self.menu = menu
        self.game = menu.game
        self.pantalla = menu.pantalla  # Pantalla donde se dibuja la información\
        self.musica = menu.game.canciones[0]
        self.boton_cerrar = menu.boton_cerrar
        self.fuente = fuente_texto  # Fuente del texto de la información
        self.barra_sonido = Deslizante(self.pantalla, ANCHO_PANTALLA//2 - 200, SEPARACION_BORDES_PANTALLA*9, 400, 10, self.game.volumen)

    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        
        self.texto_renderizado = self.fuente.render("Configuración", True, BLANCO)  # Renderiza el texto de la configuración
        self.texto_musica_renderizado = self.fuente.render("Volumen de la música", True, BLANCO)  # Renderiza el texto del volumen de la música
        
        self.pantalla.blit(self.texto_renderizado, (ANCHO_PANTALLA // 2 - self.texto_renderizado.get_width() // 2, 30))  # Dibuja el texto centrado en la pantalla
        self.pantalla.blit(self.texto_musica_renderizado, (SEPARACION_BORDES_PANTALLA * 4, SEPARACION_BORDES_PANTALLA * 8))
        
        self.barra_sonido.dibujar()
        self.boton_cerrar.dibujar()  # Dibuja el botón de cerrar la información
        
    def eventos(self, evento):
        mouse_pos = pg.mouse.get_pos()
        
        self.barra_sonido.eventos(evento)
        
        if self.boton_cerrar.detectar_presionado(mouse_pos, pg.mouse.get_pressed()[0]): #Click izquierdo
            self.menu.cambiar_modo(self.menu)
    
    def actualizar(self):
        self.barra_sonido.actualizar()
        if self.barra_sonido.deslizando: # Si se está deslizando la barra de sonido
            self.game.volumen = self.barra_sonido.parametro #Cambia el volumen en todo el juego
            self.musica.set_volume(self.game.volumen)  # Establece el volumen de la música

        

class Resultados:
    def __init__(self, game):
        self.pantalla = game.pantalla
        self.musica = game.canciones[2]
        # TODO

# Clase game que maneja a todas las otras clases
class Game: 
    def __init__(self):
        init()  # Inicializamos Pygame
        
        self.pantalla = display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))  # Configura la ventana
        display.set_caption("Wooly Warfare")  # Título de la ventana
        self.clock = time.Clock()  # Crea un objeto de reloj para controlar la tasa de refresco, necesario para la física y el movimiento
        self.running = True  # Variable para controlar el bucle del juego
        self.dt = 0  # Delta time, tiempo entre frames
        
        # Configuraciones de la música
        self.canciones = cargar_canciones()
        self.musica = None  # Espera a tener una instancia de música
        self.volumen = VALOR_INCIAL_VOLUMEN  # Volumen inicial del juego
        
        self.sprites_bomba = cargar_bomba()
        
        self.jugar = Jugar(self) #Crea una instancia del juego
        self.menu = Menu(self)  # Crea una instancia del menú

        self.modo = self.menu #Inicia en el modo menu
        self.modo_previo = None #Guarda el modo previo, permite devolverse en el menu

        self.administrar_musica()  # Llama a la función para administrar la música del juego

    def dibujar_texto(self, texto, x, y, fuente=fuente_texto, color=NEGRO):
        img = fuente.render(texto, True, color)
        self.pantalla.blit(img, (x, y))
    
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
        for evento in event.get():
            if evento.type == QUIT:
                self.running = False
            self.modo.eventos(evento) #Corre los eventos del modo activo
    
    def actualizar(self):
        self.modo.actualizar()


    def dibujar(self):
        self.pantalla.fill(NEGRO)  # Limpia la pantalla
        self.modo.dibujar()
        
    def run(self):
        while self.running:  # Bucle principal del juego
            display.flip()  # Actualiza la pantalla
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
# 13. Revisar todo lo que diga todo o pass
"""