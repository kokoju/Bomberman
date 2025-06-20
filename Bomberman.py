# Módulos necesarios 
from pygame import *  # Importa todos los módulos de Pygame necesarios para el juego
from time import sleep  # Importa sleep para manejar los Threads
from random import choice, randint  # Importa choice para seleccionar elementos aleatorios de listas (movimiento enemigo)
from threading import Thread  # Importa los Threads para el manejo de entidades en paralelo
from config import *  # Importa las configuraciones del juego, como dimensiones y FPS
from sprites import *  # Importa los sprites del jugador y otros elementos visuales
from niveles import *

# Usaremos una definición HD (1280x720p)
# En la parte superior de la pantalla, dejaremos una HUD de tamaño 1280x176 
# Abajo del HUD, haremos matrices de 11x26 (siendo cada bloque de 48x48): esto nos dejará con 32 pixeles sobrantes, repartidos en 16 pixeles en la parte izquierda y 16 pixeles en la parte derecha de la pantalla
# Además, dejé un espacio de 16 pixeles entre la matriz y el borde inferior, para que no se vea tan pegado
# Haremos los niveles con matrices (11x26), y como no se requiere crear nuevos, podemos ponerlos dentro del archivo de código

font.init()  # Inicializa el módulo de fuentes de Pygame
fuente_texto = font.Font("assets/FuenteTexto.ttf", 30)  # Tipografía del texto del juego

# Ideas de Items 
# Fantasmal -> Permite al jugador atravesar bloques destructibles/indestructibles por un tiempo limitado 
# Explosivo -> Aumenta el rango de las bombas del jugador por un tiempo limitado, además de no detenerse al contacto de un muro
# Freeze -> Congela a los enemigos por un tiempo limitado

