"""
Visualización del vector de estado
"""
from tabulate import tabulate


class VisualizadorVectorEstado:
    """Visualiza el vector de estado de manera formateada"""

    def __init__(self, vector_estado):
        self.vector_estado = vector_estado

    def mostrar_filas(self, inicio, cantidad, mostrar_ultima=True):
        """
        Muestra las filas del vector de estado
        inicio: fila j desde donde comenzar
        cantidad: i filas a mostrar
        mostrar_ultima: si True, también muestra la última fila
        """
        print("\n" + "="*120)
        print("VECTOR DE ESTADO - SIMULACIÓN BIBLIOTECA")
        print("="*120)

        # Mostrar filas desde inicio hasta inicio+cantidad
        filas_a_mostrar = []
        fin = min(inicio + cantidad, len(self.vector_estado))

        for idx in range(inicio, fin):
            if idx < len(self.vector_estado):
                filas_a_mostrar.append(idx)

        # Agregar última fila si se solicita y no está ya incluida
        if mostrar_ultima and len(self.vector_estado) > 0:
            ultima_idx = len(self.vector_estado) - 1
            if ultima_idx not in filas_a_mostrar:
                filas_a_mostrar.append(ultima_idx)

        # Mostrar cada fila
        for idx in filas_a_mostrar:
            self._mostrar_fila_detallada(self.vector_estado[idx])
            print("-" * 120)

        print("\n")

    def _mostrar_fila_detallada(self, fila):
        """Muestra una fila del vector de estado de forma detallada"""
        print(f"\n{'FILA':<15}: {fila.numero_fila}")
        print(f"{'RELOJ':<15}: {fila.reloj:.2f} min")
        print(f"{'EVENTO':<15}: {fila.evento}")

        # Próximos eventos
        print(f"\n{'PRÓXIMOS EVENTOS':<15}:")
        if fila.proximos_eventos:
            for i, evento in enumerate(fila.proximos_eventos[:3], 1):
                print(f"  {i}. {evento['tipo']} a las {evento['tiempo']:.2f} min")
        else:
            print("  (ninguno)")

        # Estado de la biblioteca
        print(f"\n{'BIBLIOTECA':<15}:")
        print(f"  Estado: {'CERRADA' if fila.biblioteca['cerrada'] else 'ABIERTA'}")
        print(f"  Personas dentro: {fila.biblioteca['personas_dentro']}")
        print(f"  En cola: {len(fila.biblioteca['cola_atencion'])} {fila.biblioteca['cola_atencion']}")
        print(f"  Leyendo: {len(fila.biblioteca['personas_leyendo'])} {fila.biblioteca['personas_leyendo']}")

        # Empleados
        print(f"\n{'EMPLEADOS':<15}:")
        for emp in fila.biblioteca['empleados']:
            estado_emp = emp['estado']
            if emp['persona_atendiendo']:
                print(f"  E{emp['id']}: {estado_emp} - Atendiendo {emp['persona_atendiendo']} hasta {emp['hora_fin_atencion']:.2f}")
            else:
                print(f"  E{emp['id']}: {estado_emp}")

        # Randoms utilizados
        if fila.randoms_usados:
            print(f"\n{'RANDOMS USADOS':<15}:")
            for nombre, valor in fila.randoms_usados.items():
                print(f"  {nombre}: {valor:.4f}")

        # Integraciones activas
        if fila.integraciones:
            print(f"\n{'INTEGRACIONES EULER':<15}:")
            for persona_id, integrador in fila.integraciones.items():
                valor_actual = integrador.obtener_valor_actual()
                print(f"  {persona_id}: P(t) = {valor_actual:.2f} páginas")

        # Acumuladores
        print(f"\n{'ACUMULADORES':<15}:")
        print(f"  Total llegadas: {fila.acumuladores['total_personas_llegadas']}")
        print(f"  Total salidas: {fila.acumuladores['total_personas_salidas']}")
        print(f"  Libros pedidos: {fila.acumuladores['total_libros_pedidos']}")
        print(f"  Libros devueltos: {fila.acumuladores['total_libros_devueltos']}")
        print(f"  Consultas: {fila.acumuladores['total_consultas']}")
        print(f"  Personas no entraron (cerrada): {fila.acumuladores['personas_no_entraron_cerrada']}")
        print(f"  Tiempo acum. permanencia: {fila.acumuladores['tiempo_acumulado_permanencia']:.2f} min")
        print(f"  Tiempo biblioteca cerrada: {fila.acumuladores['tiempo_biblioteca_cerrada']:.2f} min")

    def mostrar_resumen_tabla(self, inicio, cantidad, mostrar_ultima=True):
        """Muestra un resumen del vector de estado en formato tabla"""
        filas_a_mostrar = []
        fin = min(inicio + cantidad, len(self.vector_estado))

        for idx in range(inicio, fin):
            if idx < len(self.vector_estado):
                filas_a_mostrar.append(idx)

        if mostrar_ultima and len(self.vector_estado) > 0:
            ultima_idx = len(self.vector_estado) - 1
            if ultima_idx not in filas_a_mostrar:
                filas_a_mostrar.append(ultima_idx)

        # Preparar datos para tabla
        tabla = []
        headers = ["Fila", "Reloj", "Evento", "Personas\nDentro", "Cola", "Leyendo",
                   "Biblioteca", "Llegadas", "Salidas"]

        for idx in filas_a_mostrar:
            fila = self.vector_estado[idx]
            tabla.append([
                fila.numero_fila,
                f"{fila.reloj:.2f}",
                fila.evento[:20],
                fila.biblioteca['personas_dentro'],
                len(fila.biblioteca['cola_atencion']),
                len(fila.biblioteca['personas_leyendo']),
                "CERRADA" if fila.biblioteca['cerrada'] else "ABIERTA",
                fila.acumuladores['total_personas_llegadas'],
                fila.acumuladores['total_personas_salidas']
            ])

        print("\n" + "="*120)
        print("RESUMEN VECTOR DE ESTADO - SIMULACIÓN BIBLIOTECA")
        print("="*120)
        print(tabulate(tabla, headers=headers, tablefmt="grid"))
        print()

    def mostrar_metricas(self, metricas):
        """Muestra las métricas finales calculadas"""
        print("\n" + "="*120)
        print("MÉTRICAS FINALES DE LA SIMULACIÓN")
        print("="*120)
        print(f"\nPromedio de permanencia en biblioteca: {metricas['promedio_permanencia']:.2f} minutos")
        print(f"Porcentaje de tiempo biblioteca cerrada: {metricas['porcentaje_tiempo_cerrada']:.2f}%")
        print(f"\nPersonas que no pudieron entrar (cerrada): {metricas['personas_no_entraron']}")
        print(f"Total personas que llegaron: {metricas['total_personas_llegadas']}")
        print(f"Total personas que salieron: {metricas['total_personas_salidas']}")
        print(f"Tiempo total simulado: {metricas['tiempo_total_simulado']:.2f} minutos")
        print("="*120 + "\n")
