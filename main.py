"""
Programa principal - Simulación de Sistema de Biblioteca
"""
from config import ConfigSimulacion
from simulador import Simulador
from visualizador import VisualizadorVectorEstado
from exportador import ExportadorExcel


def solicitar_parametros():
    """Solicita los parámetros de simulación al usuario"""
    print("="*120)
    print("SIMULACIÓN DE SISTEMA DE BIBLIOTECA")
    print("="*120)
    print("\nIngrese los parámetros de simulación:")
    print("-"*120)

    config = ConfigSimulacion()

    # Tiempo máximo de simulación
    tiempo = input(f"\nTiempo máximo de simulación en minutos [{config.TIEMPO_MAXIMO_SIMULACION}]: ").strip()
    if tiempo:
        config.TIEMPO_MAXIMO_SIMULACION = float(tiempo)

    # Hora j desde donde mostrar
    hora_j = input(f"Hora de inicio para mostrar (j) [{config.HORA_INICIO_MOSTRAR}]: ").strip()
    if hora_j:
        config.HORA_INICIO_MOSTRAR = float(hora_j)

    # Cantidad de iteraciones a mostrar
    filas_i = input(f"Cantidad de filas a mostrar (i) [{config.FILAS_A_MOSTRAR}]: ").strip()
    if filas_i:
        config.FILAS_A_MOSTRAR = int(filas_i)

    # Parámetros parametrizables (en rojo en el enunciado)
    print("\n" + "-"*120)
    print("PARÁMETROS PARAMETRIZABLES (valores en rojo del enunciado):")
    print("-"*120)

    tiempo_llegadas = input(f"\nTiempo entre llegadas (minutos) [{config.TIEMPO_ENTRE_LLEGADAS}]: ").strip()
    if tiempo_llegadas:
        config.TIEMPO_ENTRE_LLEGADAS = float(tiempo_llegadas)

    prob_pedir = input(f"Probabilidad de pedir libro (0-1) [{config.PROB_PEDIR_LIBRO}]: ").strip()
    if prob_pedir:
        config.PROB_PEDIR_LIBRO = float(prob_pedir)

    prob_devolver = input(f"Probabilidad de devolver libro (0-1) [{config.PROB_DEVOLVER_LIBRO}]: ").strip()
    if prob_devolver:
        config.PROB_DEVOLVER_LIBRO = float(prob_devolver)

    prob_consultar = input(f"Probabilidad de consultar (0-1) [{config.PROB_CONSULTAR}]: ").strip()
    if prob_consultar:
        config.PROB_CONSULTAR = float(prob_consultar)

    # Normalizar probabilidades si no suman 1
    suma_prob = config.PROB_PEDIR_LIBRO + config.PROB_DEVOLVER_LIBRO + config.PROB_CONSULTAR
    if abs(suma_prob - 1.0) > 0.001:
        print(f"\nAVISO: Las probabilidades suman {suma_prob:.2f}, normalizando a 1.0")
        config.PROB_PEDIR_LIBRO /= suma_prob
        config.PROB_DEVOLVER_LIBRO /= suma_prob
        config.PROB_CONSULTAR /= suma_prob

    consulta_min = input(f"\nTiempo mínimo consulta (minutos) [{config.TIEMPO_CONSULTA_MIN}]: ").strip()
    if consulta_min:
        config.TIEMPO_CONSULTA_MIN = float(consulta_min)

    consulta_max = input(f"Tiempo máximo consulta (minutos) [{config.TIEMPO_CONSULTA_MAX}]: ").strip()
    if consulta_max:
        config.TIEMPO_CONSULTA_MAX = float(consulta_max)

    media_busqueda = input(f"Media búsqueda EXP (minutos) [{config.MEDIA_BUSQUEDA}]: ").strip()
    if media_busqueda:
        config.MEDIA_BUSQUEDA = float(media_busqueda)

    prob_retirarse = input(f"\nProbabilidad de retirarse con libro (0-1) [{config.PROB_RETIRARSE}]: ").strip()
    if prob_retirarse:
        config.PROB_RETIRARSE = float(prob_retirarse)
        config.PROB_QUEDARSE_LEER = 1.0 - config.PROB_RETIRARSE

    # Parámetros K para la ecuación diferencial
    print("\nParámetros K para ecuación diferencial dP/dt = K/5:")
    k_100_200 = input(f"K para libros 100-200 páginas [{config.K_100_200_PAG}]: ").strip()
    if k_100_200:
        config.K_100_200_PAG = float(k_100_200)

    k_200_300 = input(f"K para libros 200-300 páginas [{config.K_200_300_PAG}]: ").strip()
    if k_200_300:
        config.K_200_300_PAG = float(k_200_300)

    k_mas_300 = input(f"K para libros >300 páginas [{config.K_MAS_300_PAG}]: ").strip()
    if k_mas_300:
        config.K_MAS_300_PAG = float(k_mas_300)

    paginas_min = input(f"\nNúmero mínimo de páginas [{config.PAGINAS_MIN}]: ").strip()
    if paginas_min:
        config.PAGINAS_MIN = int(paginas_min)

    paginas_max = input(f"Número máximo de páginas [{config.PAGINAS_MAX}]: ").strip()
    if paginas_max:
        config.PAGINAS_MAX = int(paginas_max)

    h_euler = input(f"\nPaso h para integración Euler [{config.H_EULER}]: ").strip()
    if h_euler:
        config.H_EULER = float(h_euler)

    capacidad = input(f"\nCapacidad máxima biblioteca (personas) [{config.CAPACIDAD_MAXIMA}]: ").strip()
    if capacidad:
        config.CAPACIDAD_MAXIMA = int(capacidad)

    return config