# Clase Jugador
class Jugador:
    def __init__(self, juego, num_skin=3):
        self.pantalla = juego.pantalla  # Pantalla donde se dibuja el jugador
        self.nivel = juego.nivel  # Nivel actual del jugador (se usa para verificar colisiones)

        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = num_skin  # Número de skin del jugador (se puede cambiar para personalizar el jugador)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_iniciales_skins_jugador)  # Carga la skin del jugador desde la hoja de sprites

        self.direccion = "abajo"  # Dirección inicial del jugador (y a la que está mirando)
        self.frame = 0  # Frame actual del sprite del jugador
        self.sprite = self.skin_hoja_sprites[self.direccion][self.frame] #Sprite inicial del jugador
        
        self.vidas = 3  # Cantidad de vidas del jugador
        self.velocidad = 5  # Velocidad de movimiento del jugador (en pixeles)
        self.moviendose = False  # Indica si el jugador se está moviendo o no
        
        self.rect = Rect(ANCHO_PANTALLA//2, ALTO_PANTALLA//2, MEDIDA_BLOQUE-MEDIDA_BLOQUE//4, MEDIDA_BLOQUE-MEDIDA_BLOQUE) #  Rectangulo del jugador para posicion y colision
        
        self.movimientos_posibles = {
            K_w: (0, -(self.velocidad), "arriba"),  # Arriba
            K_s: (0, self.velocidad, "abajo"),     # Abajo
            K_a: (-(self.velocidad), 0, "izquierda"), # Izquierda
            K_d: (self.velocidad, 0, "derecha")     # Derecha
        }

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
            if self.nivel[y][x] != 0:
                return False
        return True
    
    def actualizar(self, keys):
        dx, dy = 0, 0
        # Saca el input del usuario
        self.moviendose = False
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
        if self.moviendose: #Jugador se mueve
            self.ultima_actualizacion_frame = time.get_ticks() # Reinicia el tiempo de la última actualización del sprite
            self.frame = (self.frame + 1) % len(self.skin_hoja_sprites) # Frame ciclico, se reinicia cuando llega al final
        else: #Jugador no se mueve
            self.frame = 0 #Reinicia
        self.sprite = self.skin_hoja_sprites[self.direccion][self.frame]

    #  Dibuja al jugador en la pantalla
    def dibujar(self):
        self.pantalla.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))  # Dibuja el sprite del jugador en la pantalla

    def poner_bomba(self):
        Bomba(self.pantalla, self.rect.centerx//MEDIDA_BLOQUE, self.rect.centery//MEDIDA_BLOQUE) # Pone una bomba en el jugador y la guarda en la lista de bombas

    def habilidad1(self):
        pass
    
    def habilidad2(self):
        pass
    
    def eventos(self, evento):
        if evento.type == KEYDOWN:
            if evento.key == K_SPACE: #Si le da a espacio
                self.poner_bomba()

            if evento.key == K_1: #Si le da a 1
                self.habilidad1()
                
            elif evento.key == K_2: #O si le da a 2
                self.habilidad2()

class Enemigo:
    def __init__(self, x, y, pantalla):
        self.x = x
        self.y = y
        self.pantalla = pantalla
        self.frame = 0
        self.ultima_actualizacion_frame = time.get_ticks()  # Tiempo de la última actualización del sprite
        self.numero_skin = 1  # Número de skin del enemigo (se puede cambiar para hacerlo más complicado)
        self.skin_hoja_sprites = cargar_skins(self.numero_skin, puntos_inciales_skins_enemigos)  # Carga la skin del enemigo desde la hoja de sprites
        self.direccion = 'abajo'  # Dirección inicial del enemigo (y a la que está mirando)
        self.vida = 1
        self.velocidad = 5
        self.rect = Rect(self.x, self.y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al enemigo en el canvas (uso para colisiones)

    # Mueve al enemigo en una dirección aleatoria
    def movimiento(self, obstaculos):
        # Genera un movimiento aleatorio
        movimientos = {"arriba" : (0, -self.velocidad), "abajo" : (0, self.velocidad), "izquierda" : (-self.velocidad, 0), "derecha" : (self.velocidad, 0)}  # Diccionario con los movimientos posibles
        movimiento_elegido = choice(list(movimientos.keys()))  # Elige un movimiento aleatorio del diccionario
        dx, dy = movimientos[movimiento_elegido]  # Obtiene el desplazamiento correspondiente al movimiento elegido
        # Cambia sus coords x y y
        new_x = self.x + dx  # Se calcula la nueva posición x
        new_y = self.y + dy
        rectangulo_verif = Rect(new_x, new_y, MEDIDA_BLOQUE, MEDIDA_BLOQUE, "red")  # Rectángulo que representa la nueva posición del jugador
        # Se hace una resta de MEDIDA_BLOQUE para que no se salga, ya que recordamos que las coords marcan la esquina superior izquierda del rectángulo
        if (ANCHO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_x > SEPARACION_BORDES_PANTALLA and (ALTO_PANTALLA - SEPARACION_BORDES_PANTALLA) - MEDIDA_BLOQUE > new_y > MEDIDA_HUD:  # Si está dentro de los límites del mapa
            # Verifica si no hay obstáculos en la nueva posición
            if all(not rectangulo_verif.colliderect(obs.rect) for obs in obstaculos):  # Si el rectángulo del enemigo no colisiona con NINGÚN obstáculo
                self.y = new_y
                self.x = new_x
                self.direccion = movimiento_elegido  # Actualiza la dirección del enemigo
                self.rect = rectangulo_verif  # Actualiza el rectángulo del enemigo a la nueva posición

    def actualizar_frame_sprite(self):
        self.ultima_actualizacion_frame = time.get_ticks()  # Reinicia el tiempo de la última actualización del sprite
        self.frame += 1  # Incrementa el frame actual del sprite
        if self.frame >= len(self.skin_hoja_sprites):  # Si el frame actual es mayor o igual al número de frames del sprite en la dirección actual
            self.frame = 0  # Reinicia el frame a 0 para que vuelva al primer sprite de la animación

    #  Dibuja al enemigo en la pantalla
    def dibujar(self):
        self.pantalla.blit(self.skin_hoja_sprites[self.direccion][self.frame], (self.x, self.y))  # Dibuja el sprite del jugador en la pantalla
        

class Bomba:
    bombas = [] #Guarda las bombas activas
    def __init__(self, pantalla, bloque_x, bloque_y):
        self.pantalla = pantalla #Pantalla para dibujar la bomba
        self.radio = MEDIDA_BLOQUE//2
        self.x = bloque_x*MEDIDA_BLOQUE+self.radio
        self.y = bloque_y*MEDIDA_BLOQUE+self.radio
        self.tiempo_detonar = TIEMPO_DETONACION_BOMBA  # Tiempo en segundos para que la bomba explote
        self.hit = HIT_BOMBA # Daño que causa la bomba al explotar
        self.activa = True
        Bomba.bombas.append(self)
        hilo = Thread(target=self.detonar) #Crea un hilo para la bomba
        hilo.daemon = True
        hilo.start()

    def detonar(self):
        sleep(self.tiempo_detonar)
        self.activa = False #Explota
        #TODO
        Bomba.bombas = [b for b in Bomba.bombas if b != self] #Quita la bomba
    
    def actualizar(self):
        pass #TODO
    
    def dibujar(self):
        if self.activa:
            draw.circle(self.pantalla, NEGRO, (self.x, self.y), self.radio)

class Explosion:
    pass


class Obstaculo:
    def __init__(self, x, y, destructible=False):
        self.x = x  # Posición x del obstáculo
        self.y = y  # Posición y del obstáculo
        self.destructible = destructible  # Si es destructible, puede ser destruido por una bomba
        self.rect = Rect(x, y, MEDIDA_BLOQUE, MEDIDA_BLOQUE)  # Rectángulo que representa al obstáculo en el canvas (SE USA EN COLISIONES)

    def colocar(self, pantalla):
        draw.rect(pantalla, "brown" if self.destructible else "gray", self.rect)  # Dibuja el obstáculo en la pantalla, con un color diferente si es destructible

    # Destruye el obstáculo si es destructible (se le pasa la lista de obstáculos y se saca solo)
    def destruir(self, lista_obstaculos):
        if self.destructible:
            lista_obstaculos.remove(self)


class Jefe:
    pass


class Objetos:
    pass


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
        self.fuente = fuente_texto  # Fuente del texto del botón
        self.fue_clickeado = False  # Indica si el botón ha sido clickeado

    def obtener_texto(self):
        # Devuelve el texto del botón
        return self.texto

    def clickeado(self, mouse_pos):
        # Comprueba si el botón ha sido clickeado
        if self.rect.collidepoint(mouse_pos):
            self.fue_clickeado = True  #  Marca el botón como clickeado
        
    def dibujar(self):
        pg.draw.rect(self.pantalla, self.color, self.rect)  # Dibuja el botón en la pantalla
        pg.draw.rect(self.pantalla, (0, 0, 0), self.rect, 2)  # Le crea un borde al botón (eso es lo que indica el 2, que es el grosor del borde)
        texto_renderizado = self.fuente.render(self.texto, True, self.color_texto)  # Renderiza el texto del botón
        self.pantalla.blit(texto_renderizado, (self.rect.x + (self.rect.width - texto_renderizado.get_width()) // 2, self.rect.y + (self.rect.height - texto_renderizado.get_height()) // 2))  # Dibuja el texto centrado en el botón

class Menu:
    def __init__(self, pantalla):
        self.pantalla = pantalla  # Pantalla donde se dibuja el menú
        self.opciones = ["Jugar", "Opciones", "Información", "Salir"]  # Opciones del menú
        self.logo = pg.image.load("assets/logo.png").convert_alpha()  # Carga el logo del juego
        self.logo = pg.transform.scale(self.logo, (MEDIDA_REESCALADO_LOGO, MEDIDA_REESCALADO_LOGO))  # Reescala el logo a la medida deseada
        self.lista_botones = []  # Lista de botones del menú
        self.musica = pg.mixer.Sound("assets/musica/MusicaMenu.mp3")  # Carga la música del menú
        self.crear_botones()  # Crea los botones del menú

    def crear_botones(self):
        for i in range(len(self.opciones)):  # Crea un botón para cada opción del menú
            x = ANCHO_PANTALLA // 2 - 100  # Centra el botón en la pantalla (no cambia para los demás botones, ya que están alineados en el mismo x)
            y = 480 + i * 60  # Espacio entre botones (en este caso, 60 píxeles entre cada botón)
            self.boton = Boton(x, y, ANCHO_BOTON, ALTO_BOTON, self.opciones[i], self.pantalla)  # Crea un botón con las dimensiones y texto correspondientes
            self.lista_botones.append(self.boton)  # Agrega el botón a la lista de botones del menú

    def dibujar(self):
        # Llena la pantalla de negro
        self.pantalla.fill((0, 0, 0))
        for boton in self.lista_botones:  # Dibuja cada botón en la pantalla
            boton.dibujar()
        self.pantalla.blit(self.logo, (ANCHO_PANTALLA // 2 - self.logo.get_width() // 2, - 20))  # Dibuja el logo del juego en la parte superior de la pantalla

# Clase del juego
class Juego:
    def __init__(self, pantalla, lista_niveles):
        self.pantalla = pantalla  # Pantalla donde se dibuja el juego
        self.nivel = cargar_niveles()[0]  # Carga el primer nivel del juego
        self.jugador = Jugador(self)  # Crea una instancia del jugador
        self.lista_enemigos = []  # Lista de enemigos en el juego
        self.lista_obstaculos = []  # Lista de obstáculos en el juego
        self.colocar_enemigos()
        self.num_nivel = 0  # Nivel actual del juego (self.nivel = 0 significa que estamos en el primer nivel)
        self.lista_niveles = lista_niveles  # Lista de niveles del juego
        self.nivel = self.lista_niveles[0]  # Carga el primer nivel del juego
        self.musica = pg.mixer.Sound("assets/musica/MusicaJuego.mp3")  # Carga la música del juego
        self.colocar_enemigos()  # Coloca los enemigos en el nivel actual

    def cambio_nivel(self):
        self.nivel += 1  # Incrementa el nivel actual del juego
        if self.nivel > len(self.lista_niveles):  # Si se llega al final, se vuelve al incio
            self.nivel = 0

    def colocar_enemigos(self):
        for _ in range(CANTIDAD_ENEMIGOS):  # Coloca 5 enemigos en posiciones aleatorias del mapa
            coord_x = randint(0, ANCHO_MATRIZ - 1) * MEDIDA_BLOQUE + SEPARACION_BORDES_PANTALLA  # Genera una coordenada x aleatoria dentro del mapa
            coord_y = randint(0, ALTO_MATRIZ - 1) * MEDIDA_BLOQUE + MEDIDA_HUD  # Genera una coordenada y aleatoria dentro del mapa
            enemigo = Enemigo(coord_x, coord_y, self.pantalla)  # Crea una instancia del enemigo en la posición aleatoria
            self.lista_enemigos.append(enemigo)  # Agrega el enemigo a la lista de enemigos

    def actualizar(self):
        keys = key.get_pressed()
        for bomba in Bomba.bombas:
            bomba.actualizar()
        self.jugador.actualizar(keys)

    def eventos(self, evento):
        self.jugador.eventos(evento)

    def dibujar(self):
        self.pantalla.fill((0, 0, 0))  # Limpia la pantalla
        for i in range(ANCHO_MATRIZ):
            for j in range(ALTO_MATRIZ):
                        # Dibuja el fondo de la pantalla
                        # Pantalla, color, posición (x, y), tamaño (ancho, alto)
                        if self.nivel[j][i] == 0:  # Si el bloque es vacío
                            draw.rect(self.pantalla, (0, 255, 255), (16 + (i * MEDIDA_BLOQUE), MEDIDA_HUD + (j * MEDIDA_BLOQUE), MEDIDA_BLOQUE, MEDIDA_BLOQUE)) 
                        else:
                            # La comparación de la casilla con un número nos dice qué tipo de bloque es (destructible o indestructible)
                            obs = Obstaculo(16 + (i * MEDIDA_BLOQUE), MEDIDA_HUD + (j * MEDIDA_BLOQUE), self.nivel[j][i] == 2)
                            self.lista_obstaculos.append(obs)  # Agrega el obstáculo a la lista de obstáculos
                            obs.colocar(self.pantalla)  # Dibuja el obstáculo en la pantalla
        for enemigo in self.lista_enemigos:  # Dibuja todos los enemigos en la pantalla
            enemigo.dibujar()

        for bomba in Bomba.bombas:  # Dibuja todas las bombas en la pantalla
            bomba.dibujar()

        self.jugador.dibujar()  # Dibuja al jugador en la pantalla   
    
class Informacion:
    def __init__(self, pantalla):
        self.pantalla = pantalla  # Pantalla donde se dibuja la información
        self.texto = "Información del juego"  # Texto de la información del juego
        self.fuente = fuente_texto  # Fuente del texto de la información
        self.boton_cerrar = Boton(ANCHO_PANTALLA - 70, 20, 50, 50, "X", self.pantalla, ROJO, BLANCO)  # Botón para cerrar la información
        self.foto_juan = pg.image.load("assets/carnets/JuanFoto.png").convert_alpha()  # Carga la imagen de Juan
        self.foto_pablo = pg.image.load("assets/carnets/PabloFoto.jpg").convert_alpha()  # Carga la imagen de Pablo
        self.foto_juan = pg.transform.scale(self.foto_juan, (150, 150))  # Reescala la imagen de Juan a 150x150 píxeles
        self.foto_pablo = pg.transform.scale(self.foto_pablo, (150, 150))  # Reescala la imagen de Pablo a 150x150 píxeles

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
        y = 50
        self.pantalla.fill((0, 0, 0))  # Limpia la pantalla
        lineas = self.dividir_texto()
        for linea in lineas:
            render = self.fuente.render(linea, True, (255, 255, 255))
            x = (ANCHO_PANTALLA - render.get_width()) // 2  # Centra el texto en la pantalla
            self.pantalla.blit(render, (x, y))
            y += self.fuente.get_height() + 5
        self.boton_cerrar.dibujar()  # Dibuja el botón de cerrar la información
        self.pantalla.blit(self.foto_juan, (ANCHO_PANTALLA // 2 - self.foto_juan.get_width() - 20, ALTO_PANTALLA // 2 + self.foto_juan.get_height() // 2))  # Dibuja la foto de Juan
        self.pantalla.blit(self.foto_pablo, (ANCHO_PANTALLA // 2 + 20, ALTO_PANTALLA // 2 + self.foto_pablo.get_height() // 2))  # Dibuja la foto de Pablo
       
# Clase Opciones: aquí se pueden agregar las opciones del juego, como el volumen
class Opciones:
    def __init__(self, pantalla):
        self.pantalla = pantalla  # Pantalla donde se dibuja la información
        self.texto = "Opciones"  # Texto de la información del juego
        self.texto_musica = "Volumen de la música"
        self.fuente = fuente_texto  # Fuente del texto de la información
        self.boton_cerrar = Boton(ANCHO_PANTALLA - 70, 20, 50, 50, "X", self.pantalla, ROJO, BLANCO)  # Botón para cerrar la información
        self.arrastrando_barra = False  # Indica si se está arrastrando la barra de sonido

    def barra_sonido(self, volumen):
        # Dibuja una barra de sonido en la pantalla
        # Definimos las coordenadas y dimensiones de la barra (fondo)
        pg.draw.rect(self.pantalla, (100, 100, 100), (BARRA_X, BARRA_Y, BARRA_ANCHO, BARRA_ALTO))  # Dibuja el fondo de la barra de sonido en color gris
        # Parte que se llena en función del volumen
        pg.draw.rect(self.pantalla, VERDE, (BARRA_X, BARRA_Y, BARRA_ANCHO * volumen, BARRA_ALTO))
        x_control = BARRA_X + int(BARRA_ANCHO * volumen)  # Posición del control deslizante según el volumen
        pg.draw.circle(self.pantalla, BLANCO, (x_control, BARRA_Y + BARRA_ALTO // 2), RADIO_CONTROL)  # Dibuja el control deslizante en la barra de sonido

    def dibujar(self, volumen):
        self.pantalla.fill((0, 0, 0))  # Limpia la pantalla
        self.texto_renderizado = self.fuente.render(self.texto, True, BLANCO)  # Renderiza el texto de las opciones
        self.texto_musica_renderizado = self.fuente.render(self.texto_musica, True, BLANCO)  # Renderiza el texto del volumen de la música
        self.barra_sonido(volumen)  # Dibuja la barra de sonido en el centro de la pantalla
        self.pantalla.blit(self.texto_renderizado, (ANCHO_PANTALLA // 2 - self.texto_renderizado.get_width() // 2, 30))  # Dibuja el texto centrado en la pantalla
        self.pantalla.blit(self.texto_musica_renderizado, (SEPARACION_BORDES_PANTALLA * 4, SEPARACION_BORDES_PANTALLA * 8))
        self.boton_cerrar.dibujar()  # Dibuja el botón de cerrar la información
        
class Resultados:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.musica = pg.mixer.Sound("assets/musica/MusicaResultados.mp3")  # Carga la música de los resultados
        # TODO

# Creamos una clase para el juego: esta llamará todas las opciones anteriores y las ejecutará en el orden correcto
class Game: 
    def __init__(self):
        init()  # Inicializamos Pygame
        self.pantalla = display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))  # Configura la ventana
        display.set_caption("Wooly Warfare")  # Título de la ventana
        self.clock = time.Clock()  # Crea un objeto de reloj para controlar la tasa de refresco, necesario para la física y el movimiento
        self.running = True  # Variable para controlar el bucle del juego
        self.dt = 0  # Delta time, tiempo entre frames
        self.modos = {"menu": True, "opciones": False, "info": False, "jugar": False, "resultados": False}  # Fases de juego
        
        # Configuraciones de la música 
        self.musica = None  # Espera a tener una instancia de música
        self.volumen = VALOR_INCIAL_VOLUMEN  # Volumen inicial del juego

        self.menu = Menu(self.pantalla)  # Crea una instancia del menú
        self.lista_niveles = cargar_niveles()

        self.administrar_musica()  # Llama a la función para administrar la música del juego
        
    def administrar_musica(self):
        if self.musica is not None:  # Si es la primera vez que se llama, no hay música, entonces no haríamos nada
            self.musica.stop()
        if self.modos["menu"] or self.modos["info"] or self.modos["opciones"]:
            self.musica = self.menu.musica  # Usa la música del menú
        elif self.modos["jugar"]:
            self.musica = self.juego.musica  # Usa la música del juego
        elif self.modos["resultados"]:
            self.musica = self.resultados.musica  # Usa la música de los resultados
        self.musica.play(-1)  # Reproduce la música en bucle
        self.musica.set_volume(self.volumen)  # Establece el volumen de la música

    def actualizar(self):
        for evento in event.get():
            if evento.type == QUIT:
                self.running = False
            elif evento.type == MOUSEBUTTONDOWN:  # Si se presiona un botón del mouse
                mouse_pos = mouse.get_pos()
                for boton in self.menu.lista_botones:  # Recorre la lista de botones del menú
                    boton.clickeado(mouse_pos)
                    if boton.fue_clickeado:  # Si el botón ha sido clickeado
                        if boton.obtener_texto() == "Jugar":
                            self.modos["menu"] = False
                            self.juego = Juego(self.pantalla, self.lista_niveles)  # Crea una instancia del juego
                            self.modos["jugar"] = True
                            self.administrar_musica()  # Llama a la función para administrar la música del juego
                        elif boton.obtener_texto() == "Información":
                            self.modos["menu"] = False
                            self.info = Informacion(self.pantalla)  # Crea una instancia de la clase Información
                            self.modos["info"] = True
                        elif boton.obtener_texto() == "Opciones":
                            self.modos["menu"] = False
                            self.opciones = Opciones(self.pantalla)  # Crea una instancia de la clase Opciones
                            self.modos["opciones"] = True
                        elif boton.obtener_texto() == "Salir":
                            self.running = False
                        boton.fue_clickeado = False  # Reinicia el estado del botón después de clickeado

                if hasattr(self, "info"):
                    self.info.boton_cerrar.clickeado(mouse_pos)  # Verifica si se ha clickeado el botón de cerrar en la información
                    if self.info.boton_cerrar.fue_clickeado:  # Si se ha clickeado el botón de cerrar
                        self.modos["info"] = False  # Cambia el modo a no información
                        self.modos["menu"] = True  # Vuelve al menú principal
                        self.info.boton_cerrar.fue_clickeado = False  # Reinicia el estado del botón de cerrar

                if hasattr(self, "opciones"):
                    self.opciones.boton_cerrar.clickeado(mouse_pos)
                    if self.opciones.boton_cerrar.fue_clickeado:  # Si se ha clickeado el botón de cerrar
                        self.modos["opciones"] = False  # Cambia el modo a no opciones
                        self.modos["menu"] = True  # Vuelve al menú principal
                        self.opciones.boton_cerrar.fue_clickeado = False  # Reinicia el estado del botón de cerrar

                    # Control de la barra de sonido
                    x_control = BARRA_X + int(BARRA_ANCHO * self.volumen)  # Posición del control de sonido deslizante según el volumen
                    if abs(mouse_pos[0] - x_control) <= RADIO_CONTROL and abs(mouse_pos[1] - (BARRA_Y) + BARRA_ALTO // 2) <= RADIO_CONTROL:  # Si el mouse está cerca del control deslizante
                        self.opciones.arrastrando_barra = True  # Indica que se está arrastrando el control de la barra de sonido
            
            elif evento.type == MOUSEBUTTONUP:  # Si se suelta un botón del mouse
                if hasattr(self, "opciones"):
                    if self.opciones.arrastrando_barra:
                        self.opciones.arrastrando_barra = False  # Indica que ya no se está arrastrando la barra de sonido

            elif evento.type == KEYDOWN:  # Si se presiona una tecla
                if hasattr(self, "juego") and self.modos["jugar"]:  # Si estamos en el modo de juego
                    self.juego.eventos(evento)  # Llama al método de eventos del juego

        if hasattr(self, "opciones"):
            if self.opciones.arrastrando_barra:  # Si se está arrastrando la barra de sonido
                mouse_pos = mouse.get_pos()  # Obtiene la posición del mouse
                self.volumen = max(0, min(1, (mouse_pos[0] - BARRA_X) / BARRA_ANCHO))  # Calcula el nuevo volumen según la posición del mouse
                self.musica.set_volume(self.volumen)  # Establece el volumen de la música

    def dibujar(self):
        if self.modos["menu"]:  # Si estamos en el modo de menú
            self.menu.dibujar()

        elif self.modos["jugar"]:  # Si estamos en el modo de juego
            self.juego.dibujar()  # Dibuja el juego y actualiza el estado del jugador, enemigos y obstáculos

        elif self.modos["info"]:  # Si estamos en el modo de información
            self.info.dibujar()

        elif self.modos["opciones"]:  # Si estamos en el modo de opciones
            self.opciones.dibujar(self.volumen)  # Dibuja las opciones del juego

        elif self.modos["resultados"]:
            pass

        
    def run(self):
        while self.running:  # Bucle principal del juego
            display.flip()  # Actualiza la pantalla
            self.dt = self.clock.tick(FPS) / 1000  # Controla la tasa de refresco del juego
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
"""
