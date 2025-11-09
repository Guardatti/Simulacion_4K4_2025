"""
Generadores de números aleatorios y distribuciones
"""
import random
import math

class GeneradorAleatorio:
    """Generador de números aleatorios con diferentes distribuciones"""

    def __init__(self, semilla=None):
        if semilla is not None:
            random.seed(semilla)
        self.ultimo_random = None

    def uniforme(self, a, b):
        """Genera un número aleatorio uniforme entre a y b"""
        self.ultimo_random = random.random()
        return a + (b - a) * self.ultimo_random

    def exponencial(self, media):
        """Genera un número aleatorio con distribución exponencial de media dada"""
        self.ultimo_random = random.random()
        return -media * math.log(1 - self.ultimo_random)

    def uniforme_discreta(self, a, b):
        """Genera un número entero aleatorio uniforme entre a y b (inclusive)"""
        self.ultimo_random = random.random()
        return int(a + (b - a + 1) * self.ultimo_random)

    def obtener_ultimo_random(self):
        """Retorna el último número aleatorio generado (entre 0 y 1)"""
        return self.ultimo_random if self.ultimo_random is not None else 0.0


class IntegradorEuler:
    """
    Integrador numérico por método de Euler para resolver ecuaciones diferenciales
    Para resolver: dP/dt = K/5
    """

    def __init__(self, h, K, p_inicial=0):
        """
        h: paso de integración
        K: constante que depende del número de páginas
        p_inicial: valor inicial de P (páginas leídas)
        """
        self.h = h
        self.K = K
        self.p = p_inicial
        self.historial = [(0, p_inicial)]  # (tiempo, páginas)

    def derivada(self, p, t):
        """Función derivada: dP/dt = K/5"""
        return self.K / 5.0

    def paso(self):
        """Ejecuta un paso del método de Euler"""
        t_actual = self.historial[-1][0]
        p_actual = self.historial[-1][1]

        # Euler: p_nuevo = p_actual + h * f(p_actual, t_actual)
        p_nuevo = p_actual + self.h * self.derivada(p_actual, t_actual)
        t_nuevo = t_actual + self.h

        self.historial.append((t_nuevo, p_nuevo))
        self.p = p_nuevo

        return p_nuevo

    def integrar_hasta(self, t_final):
        """Integra hasta un tiempo final dado"""
        while self.historial[-1][0] < t_final:
            self.paso()
        return self.p

    def obtener_historial(self):
        """Retorna el historial de integración"""
        return self.historial

    def obtener_valor_actual(self):
        """Retorna el valor actual de P (páginas leídas)"""
        return self.p