def main():
    """Función principal"""
    # Solicitar parámetros
    config = solicitar_parametros()

    print("\n" + "="*120)
    print("INICIANDO SIMULACIÓN...")
    print("="*120)

    # Crear y ejecutar simulador
    simulador = Simulador(config)
    vector_estado = simulador.ejecutar()

    print(f"\nSimulación completada: {len(vector_estado)} filas generadas")
    print(f"Tiempo simulado: {simulador.reloj:.2f} minutos")

    # Calcular métricas
    metricas = simulador.calcular_metricas_finales()

    # Crear visualizador
    visualizador = VisualizadorVectorEstado(vector_estado)

    # Mostrar resultados en consola
    print("\n¿Desea visualizar el vector de estado?")
    print("1. Ver detallado (muestra toda la información)")
    print("2. Ver resumen en tabla")
    print("3. Ambos")
    print("4. No visualizar")

    opcion = input("\nSeleccione opción [1]: ").strip() or "1"

    if opcion in ["1", "3"]:
        visualizador.mostrar_filas(
            inicio=int(config.HORA_INICIO_MOSTRAR),
            cantidad=config.FILAS_A_MOSTRAR,
            mostrar_ultima=True
        )

    if opcion in ["2", "3"]:
        visualizador.mostrar_resumen_tabla(
            inicio=int(config.HORA_INICIO_MOSTRAR),
            cantidad=config.FILAS_A_MOSTRAR,
            mostrar_ultima=True
        )

    # Mostrar métricas
    visualizador.mostrar_metricas(metricas)

    # Preguntar si desea exportar a Excel
    exportar = input("\n¿Desea exportar los resultados a Excel? (s/n) [s]: ").strip().lower() or "s"

    if exportar == 's':
        nombre_archivo = input("Nombre del archivo [simulacion_biblioteca.xlsx]: ").strip() or "simulacion_biblioteca.xlsx"

        exportador = ExportadorExcel(vector_estado, metricas)
        exportador.exportar(nombre_archivo)

        # Preguntar si desea exportar integraciones detalladas
        exportar_int = input("\n¿Desea exportar las integraciones de Euler detalladas? (s/n) [s]: ").strip().lower() or "s"

        if exportar_int == 's':
            nombre_int = input("Nombre del archivo [integraciones_detalladas.xlsx]: ").strip() or "integraciones_detalladas.xlsx"
            exportador.exportar_historial_integraciones_detallado(nombre_int)

    print("\n" + "="*120)
    print("SIMULACIÓN FINALIZADA")
    print("="*120)


if __name__ == "__main__":
    main()
