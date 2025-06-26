ANCHO_PANTALLA = 1280  # Definimos el tamaño de la pantalla
ALTO_PANTALLA = 720
MEDIDA_HUD = 176  # (en píxeles)
MEDIDA_BLOQUE = 48  # (en píxeles)
ANCHO_MATRIZ = 26  # (en bloques)
ALTO_MATRIZ = 11  # (en bloques)

# Nombre  del archivo de puntajes
ARCHIVO_PUNTAJES = "puntajes.txt"

FPS = 60
PIXELES_SPRITES = 16  # (en píxeles)
SEPARACION_BORDES_PANTALLA = 16 # (en píxeles)
CANTIDAD_ENEMIGOS = 10 # Cantidad de enemigos que aparecen en cada nivel

# Colores
BLANCO = 255, 255, 255
NEGRO = 0, 0, 0
ROJO = 232, 58, 5
GRIS = 100, 100, 100
VERDE = 0, 255, 0
VERDE_AGUA = 52, 235, 171
AZUL = 52, 116, 235

# Variables para el juego
MARGEN_DESLIZAMIENTO = 5  # Espacio de "spare" para ajustar el movimiento del jugador (en píxeles)

ANCHO_BOTON = 200  # Ancho de los botones en el menú
ALTO_BOTON = 50  # Alto de los botones en el menú

TEXTO_INFO = "Desarrollado por: \n Juan Andrés Bastidas López - 2025066242\n Pablo Vargas Monge - 2025064957\nAmbos son estudiantes del ITCR, cursando la carrera de Ingeniería en Computación y entregando este trabajo como el III proyecto de Introducción a la programación.\nAño 2025 - Primer Semestre\n Profesores: Diego Mora Rojas y Jeff Schmidt Peralta\n Versión 1.0" 
VALOR_INCIAL_VOLUMEN = 0.0  # Valor inicial del volumen de la música (entre 0 y 1)  # TODO PONER EN 0.5

# Jugador
X_INICIAL_JUGADOR = 0
Y_INICIAL_JUGADOR = 0
ANCHO_JUGADOR = int(MEDIDA_BLOQUE * 0.75)
ALTO_JUGADOR = int(MEDIDA_BLOQUE * 0.75)
BOMBAS_DISPONIBLES = 15
VIDAS = 3
GOLPE = 1
ENFRIAMIENTO_HABILIDAD = 8000  # Tiempo en milisegundos antes de que el jugador pueda usar la habilidad nuevamente

# Configuración de la bomba
TIEMPO_DETONACION_BOMBA = 2000 # Tiempo en milisegundos antes de que la bomba explote 
GOLPE_INICIAL_BOMBA = 1  # Daño que causa la bomba al jugador y a los enemigos

# Configuración de los caramelos
CANTIDAD_CARAMELOS = 5  # Cantidad de caramelos máximos que aparecen en cada nivel (se toma si hay más bloques destructibles que caramelos requeridos)
CANTIDAD_POCIONES = 2  # Cantidad de pociones que aparecen en cada nivel (se toma si hay más bloques destructibles que pociones requeridas)

# Configuración del pegamento
PEGAMENTO_DURACION = 3000  # Duración del efecto de pegamento en milisegundos
RALENTIZACION_PEGAMENTO = 0.5  # Factor de ralentización del jugador al pisar el pegamento (0.5 significa que se mueve a la mitad de la velocidad normal)