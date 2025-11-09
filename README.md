# Simulación de Sistema de Biblioteca

Simulación por eventos discretos de un sistema de biblioteca que implementa todos los requerimientos del TP5 de Simulación.

## Descripción del Sistema

El sistema simula una biblioteca pública con las siguientes características:

- **Llegadas**: Personas llegan cada 4 minutos (parametrizable)
- **Empleados**: 2 empleados en el mostrador
- **Acciones**: Las personas pueden:
  - Pedir libros prestados (45%)
  - Devolver libros (45%)
  - Consultar condiciones para hacerse socio (10%)
- **Lectura**: Las personas que piden libros pueden retirarse (60%) o quedarse a leer (40%)
- **Tiempo de lectura**: Determinado por ecuación diferencial `dP/dt = K/5`, integrada numéricamente con método de Euler
- **Política de cierre**: La biblioteca cierra cuando hay 20 personas dentro

## Características Implementadas

✅ **Vector de Estado Completo**:
- Número de fila
- Reloj de simulación
- Evento ejecutado
- Próximos eventos en FEL
- Estado de todos los objetos (Biblioteca, Empleados, Personas)
- Números aleatorios utilizados
- Integraciones de Euler activas
- Acumuladores y contadores

✅ **Parámetros Configurables**:
- Todos los valores "en rojo" del enunciado son parametrizables
- Tiempo máximo de simulación (X)
- Número máximo de iteraciones (hasta 100,000)
- Hora de inicio (j) y cantidad de filas a mostrar (i)
- Paso de integración h para Euler

✅ **Visualización**:
- Vista detallada de cada fila del vector de estado
- Vista resumida en tabla
- Última fila de simulación siempre mostrada
- Números aleatorios mostrados en cada iteración

✅ **Integración Numérica**:
- Método de Euler con paso h parametrizable
- Ecuación diferencial: dP/dt = K/5
- K variable según número de páginas:
  - K=100 para 100-200 páginas
  - K=90 para 200-300 páginas
  - K=70 para más de 300 páginas
- Historial completo de integración exportable a Excel

✅ **Métricas Calculadas**:
- Promedio de permanencia en la biblioteca
- Porcentaje de tiempo que la biblioteca estuvo cerrada

✅ **Exportación a Excel**:
- Vector de estado completo
- Integraciones de Euler con historial detallado
- Métricas finales

## Instalación

1. Clonar o descargar el repositorio

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Ejecución con Interfaz Gráfica (Recomendado) 🎨

```bash
python gui_biblioteca.py
```

**Interfaz gráfica moderna** con:
- ⚙ Configuración visual de todos los parámetros
- 📋 Tabla interactiva del vector de estado (estilo Excel)
- 📈 Gráficos de integración numérica en tiempo real
- 📊 Análisis visual de métricas y evolución del sistema
- 💾 Exportación directa a Excel desde menú
- 🔍 Búsqueda y navegación por filas
- 📉 Gráficos de personas en el sistema, utilización de empleados, cola, etc.

### Ejecución por Consola

```bash
python main.py
```

El programa solicitará todos los parámetros de forma interactiva. Presionar Enter para usar valores por defecto.

### Personalización de Parámetros

Editar el archivo [config.py](config.py) para modificar los valores por defecto de todos los parámetros.

Parámetros principales:
- `TIEMPO_MAXIMO_SIMULACION`: Tiempo máximo a simular (minutos)
- `MAX_ITERACIONES`: Máximo número de iteraciones (100,000)
- `FILAS_A_MOSTRAR`: Cantidad de filas (i) a mostrar
- `HORA_INICIO_MOSTRAR`: Hora de inicio (j) para visualización
- `H_EULER`: Paso de integración de Euler

## Estructura del Proyecto

