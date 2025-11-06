"""
Este es el método _actualizar_tabla() final que debe reemplazar al existente en gui_biblioteca_v2.py
Formato EXACTO según imagen adjunta con colores diferenciados
"""

def _actualizar_tabla(self):
    """Actualiza la tabla del vector de estado con formato EXACTO de imagen"""
    if not self.vector_estado:
        return

    # Limpiar tabla
    for item in self.tree_vector.get_children():
        self.tree_vector.delete(item)

    # Determinar filas a mostrar
    inicio = int(self.config.HORA_INICIO_MOSTRAR)
    fin = min(inicio + self.config.FILAS_A_MOSTRAR, len(self.vector_estado))
    filas_a_mostrar = list(range(inicio, fin))

    # Agregar última fila si no está incluida
    ultima_idx = len(self.vector_estado) - 1
    if ultima_idx not in filas_a_mostrar and ultima_idx >= 0:
        filas_a_mostrar.append(ultima_idx)

    # Recolectar todos los IDs de clientes
    todos_clientes = set()
    for idx in filas_a_mostrar:
        fila = self.vector_estado[idx]
        if hasattr(fila, 'clientes_activos'):
            todos_clientes.update(fila.clientes_activos.keys())

    # Limitar a max_clientes_visible más recientes
    clientes_a_mostrar = sorted(list(todos_clientes))[-self.max_clientes_visible:]

    # === CONSTRUCCIÓN DE COLUMNAS ===
    columnas = []

    # Columnas básicas del sistema
    columnas.extend([
        ("Tiempo_entre_llegadas", "sistema", 100),
        ("Prox_llegada", "sistema", 90),
        ("RND_llegada", "sistema", 80),
        ("Evento", "sistema", 100),
        ("Reloj", "sistema", 70)
    ])

    # Columnas por cliente (OBJETOS TEMPORALES - Naranja)
    for cliente_id in clientes_a_mostrar:
        columnas.extend([
            (f"C{cliente_id}_Estado", "temporal", 60),
            (f"C{cliente_id}_H_Lleg", "temporal", 70),
            (f"C{cliente_id}_T_Aten_Alq", "temporal", 80),
            (f"C{cliente_id}_Fin_Alq1", "temporal", 75),
            (f"C{cliente_id}_Fin_Alq2", "temporal", 75),
            (f"C{cliente_id}_RND_Alq", "temporal", 70),
            (f"C{cliente_id}_Se_Queda", "temporal", 70),
            (f"C{cliente_id}_Fin_Lec1", "temporal", 75),
            (f"C{cliente_id}_Fin_Lec2", "temporal", 75),
            (f"C{cliente_id}_Fin_Lec3", "temporal", 75),
            (f"C{cliente_id}_RND_Lec", "temporal", 70),
            (f"C{cliente_id}_T_Aten_Dev", "temporal", 80),
            (f"C{cliente_id}_Fin_Dev1", "temporal", 75),
            (f"C{cliente_id}_Fin_Dev2", "temporal", 75),
            (f"C{cliente_id}_RND_Dev", "temporal", 70),
            (f"C{cliente_id}_T_Aten_Con", "temporal", 80),
            (f"C{cliente_id}_Fin_Con", "temporal", 75),
            (f"C{cliente_id}_RND_Con", "temporal", 70)
        ])

    # Columnas de empleados (OBJETOS PERMANENTES - Verde)
    columnas.extend([
        ("E1_Estado", "permanente", 70),
        ("E2_Estado", "permanente", 70)
    ])

    # Columnas de cola (COLAS - Azul)
    columnas.extend([
        ("Cola", "cola", 60),
        ("Leyendo", "cola", 70)
    ])

    # Configurar columnas del Treeview
    nombres_columnas = [c[0] for c in columnas]
    self.tree_vector.configure(columns=nombres_columnas)

    # Configurar headers con colores
    for nombre_col, tipo_col, ancho in columnas:
        # Texto del header (simplificado)
        texto_header = nombre_col.replace("_", " ").replace("C", "Cliente ")

        self.tree_vector.heading(nombre_col, text=texto_header)
        self.tree_vector.column(nombre_col, width=ancho, anchor='center')

    # Configurar tags de color para headers (esto es limitado en Tkinter standard)
    # Los colores de fondo de headers requieren una solución personalizada
    # Por ahora, aplicamos colores a las celdas

    # Tags para celdas
    self.tree_vector.tag_configure('evenrow', background='#FFFFFF')
    self.tree_vector.tag_configure('oddrow', background='#F5F5F5')
    self.tree_vector.tag_configure('lastrow', background='#FFFF00', font=('Segoe UI', 9, 'bold'))

    # === INSERTAR FILAS ===
    for fila_idx, idx in enumerate(filas_a_mostrar):
        fila = self.vector_estado[idx]
        valores = []

        # Valores básicos del sistema
        tiempo_entre_llegadas = self.config.TIEMPO_ENTRE_LLEGADAS
        prox_llegada = ""
        rnd_llegada = ""

        if fila.proximos_eventos:
            for evento in fila.proximos_eventos:
                if "Llegada" in evento['tipo']:
                    prox_llegada = f"{evento['tiempo']:.2f}"
                    break

        valores.extend([
            f"{tiempo_entre_llegadas:.2f}",
            prox_llegada,
            rnd_llegada,
            fila.evento[:15],
            f"{fila.reloj:.2f}"
        ])

        # Valores por cliente
        for cliente_id in clientes_a_mostrar:
            if hasattr(fila, 'clientes_activos') and cliente_id in fila.clientes_activos:
                c = fila.clientes_activos[cliente_id]

                # Formato de valores: SOLO NÚMEROS
                def fmt(val):
                    if val is None:
                        return ""
                    if isinstance(val, (int, float)):
                        if isinstance(val, float):
                            return f"{val:.2f}"
                        else:
                            return str(val)
                    return str(val)

                valores.extend([
                    c['estado'] if c['estado'] else "",  # Estado
                    fmt(c['hora_llegada']),               # Hora llegada
                    fmt(c['tiempo_atencion_alquiler']),   # Tiempo atención alquiler
                    fmt(c['fin_atencion_alquiler_1']),    # Fin atención alq 1
                    fmt(c['fin_atencion_alquiler_2']),    # Fin atención alq 2
                    fmt(c['rnd_alquiler']),               # RND alquiler (SOLO NÚMERO)
                    fmt(c['se_queda']),                   # Se queda (1 o vacío)
                    fmt(c['fin_lectura_1']),              # Fin lectura 1
                    fmt(c['fin_lectura_2']),              # Fin lectura 2
                    fmt(c['fin_lectura_3']),              # Fin lectura 3
                    fmt(c['rnd_lectura']),                # RND lectura (SOLO NÚMERO)
                    fmt(c['tiempo_atencion_devolucion']), # Tiempo atención devolución
                    fmt(c['fin_atencion_devolucion_1']),  # Fin atención dev 1
                    fmt(c['fin_atencion_devolucion_2']),  # Fin atención dev 2
                    fmt(c['rnd_devolucion']),             # RND devolución (SOLO NÚMERO)
                    fmt(c['tiempo_atencion_consulta']),   # Tiempo atención consulta
                    fmt(c['fin_atencion_consulta']),      # Fin atención consulta
                    fmt(c['rnd_consulta'])                # RND consulta (SOLO NÚMERO)
                ])
            else:
                # Cliente no presente en esta fila
                valores.extend([""] * 18)

        # Valores de empleados
        if fila.biblioteca['empleados']:
            valores.append(fila.biblioteca['empleados'][0]['estado'][:6])
            valores.append(fila.biblioteca['empleados'][1]['estado'][:6] if len(fila.biblioteca['empleados']) > 1 else "")
        else:
            valores.extend(["", ""])

        # Valores de colas
        valores.append(len(fila.biblioteca['cola_atencion']))
        valores.append(len(fila.biblioteca['personas_leyendo']))

        # Determinar tag
        if idx == ultima_idx and idx != filas_a_mostrar[0]:
            tag = 'lastrow'
        else:
            tag = 'evenrow' if fila_idx % 2 == 0 else 'oddrow'

        self.tree_vector.insert('', 'end', values=valores, tags=(tag,))

    print(f"Tabla actualizada: {len(filas_a_mostrar)} filas, {len(clientes_a_mostrar)} clientes")


# NOTA IMPORTANTE:
# Tkinter Treeview NO permite aplicar colores de fondo a los headers directamente.
# Para tener headers con colores como en la imagen, se necesita una solución personalizada:

# SOLUCIÓN PROPUESTA:
# Crear un frame superior con labels que simulen los headers con colores,
# y debajo poner el Treeview sin headers (show='tree' en lugar de show='headings')

# Ver método _crear_tabla_con_headers_coloreados() más abajo
