"""
Configuración de parámetros de la simulación de la Biblioteca
Todos los valores en rojo del enunciado son parametrizables aquí
"""

class ConfigSimulacion:
    # Parámetros temporales
    TIEMPO_MAXIMO_SIMULACION = 480  # minutos (8 horas por defecto)
    MAX_ITERACIONES = 100000
    FILAS_A_MOSTRAR = 50  # cantidad de filas i a mostrar
    HORA_INICIO_MOSTRAR = 0  # hora j desde donde mostrar

    # Parámetros de llegadas
    TIEMPO_ENTRE_LLEGADAS = 4  # minutos

    # Parámetros de distribución de personas
    PROB_PEDIR_LIBRO = 0.45  # 45%
    PROB_DEVOLVER_LIBRO = 0.45  # 45%
    PROB_CONSULTAR = 0.10  # 10%

    # Parámetros de consultas
    TIEMPO_CONSULTA_MIN = 2  # minutos
    TIEMPO_CONSULTA_MAX = 5  # minutos

    # Parámetros de búsqueda de libros (Exponencial)
    MEDIA_BUSQUEDA = 6  # minutos (media de la exponencial)
    TIEMPO_DEVOLUCION_MIN = 2  # minutos
    TIEMPO_DEVOLUCION_MAX = 3.5  # 2 + 0.5 * 3 = 3.5 minutos máximo

    # Parámetros de personas que piden libros
    PROB_RETIRARSE = 0.60  # 60% se retira
    PROB_QUEDARSE_LEER = 0.40  # 40% se queda a leer

    # Parámetros de lectura (ecuación diferencial)
    # dP/dt = K/5, donde K depende del número de páginas
    K_100_200_PAG = 100  # K para libros entre 100 y 200 páginas
    K_200_300_PAG = 90   # K para libros entre 200 y 300 páginas
    K_MAS_300_PAG = 70   # K para libros con más de 300 páginas

    PAGINAS_MIN = 100  # U[100-350]
    PAGINAS_MAX = 350

    UNIDAD_INTEGRACION = 10  # minutos (unidad de tiempo para integración)
    H_EULER = 0.1  # paso de integración de Euler (parametrizable)

    # Parámetros de la biblioteca
    NUM_EMPLEADOS = 2
    CAPACIDAD_MAXIMA = 20  # personas (para cerrar biblioteca)

    # Semilla para reproducibilidad (opcional)
    SEMILLA_RANDOM = None  # None para aleatorio, o un número para reproducibilidad