```
Tp5-SIM/
│
├── config.py              # Configuración de parámetros
├── generadores.py         # Generadores aleatorios e integrador Euler
├── entidades.py          # Clases: Persona, Empleado, Libro, Biblioteca
├── eventos.py            # Sistema de eventos (FEL)
├── simulador.py          # Motor principal de simulación
├── visualizador.py       # Visualización del vector de estado (consola)
├── exportador.py         # Exportación a Excel
├── gui_biblioteca.py     # Interfaz gráfica (GUI) ⭐
├── main.py               # Programa principal (consola)
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## Componentes Principales

### Motor de Simulación ([simulador.py](simulador.py))

Implementa la lógica de eventos discretos:
- `LLEGADA_PERSONA`: Llegada de una nueva persona
- `FIN_ATENCION`: Fin de atención en el mostrador
- `FIN_LECTURA`: Persona termina de leer
- `FIN_SIMULACION`: Fin del tiempo de simulación

### Vector de Estado

Cada fila contiene:
- Estado de la biblioteca (abierta/cerrada)
- Cola de atención
- Personas leyendo
- Estado de empleados
- Acumuladores
- Números aleatorios usados
- Integraciones activas

### Integración de Euler ([generadores.py](generadores.py))

Resuelve la ecuación diferencial `dP/dt = K/5` para calcular el tiempo de lectura:
- Paso configurable (h)
- Historial completo de valores
- Diferentes valores de K según páginas del libro

## Ejemplo de Salida

```
===============================================
VECTOR DE ESTADO - SIMULACIÓN BIBLIOTECA
===============================================

FILA           : 15
RELOJ          : 60.00 min
EVENTO         : Fin Atención

PRÓXIMOS EVENTOS:
  1. Llegada Persona a las 64.00 min
  2. Fin Lectura a las 90.00 min
  3. Fin Atención a las 62.50 min

BIBLIOTECA     :
  Estado: ABIERTA
  Personas dentro: 8
  En cola: 2 ['P10', 'P11']
  Leyendo: 3 ['P5', 'P7', 'P9']

EMPLEADOS      :
  E1: Ocupado - Atendiendo P12 hasta 65.30
  E2: Libre

RANDOMS USADOS :
  decision_leer: 0.3456
  num_paginas: 0.7234

INTEGRACIONES EULER:
  P5: P(t) = 45.67 páginas
  P7: P(t) = 89.23 páginas
  P9: P(t) = 12.45 páginas

ACUMULADORES   :
  Total llegadas: 16
  Total salidas: 8
  Libros pedidos: 7
  Libros devueltos: 6
  Consultas: 3
  Personas no entraron (cerrada): 0
  Tiempo acum. permanencia: 345.67 min
  Tiempo biblioteca cerrada: 0.00 min
```

## Métricas Finales

Al finalizar la simulación se calculan:

1. **Promedio de permanencia**: Tiempo promedio que cada persona estuvo en la biblioteca
2. **Porcentaje de tiempo cerrada**: Porcentaje del tiempo total que la biblioteca estuvo cerrada por capacidad completa
3. **Personas que no entraron**: Cantidad de personas que llegaron pero no pudieron entrar por estar cerrada

## Exportación a Excel

El sistema genera dos archivos Excel:

1. **simulacion_biblioteca.xlsx**:
   - Hoja "Vector de Estado": Vector completo
   - Hoja "Integraciones Euler": Resumen de integraciones
   - Hoja "Métricas Finales": Resultados finales

2. **integraciones_detalladas.xlsx**:
   - Una hoja por cada persona que leyó
   - Historial completo de la integración paso a paso
   - Útil para graficar curvas de lectura

## Notas Técnicas

- **Semilla aleatoria**: Configurable en [config.py](config.py) para reproducibilidad
- **Límite de iteraciones**: 100,000 o tiempo X, lo que ocurra primero
- **Unidad de integración**: 10 minutos por defecto
- **Distribuciones**: Uniforme para tiempos de consulta/devolución, Exponencial para búsqueda de libros

## Autor

Simulación desarrollada para TP5 - Sistemas de Colas
Implementa todos los lineamientos del enunciado punto B.
