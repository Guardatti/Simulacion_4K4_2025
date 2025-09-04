import random
import math

def generar_uniforme(n, a, b):
    return [round(a + (b - a) * random.random(), 4) for _ in range(n)]

def generar_exponencial(n, lambd):
    return [round((-1 / lambd) * math.log(1 - random.random()), 4) for _ in range(n)]

def generar_normal(n, mu, sigma):
    resultados = []
    for _ in range(n // 2):
        u1, u2 = random.random(), random.random()
        z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        z2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        resultados.append(round(mu + sigma * z1, 4))
        resultados.append(round(mu + sigma * z2, 4))
    if len(resultados) < n:
        resultados.append(round(mu + sigma * z1, 4))
    return resultados
