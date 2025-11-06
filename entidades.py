"""
Entidades del sistema: Persona, Empleado, Libro, Biblioteca
"""
from enum import Enum

class EstadoPersona(Enum):
    """Estados posibles de una persona en el sistema"""
    EN_COLA = "En Cola"
    SIENDO_ATENDIDA = "Siendo Atendida"
    LEYENDO = "Leyendo"
    RETIRÁNDOSE = "Retirándose"
    FUERA = "Fuera del Sistema"


class TipoAccion(Enum):
    """Tipo de acción que quiere realizar una persona"""
    PEDIR_LIBRO = "Pedir Libro"
    DEVOLVER_LIBRO = "Devolver Libro"
    CONSULTAR = "Consultar Condiciones"


class EstadoEmpleado(Enum):
    """Estados posibles de un empleado"""
    LIBRE = "Libre"
    OCUPADO = "Ocupado"


class Persona:
    """Representa una persona que llega a la biblioteca"""
    contador = 0

    def __init__(self, hora_llegada, tipo_accion):
        Persona.contador += 1
        self.id = Persona.contador
        self.hora_llegada = hora_llegada
        self.tipo_accion = tipo_accion
        self.estado = EstadoPersona.EN_COLA
        self.hora_inicio_atencion = None
        self.hora_fin_atencion = None
        self.hora_salida = None
        self.libro = None
        self.se_queda_leer = False
        self.integrador_euler = None
        self.rnd_tipo_accion = None
        self.rnd_tiempo_servicio = None
        self.rnd_decision_leer = None
        self.rnd_paginas = None

    def tiempo_en_sistema(self):
        """Calcula el tiempo total que la persona estuvo en el sistema"""
        if self.hora_salida:
            return self.hora_salida - self.hora_llegada
        return None

    def __str__(self):
        return f"P{self.id}"

    def __repr__(self):
        return f"Persona(id={self.id}, accion={self.tipo_accion.value}, estado={self.estado.value})"


class Empleado:
    """Representa un empleado del mostrador"""

    def __init__(self, id_empleado):
        self.id = id_empleado
        self.estado = EstadoEmpleado.LIBRE
        self.persona_atendiendo = None
        self.hora_fin_atencion = None

    def esta_libre(self):
        return self.estado == EstadoEmpleado.LIBRE

    def atender(self, persona, hora_fin):
        self.estado = EstadoEmpleado.OCUPADO
        self.persona_atendiendo = persona
        self.hora_fin_atencion = hora_fin

    def liberar(self):
        self.estado = EstadoEmpleado.LIBRE
        persona_atendida = self.persona_atendiendo
        self.persona_atendiendo = None
        self.hora_fin_atencion = None
        return persona_atendida

    def __str__(self):
        return f"E{self.id}"

    def __repr__(self):
        return f"Empleado(id={self.id}, estado={self.estado.value})"


class Libro:
    """Representa un libro de la biblioteca"""
    contador = 0

    def __init__(self, num_paginas):
        Libro.contador += 1
        self.id = Libro.contador
        self.num_paginas = num_paginas
        self.paginas_leidas = 0
        self.K = self._determinar_K()

    def _determinar_K(self):
        """Determina el valor de K según el número de páginas"""
        if 100 <= self.num_paginas <= 200:
            return 100
        elif 200 < self.num_paginas <= 300:
            return 90
        else:  # más de 300
            return 70

    def lectura_completa(self):
        """Verifica si se completó la lectura del libro"""
        return self.paginas_leidas >= self.num_paginas

    def __str__(self):
        return f"L{self.id}"

    def __repr__(self):
        return f"Libro(id={self.id}, paginas={self.num_paginas}, K={self.K})"


class Biblioteca:
    """Representa el estado de la biblioteca"""

    def __init__(self, num_empleados, capacidad_maxima):
        self.empleados = [Empleado(i+1) for i in range(num_empleados)]
        self.capacidad_maxima = capacidad_maxima
        self.cola_atencion = []
        self.personas_leyendo = []
        self.personas_dentro = []  # todas las personas dentro de la biblioteca
        self.cerrada = False

    def cantidad_personas_dentro(self):
        """Retorna la cantidad de personas dentro de la biblioteca"""
        return len(self.personas_dentro)

    def hay_empleado_libre(self):
        """Verifica si hay algún empleado libre"""
        return any(emp.esta_libre() for emp in self.empleados)

    def obtener_empleado_libre(self):
        """Retorna el primer empleado libre disponible"""
        for emp in self.empleados:
            if emp.esta_libre():
                return emp
        return None

    def agregar_a_cola(self, persona):
        """Agrega una persona a la cola de atención"""
        self.cola_atencion.append(persona)
        if persona not in self.personas_dentro:
            self.personas_dentro.append(persona)

    def quitar_de_cola(self):
        """Quita y retorna la primera persona de la cola"""
        if self.cola_atencion:
            return self.cola_atencion.pop(0)
        return None

    def actualizar_estado_cierre(self):
        """Actualiza el estado de cierre de la biblioteca"""
        if self.cantidad_personas_dentro() >= self.capacidad_maxima:
            self.cerrada = True
        elif self.cantidad_personas_dentro() < self.capacidad_maxima:
            self.cerrada = False

    def persona_sale(self, persona):
        """Registra que una persona sale de la biblioteca"""
        if persona in self.personas_dentro:
            self.personas_dentro.remove(persona)
        if persona in self.personas_leyendo:
            self.personas_leyendo.remove(persona)
        self.actualizar_estado_cierre()
