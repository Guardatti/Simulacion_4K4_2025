"""
Motor principal de simulación de la Biblioteca
"""
from config import ConfigSimulacion
from generadores import GeneradorAleatorio, IntegradorEuler
from entidades import *
from eventos import *


class FilaVectorEstado:
    """Representa una fila del vector de estado"""

    def __init__(self, numero_fila, reloj, evento, proximos_eventos, biblioteca,
                 acumuladores, randoms_usados, integraciones, clientes_activos):
        self.numero_fila = numero_fila
        self.reloj = reloj
        self.evento = evento
        self.proximos_eventos = proximos_eventos
        self.biblioteca = biblioteca  # snapshot del estado
        self.acumuladores = acumuladores.copy()
        self.randoms_usados = randoms_usados.copy()
        self.integraciones = integraciones.copy()
        self.clientes_activos = clientes_activos.copy()  # NUEVO: info completa de cada cliente


class Simulador:
    """Motor de simulación del sistema de biblioteca"""

    def __init__(self, config=None):
        self.config = config if config else ConfigSimulacion()
        self.generador = GeneradorAleatorio(self.config.SEMILLA_RANDOM)

        # Estado del sistema
        self.reloj = 0.0
        self.biblioteca = Biblioteca(
            self.config.NUM_EMPLEADOS,
            self.config.CAPACIDAD_MAXIMA
        )

        # Lista de eventos futuros
        self.fel = ListaEventos()

        # Vector de estado (todas las filas)
        self.vector_estado = []
        self.numero_fila = 0

        # Acumuladores y contadores
        self.acumuladores = {
            'total_personas_llegadas': 0,
            'total_personas_salidas': 0,
            'tiempo_acumulado_permanencia': 0.0,
            'tiempo_biblioteca_cerrada': 0.0,
            'ultimo_tiempo_cierre': None,
            'personas_no_entraron_cerrada': 0,
            'total_libros_pedidos': 0,
            'total_libros_devueltos': 0,
            'total_consultas': 0,
            'suma_tiempo_cola': 0.0,
        }

        # Randoms usados en la última iteración
        self.randoms_ultima_iteracion = {}

        # Integraciones activas
        self.integraciones_activas = {}

    def inicializar(self):
        """Inicializa la simulación"""
        # Programar primera llegada
        tiempo_primera_llegada = self.config.TIEMPO_ENTRE_LLEGADAS
        evento_llegada = Evento(TipoEvento.LLEGADA_PERSONA, tiempo_primera_llegada)
        self.fel.agregar_evento(evento_llegada)

        # Programar fin de simulación
        evento_fin = Evento(TipoEvento.FIN_SIMULACION, self.config.TIEMPO_MAXIMO_SIMULACION)
        self.fel.agregar_evento(evento_fin)

        # Guardar estado inicial
        self._guardar_fila_vector_estado(None)

    def ejecutar(self):
        """Ejecuta la simulación completa"""
        self.inicializar()

        while self.fel.tiene_eventos() and self.numero_fila < self.config.MAX_ITERACIONES:
            evento = self.fel.proximo_evento()

            if evento.tipo == TipoEvento.FIN_SIMULACION:
                self.reloj = evento.tiempo
                self._guardar_fila_vector_estado(evento)
                break

            # Avanzar el reloj
            tiempo_anterior = self.reloj
            self.reloj = evento.tiempo

            # Actualizar tiempo de cierre de biblioteca si estaba cerrada
            if self.biblioteca.cerrada and self.acumuladores['ultimo_tiempo_cierre'] is not None:
                self.acumuladores['tiempo_biblioteca_cerrada'] += (self.reloj - tiempo_anterior)

            # Limpiar randoms de iteración anterior
            self.randoms_ultima_iteracion = {}

            # Procesar el evento
            if evento.tipo == TipoEvento.LLEGADA_PERSONA:
                self._procesar_llegada_persona(evento)
            elif evento.tipo == TipoEvento.FIN_ATENCION:
                self._procesar_fin_atencion(evento)
            elif evento.tipo == TipoEvento.FIN_LECTURA:
                self._procesar_fin_lectura(evento)

            # Guardar fila en el vector de estado
            self._guardar_fila_vector_estado(evento)

        return self.vector_estado

    def _procesar_llegada_persona(self, evento):
        """Procesa la llegada de una persona a la biblioteca"""
        # Determinar tipo de acción
        rnd_accion = self.generador.uniforme(0, 1)
        self.randoms_ultima_iteracion['tipo_accion'] = rnd_accion

        if rnd_accion < self.config.PROB_PEDIR_LIBRO:
            tipo_accion = TipoAccion.PEDIR_LIBRO
        elif rnd_accion < (self.config.PROB_PEDIR_LIBRO + self.config.PROB_DEVOLVER_LIBRO):
            tipo_accion = TipoAccion.DEVOLVER_LIBRO
        else:
            tipo_accion = TipoAccion.CONSULTAR

        # Crear persona
        persona = Persona(self.reloj, tipo_accion)
        persona.rnd_tipo_accion = rnd_accion
        self.acumuladores['total_personas_llegadas'] += 1

        # Actualizar contador según tipo de acción
        if tipo_accion == TipoAccion.PEDIR_LIBRO:
            self.acumuladores['total_libros_pedidos'] += 1
        elif tipo_accion == TipoAccion.DEVOLVER_LIBRO:
            self.acumuladores['total_libros_devueltos'] += 1
        else:
            self.acumuladores['total_consultas'] += 1

        # Verificar si puede entrar (biblioteca no cerrada)
        if not self.biblioteca.cerrada:
            self.biblioteca.agregar_a_cola(persona)

            # Intentar atender inmediatamente si hay empleado libre
            if self.biblioteca.hay_empleado_libre() and len(self.biblioteca.cola_atencion) > 0:
                self._iniciar_atencion()

        else:
            # La persona no puede entrar
            persona.estado = EstadoPersona.FUERA
            self.acumuladores['personas_no_entraron_cerrada'] += 1

        # Actualizar estado de cierre
        self.biblioteca.actualizar_estado_cierre()
        if self.biblioteca.cerrada and self.acumuladores['ultimo_tiempo_cierre'] is None:
            self.acumuladores['ultimo_tiempo_cierre'] = self.reloj

        # Programar próxima llegada
        tiempo_proxima_llegada = self.reloj + self.config.TIEMPO_ENTRE_LLEGADAS
        if tiempo_proxima_llegada <= self.config.TIEMPO_MAXIMO_SIMULACION:
            evento_llegada = Evento(TipoEvento.LLEGADA_PERSONA, tiempo_proxima_llegada)
            self.fel.agregar_evento(evento_llegada)

    def _iniciar_atencion(self):
        """Inicia la atención de una persona en cola"""
        if not self.biblioteca.hay_empleado_libre() or len(self.biblioteca.cola_atencion) == 0:
            return

        empleado = self.biblioteca.obtener_empleado_libre()
        persona = self.biblioteca.quitar_de_cola()

        persona.estado = EstadoPersona.SIENDO_ATENDIDA
        persona.hora_inicio_atencion = self.reloj

        # Calcular tiempo de servicio según tipo de acción
        if persona.tipo_accion == TipoAccion.CONSULTAR:
            tiempo_servicio = self.generador.uniforme(
                self.config.TIEMPO_CONSULTA_MIN,
                self.config.TIEMPO_CONSULTA_MAX
            )
            persona.rnd_tiempo_servicio = self.generador.obtener_ultimo_random()
            self.randoms_ultima_iteracion['tiempo_consulta'] = persona.rnd_tiempo_servicio

        elif persona.tipo_accion == TipoAccion.PEDIR_LIBRO:
            tiempo_servicio = self.generador.exponencial(self.config.MEDIA_BUSQUEDA)
            persona.rnd_tiempo_servicio = self.generador.obtener_ultimo_random()
            self.randoms_ultima_iteracion['tiempo_busqueda'] = persona.rnd_tiempo_servicio

        else:  # DEVOLVER_LIBRO
            tiempo_servicio = self.generador.uniforme(
                self.config.TIEMPO_DEVOLUCION_MIN,
                self.config.TIEMPO_DEVOLUCION_MAX
            )
            persona.rnd_tiempo_servicio = self.generador.obtener_ultimo_random()
            self.randoms_ultima_iteracion['tiempo_devolucion'] = persona.rnd_tiempo_servicio

        # Programar fin de atención
        hora_fin_atencion = self.reloj + tiempo_servicio
        persona.hora_fin_atencion = hora_fin_atencion
        empleado.atender(persona, hora_fin_atencion)

        evento_fin = Evento(
            TipoEvento.FIN_ATENCION,
            hora_fin_atencion,
            {'empleado': empleado, 'persona': persona}
        )
        self.fel.agregar_evento(evento_fin)

    def _procesar_fin_atencion(self, evento):
        """Procesa el fin de atención de una persona"""
        empleado = evento.datos['empleado']
        persona = evento.datos['persona']

        # Liberar empleado
        empleado.liberar()

        # Determinar qué hace la persona después
        if persona.tipo_accion == TipoAccion.PEDIR_LIBRO:
            # Generar libro
            num_paginas = int(self.generador.uniforme(self.config.PAGINAS_MIN, self.config.PAGINAS_MAX))
            persona.rnd_paginas = self.generador.obtener_ultimo_random()
            self.randoms_ultima_iteracion['num_paginas'] = persona.rnd_paginas

            libro = Libro(num_paginas)
            persona.libro = libro

            # Decidir si se retira o se queda a leer
            rnd_decision = self.generador.uniforme(0, 1)
            persona.rnd_decision_leer = rnd_decision
            self.randoms_ultima_iteracion['decision_leer'] = rnd_decision

            if rnd_decision < self.config.PROB_RETIRARSE:
                # Se retira con el libro
                persona.estado = EstadoPersona.RETIRÁNDOSE
                persona.hora_salida = self.reloj
                self.biblioteca.persona_sale(persona)
                self.acumuladores['total_personas_salidas'] += 1
                self.acumuladores['tiempo_acumulado_permanencia'] += persona.tiempo_en_sistema()
            else:
                # Se queda a leer
                persona.se_queda_leer = True
                persona.estado = EstadoPersona.LEYENDO
                self.biblioteca.personas_leyendo.append(persona)

                # Crear integrador de Euler para esta persona
                integrador = IntegradorEuler(
                    h=self.config.H_EULER,
                    K=libro.K,
                    p_inicial=0
                )
                persona.integrador_euler = integrador
                self.integraciones_activas[f'P{persona.id}'] = integrador

                # Calcular tiempo de lectura
                tiempo_lectura = self._calcular_tiempo_lectura(libro, integrador)

                # Programar fin de lectura
                hora_fin_lectura = self.reloj + tiempo_lectura
                evento_fin_lectura = Evento(
                    TipoEvento.FIN_LECTURA,
                    hora_fin_lectura,
                    {'persona': persona}
                )
                self.fel.agregar_evento(evento_fin_lectura)

        else:  # DEVOLVER_LIBRO o CONSULTAR
            # La persona se retira
            persona.estado = EstadoPersona.RETIRÁNDOSE
            persona.hora_salida = self.reloj
            self.biblioteca.persona_sale(persona)
            self.acumuladores['total_personas_salidas'] += 1
            self.acumuladores['tiempo_acumulado_permanencia'] += persona.tiempo_en_sistema()

        # Actualizar estado de cierre
        estado_anterior = self.biblioteca.cerrada
        self.biblioteca.actualizar_estado_cierre()

        if estado_anterior and not self.biblioteca.cerrada:
            # La biblioteca se abrió
            self.acumuladores['ultimo_tiempo_cierre'] = None

        # Atender siguiente persona en cola si hay
        if self.biblioteca.hay_empleado_libre() and len(self.biblioteca.cola_atencion) > 0:
            self._iniciar_atencion()

    def _calcular_tiempo_lectura(self, libro, integrador):
        """
        Calcula el tiempo necesario para leer un libro usando integración de Euler
        Resuelve: dP/dt = K/5 hasta que P >= num_paginas
        """
        paginas_objetivo = libro.num_paginas
        tiempo_unidad = self.config.UNIDAD_INTEGRACION
        tiempo_total = 0

        while integrador.obtener_valor_actual() < paginas_objetivo:
            integrador.integrar_hasta(integrador.historial[-1][0] + tiempo_unidad)
            tiempo_total += tiempo_unidad

            if integrador.obtener_valor_actual() >= paginas_objetivo:
                break

        libro.paginas_leidas = integrador.obtener_valor_actual()
        return tiempo_total

    def _procesar_fin_lectura(self, evento):
        """Procesa el fin de lectura de una persona"""
        persona = evento.datos['persona']

        # La persona devuelve el libro y se retira
        persona.estado = EstadoPersona.RETIRÁNDOSE
        persona.hora_salida = self.reloj
        self.biblioteca.persona_sale(persona)

        # Eliminar integración activa
        if f'P{persona.id}' in self.integraciones_activas:
            del self.integraciones_activas[f'P{persona.id}']

        self.acumuladores['total_personas_salidas'] += 1
        self.acumuladores['tiempo_acumulado_permanencia'] += persona.tiempo_en_sistema()

        # Actualizar estado de cierre
        estado_anterior = self.biblioteca.cerrada
        self.biblioteca.actualizar_estado_cierre()

        if estado_anterior and not self.biblioteca.cerrada:
            self.acumuladores['ultimo_tiempo_cierre'] = None

        # Atender siguiente persona en cola si hay
        if self.biblioteca.hay_empleado_libre() and len(self.biblioteca.cola_atencion) > 0:
            self._iniciar_atencion()

    def _guardar_fila_vector_estado(self, evento):
        """Guarda una fila del vector de estado"""
        # Tomar snapshot del estado actual
        snapshot_biblioteca = {
            'cerrada': self.biblioteca.cerrada,
            'cola_atencion': [f'P{p.id}' for p in self.biblioteca.cola_atencion],
            'personas_dentro': len(self.biblioteca.personas_dentro),
            'personas_leyendo': [f'P{p.id}' for p in self.biblioteca.personas_leyendo],
            'empleados': [
                {
                    'id': emp.id,
                    'estado': emp.estado.value,
                    'persona_atendiendo': f'P{emp.persona_atendiendo.id}' if emp.persona_atendiendo else None,
                    'hora_fin_atencion': emp.hora_fin_atencion
                }
                for emp in self.biblioteca.empleados
            ]
        }

        # NUEVO: Recolectar información completa de todos los clientes activos
        clientes_activos = {}

        # Clientes en cola de atención
        for persona in self.biblioteca.cola_atencion:
            clientes_activos[persona.id] = {
                'estado': 'SA',  # En sistema de atención
                'hora_llegada': persona.hora_llegada,
                'tiempo_atencion_alquiler': None,
                'fin_atencion_alquiler_1': None,
                'fin_atencion_alquiler_2': None,
                'rnd_alquiler': None,
                'se_queda': None,
                'fin_lectura_1': None,
                'fin_lectura_2': None,
                'fin_lectura_3': None,
                'rnd_lectura': None,
                'tiempo_atencion_devolucion': None,
                'fin_atencion_devolucion_1': None,
                'fin_atencion_devolucion_2': None,
                'rnd_devolucion': None,
                'tiempo_atencion_consulta': None,
                'fin_atencion_consulta': None,
                'rnd_consulta': None
            }

        # Clientes siendo atendidos
        for empleado in self.biblioteca.empleados:
            if empleado.persona_atendiendo:
                persona = empleado.persona_atendiendo
                tiempo_restante = empleado.hora_fin_atencion - self.reloj if empleado.hora_fin_atencion else None

                info_cliente = {
                    'estado': 'SA',
                    'hora_llegada': persona.hora_llegada,
                    'tiempo_atencion_alquiler': None,
                    'fin_atencion_alquiler_1': None,
                    'fin_atencion_alquiler_2': None,
                    'rnd_alquiler': None,
                    'se_queda': None,
                    'fin_lectura_1': None,
                    'fin_lectura_2': None,
                    'fin_lectura_3': None,
                    'rnd_lectura': None,
                    'tiempo_atencion_devolucion': None,
                    'fin_atencion_devolucion_1': None,
                    'fin_atencion_devolucion_2': None,
                    'rnd_devolucion': None,
                    'tiempo_atencion_consulta': None,
                    'fin_atencion_consulta': None,
                    'rnd_consulta': None
                }

                # Llenar según el tipo de acción
                if persona.tipo_accion == TipoAccion.PEDIR_LIBRO:
                    info_cliente['tiempo_atencion_alquiler'] = tiempo_restante
                    info_cliente['fin_atencion_alquiler_1'] = empleado.hora_fin_atencion
                    info_cliente['rnd_alquiler'] = persona.rnd_tiempo_servicio if hasattr(persona, 'rnd_tiempo_servicio') else None
                elif persona.tipo_accion == TipoAccion.DEVOLVER_LIBRO:
                    info_cliente['tiempo_atencion_devolucion'] = tiempo_restante
                    info_cliente['fin_atencion_devolucion_1'] = empleado.hora_fin_atencion
                    info_cliente['rnd_devolucion'] = persona.rnd_tiempo_servicio if hasattr(persona, 'rnd_tiempo_servicio') else None
                elif persona.tipo_accion == TipoAccion.CONSULTAR:
                    info_cliente['tiempo_atencion_consulta'] = tiempo_restante
                    info_cliente['fin_atencion_consulta'] = empleado.hora_fin_atencion
                    info_cliente['rnd_consulta'] = persona.rnd_tiempo_servicio if hasattr(persona, 'rnd_tiempo_servicio') else None

                clientes_activos[persona.id] = info_cliente

        # Clientes leyendo
        for persona in self.biblioteca.personas_leyendo:
            paginas_leidas = None
            if persona.integrador_euler:
                paginas_leidas = persona.integrador_euler.obtener_valor_actual()

            clientes_activos[persona.id] = {
                'estado': 'Leyendo',
                'hora_llegada': persona.hora_llegada,
                'tiempo_atencion_alquiler': None,
                'fin_atencion_alquiler_1': None,
                'fin_atencion_alquiler_2': None,
                'rnd_alquiler': persona.rnd_tiempo_servicio if hasattr(persona, 'rnd_tiempo_servicio') else None,
                'se_queda': 1 if persona.se_queda_leer else 0,
                'fin_lectura_1': paginas_leidas,
                'fin_lectura_2': None,
                'fin_lectura_3': None,
                'rnd_lectura': persona.rnd_paginas if hasattr(persona, 'rnd_paginas') else None,
                'tiempo_atencion_devolucion': None,
                'fin_atencion_devolucion_1': None,
                'fin_atencion_devolucion_2': None,
                'rnd_devolucion': None,
                'tiempo_atencion_consulta': None,
                'fin_atencion_consulta': None,
                'rnd_consulta': None
            }

        proximos = self.fel.obtener_proximos_eventos(5)
        proximos_eventos = [
            {'tipo': e.tipo.value, 'tiempo': e.tiempo}
            for e in proximos
        ]

        fila = FilaVectorEstado(
            numero_fila=self.numero_fila,
            reloj=self.reloj,
            evento=evento.tipo.value if evento else "Inicio",
            proximos_eventos=proximos_eventos,
            biblioteca=snapshot_biblioteca,
            acumuladores=self.acumuladores,
            randoms_usados=self.randoms_ultima_iteracion,
            integraciones=self.integraciones_activas,
            clientes_activos=clientes_activos  # NUEVO
        )

        self.vector_estado.append(fila)
        self.numero_fila += 1

    def calcular_metricas_finales(self):
        """Calcula las métricas solicitadas en el enunciado"""
        metricas = {}

        # Promedio de permanencia
        if self.acumuladores['total_personas_salidas'] > 0:
            metricas['promedio_permanencia'] = (
                self.acumuladores['tiempo_acumulado_permanencia'] /
                self.acumuladores['total_personas_salidas']
            )
        else:
            metricas['promedio_permanencia'] = 0

        # Porcentaje de tiempo que la biblioteca estuvo cerrada
        if self.reloj > 0:
            metricas['porcentaje_tiempo_cerrada'] = (
                (self.acumuladores['tiempo_biblioteca_cerrada'] / self.reloj) * 100
            )
        else:
            metricas['porcentaje_tiempo_cerrada'] = 0

        metricas['personas_no_entraron'] = self.acumuladores['personas_no_entraron_cerrada']
        metricas['total_personas_llegadas'] = self.acumuladores['total_personas_llegadas']
        metricas['total_personas_salidas'] = self.acumuladores['total_personas_salidas']
        metricas['tiempo_total_simulado'] = self.reloj

        return metricas
