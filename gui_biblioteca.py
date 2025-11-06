"""
Interfaz Gráfica para la Simulación de Biblioteca
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from config import ConfigSimulacion
from simulador import Simulador
from exportador import ExportadorExcel


class BibliotecaGUI:
    """Interfaz gráfica principal"""

    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Sistema de Biblioteca - TP5 SIM")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # Variables
        self.config = ConfigSimulacion()
        self.simulador = None
        self.vector_estado = None
        self.metricas = None
        self.simulacion_en_progreso = False

        # Configurar estilo
        self._configurar_estilos()

        # Crear interfaz
        self._crear_menu()
        self._crear_interfaz()

    def _configurar_estilos(self):
        """Configura los estilos de ttk"""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo para botones
        style.configure('Primary.TButton',
                       background='#0078D4',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=10,
                       font=('Segoe UI', 10, 'bold'))

        style.map('Primary.TButton',
                 background=[('active', '#005A9E')])

        # Estilo para frames
        style.configure('Card.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=1)

        # Estilo para labels
        style.configure('Title.TLabel',
                       background='white',
                       font=('Segoe UI', 12, 'bold'),
                       foreground='#333333')

        style.configure('Subtitle.TLabel',
                       background='white',
                       font=('Segoe UI', 10),
                       foreground='#666666')

    def _crear_menu(self):
        """Crea el menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Exportar a Excel", command=self._exportar_excel)
        menu_archivo.add_command(label="Exportar Integraciones", command=self._exportar_integraciones)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)

        # Menú Ver
        menu_ver = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=menu_ver)
        menu_ver.add_command(label="Actualizar Tabla", command=self._actualizar_tabla)
        menu_ver.add_command(label="Actualizar Gráficos", command=self._actualizar_graficos)

        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self._mostrar_acerca_de)

    def _crear_interfaz(self):
        """Crea la interfaz principal"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(1, weight=1)

        # Panel izquierdo - Configuración
        self._crear_panel_configuracion(main_frame)

        # Panel derecho - Resultados
        self._crear_panel_resultados(main_frame)

    def _crear_panel_configuracion(self, parent):
        """Crea el panel de configuración de parámetros"""
        config_frame = ttk.LabelFrame(parent, text="⚙ Configuración de Parámetros",
                                      padding="15", style='Card.TFrame')
        config_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Canvas con scrollbar para muchos parámetros
        canvas = tk.Canvas(config_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Variables de parámetros
        self.vars_params = {}

        # Parámetros de simulación
        params_sim = [
            ("Tiempo Máximo (min)", "TIEMPO_MAXIMO_SIMULACION", 480),
            ("Max Iteraciones", "MAX_ITERACIONES", 100000),
            ("Fila Inicio (j)", "HORA_INICIO_MOSTRAR", 0),
            ("Filas a Mostrar (i)", "FILAS_A_MOSTRAR", 50),
        ]

        ttk.Label(scrollable_frame, text="Parámetros de Simulación",
                 style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        for idx, (label, key, default) in enumerate(params_sim, 1):
            ttk.Label(scrollable_frame, text=label + ":",
                     style='Subtitle.TLabel').grid(row=idx, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=str(default))
            self.vars_params[key] = var
            entry = ttk.Entry(scrollable_frame, textvariable=var, width=15)
            entry.grid(row=idx, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Parámetros del sistema
        row_offset = len(params_sim) + 2
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row_offset-1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(scrollable_frame, text="Parámetros del Sistema",
                 style='Title.TLabel').grid(row=row_offset, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        params_sistema = [
            ("Tiempo Entre Llegadas (min)", "TIEMPO_ENTRE_LLEGADAS", 4),
            ("Prob. Pedir Libro", "PROB_PEDIR_LIBRO", 0.45),
            ("Prob. Devolver Libro", "PROB_DEVOLVER_LIBRO", 0.45),
            ("Prob. Consultar", "PROB_CONSULTAR", 0.10),
            ("Tiempo Consulta Min (min)", "TIEMPO_CONSULTA_MIN", 2),
            ("Tiempo Consulta Max (min)", "TIEMPO_CONSULTA_MAX", 5),
            ("Media Búsqueda EXP (min)", "MEDIA_BUSQUEDA", 6),
            ("Prob. Retirarse", "PROB_RETIRARSE", 0.60),
        ]

        for idx, (label, key, default) in enumerate(params_sistema, row_offset + 1):
            ttk.Label(scrollable_frame, text=label + ":",
                     style='Subtitle.TLabel').grid(row=idx, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=str(default))
            self.vars_params[key] = var
            entry = ttk.Entry(scrollable_frame, textvariable=var, width=15)
            entry.grid(row=idx, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Parámetros de integración
        row_offset = row_offset + len(params_sistema) + 2
        ttk.Separator(scrollable_frame, orient='horizontal').grid(
            row=row_offset-1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(scrollable_frame, text="Parámetros de Integración",
                 style='Title.TLabel').grid(row=row_offset, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        params_integracion = [
            ("K (100-200 pág)", "K_100_200_PAG", 100),
            ("K (200-300 pág)", "K_200_300_PAG", 90),
            ("K (>300 pág)", "K_MAS_300_PAG", 70),
            ("Páginas Min", "PAGINAS_MIN", 100),
            ("Páginas Max", "PAGINAS_MAX", 350),
            ("Paso Euler (h)", "H_EULER", 0.1),
            ("Capacidad Máxima", "CAPACIDAD_MAXIMA", 20),
        ]

        for idx, (label, key, default) in enumerate(params_integracion, row_offset + 1):
            ttk.Label(scrollable_frame, text=label + ":",
                     style='Subtitle.TLabel').grid(row=idx, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=str(default))
            self.vars_params[key] = var
            entry = ttk.Entry(scrollable_frame, textvariable=var, width=15)
            entry.grid(row=idx, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        config_frame.rowconfigure(0, weight=1)
        config_frame.columnconfigure(0, weight=1)

        # Botón de ejecutar
        btn_frame = ttk.Frame(config_frame, style='Card.TFrame')
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(15, 0))

        self.btn_ejecutar = ttk.Button(btn_frame, text="▶ Ejecutar Simulación",
                                       command=self._ejecutar_simulacion,
                                       style='Primary.TButton',
                                       width=25)
        self.btn_ejecutar.pack()

        # Barra de progreso
        self.progress = ttk.Progressbar(config_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def _crear_panel_resultados(self, parent):
        """Crea el panel de resultados"""
        results_frame = ttk.Frame(parent)
        results_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)

        # Header con métricas
        self._crear_header_metricas(results_frame)

        # Notebook para tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

        # Tab 1: Vector de Estado
        self._crear_tab_vector_estado()

        # Tab 2: Gráficos de Integración
        self._crear_tab_integracion()

        # Tab 3: Análisis
        self._crear_tab_analisis()

    def _crear_header_metricas(self, parent):
        """Crea el header con las métricas principales"""
        header = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=1)
        header.columnconfigure(3, weight=1)

        # Métricas
        self.lbl_tiempo_sim = self._crear_metrica_card(header, "⏱ Tiempo Simulado", "0.00 min", 0)
        self.lbl_personas = self._crear_metrica_card(header, "👥 Personas", "L: 0 | S: 0", 1)
        self.lbl_permanencia = self._crear_metrica_card(header, "📊 Prom. Permanencia", "0.00 min", 2)
        self.lbl_cerrada = self._crear_metrica_card(header, "🔒 Tiempo Cerrada", "0.00%", 3)

    def _crear_metrica_card(self, parent, titulo, valor, columna):
        """Crea una tarjeta de métrica"""
        card = ttk.Frame(parent, style='Card.TFrame', padding="10")
        card.grid(row=0, column=columna, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(card, text=titulo, style='Subtitle.TLabel').pack()
        lbl_valor = ttk.Label(card, text=valor, font=('Segoe UI', 14, 'bold'),
                             background='white', foreground='#0078D4')
        lbl_valor.pack()

        return lbl_valor

    def _crear_tab_vector_estado(self):
        """Crea el tab del vector de estado"""
        tab_vector = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(tab_vector, text="📋 Vector de Estado")

        # Toolbar
        toolbar = ttk.Frame(tab_vector, style='Card.TFrame')
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(toolbar, text="Ir a fila:", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.entry_fila = ttk.Entry(toolbar, width=10)
        self.entry_fila.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar, text="🔍 Buscar", command=self._buscar_fila).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⬆ Primera", command=self._ir_primera_fila).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⬇ Última", command=self._ir_ultima_fila).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Actualizar", command=self._actualizar_tabla).pack(side=tk.LEFT, padx=2)

        # Frame con scrollbars para la tabla
        table_frame = ttk.Frame(tab_vector)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")

        # Treeview para mostrar el vector de estado
        columns = ("Fila", "Reloj", "Evento", "Prox_Evento", "Tiempo_Prox",
                  "Personas_Dentro", "Cola", "Leyendo", "Estado_Bib",
                  "E1_Estado", "E1_Atendiendo", "E2_Estado", "E2_Atendiendo",
                  "Llegadas", "Salidas", "L_Pedidos", "L_Devueltos", "Consultas",
                  "RND_usado", "Integraciones")

        self.tree_vector = ttk.Treeview(table_frame, columns=columns, show='headings',
                                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.tree_vector.yview)
        hsb.config(command=self.tree_vector.xview)

        # Configurar columnas
        column_widths = {
            "Fila": 60, "Reloj": 80, "Evento": 120, "Prox_Evento": 120, "Tiempo_Prox": 90,
            "Personas_Dentro": 80, "Cola": 60, "Leyendo": 70, "Estado_Bib": 90,
            "E1_Estado": 80, "E1_Atendiendo": 100, "E2_Estado": 80, "E2_Atendiendo": 100,
            "Llegadas": 70, "Salidas": 70, "L_Pedidos": 80, "L_Devueltos": 80, "Consultas": 70,
            "RND_usado": 100, "Integraciones": 120
        }

        for col in columns:
            self.tree_vector.heading(col, text=col.replace("_", " "))
            self.tree_vector.column(col, width=column_widths.get(col, 100), anchor='center')

        # Grid
        self.tree_vector.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Etiquetas de estilo para filas
        self.tree_vector.tag_configure('evenrow', background='#f9f9f9')
        self.tree_vector.tag_configure('oddrow', background='white')
        self.tree_vector.tag_configure('lastrow', background='#fff4ce', font=('Segoe UI', 9, 'bold'))

    def _crear_tab_integracion(self):
        """Crea el tab de gráficos de integración"""
        tab_integracion = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(tab_integracion, text="📈 Integración Numérica")

        # Frame para controles
        control_frame = ttk.Frame(tab_integracion, style='Card.TFrame')
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(control_frame, text="Seleccionar Persona:",
                 style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(0, 10))

        self.combo_personas = ttk.Combobox(control_frame, state='readonly', width=15)
        self.combo_personas.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_personas.bind('<<ComboboxSelected>>', lambda e: self._actualizar_grafico_integracion())

        ttk.Button(control_frame, text="🔄 Actualizar",
                  command=self._actualizar_graficos).pack(side=tk.LEFT)

        # Frame para el gráfico
        self.frame_grafico_integracion = ttk.Frame(tab_integracion)
        self.frame_grafico_integracion.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _crear_tab_analisis(self):
        """Crea el tab de análisis y gráficos generales"""
        tab_analisis = ttk.Frame(self.notebook, style='Card.TFrame')
        self.notebook.add(tab_analisis, text="📊 Análisis")

        # Frame para gráficos
        self.frame_graficos_analisis = ttk.Frame(tab_analisis)
        self.frame_graficos_analisis.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _aplicar_configuracion(self):
        """Aplica la configuración ingresada"""
        try:
            for key, var in self.vars_params.items():
                value = var.get()
                if '.' in value or 'EULER' in key:
                    setattr(self.config, key, float(value))
                else:
                    setattr(self.config, key, int(float(value)))
            return True
        except ValueError as e:
            messagebox.showerror("Error", f"Valor inválido en configuración:\n{str(e)}")
            return False

    def _ejecutar_simulacion(self):
        """Ejecuta la simulación en un thread separado"""
        if self.simulacion_en_progreso:
            messagebox.showwarning("Aviso", "Ya hay una simulación en progreso")
            return

        if not self._aplicar_configuracion():
            return

        # Deshabilitar botón y mostrar progreso
        self.btn_ejecutar.config(state='disabled')
        self.progress.start(10)
        self.simulacion_en_progreso = True

        # Ejecutar en thread separado
        thread = threading.Thread(target=self._ejecutar_simulacion_thread, daemon=True)
        thread.start()

    def _ejecutar_simulacion_thread(self):
        """Thread que ejecuta la simulación"""
        try:
            # Crear simulador
            self.simulador = Simulador(self.config)

            # Ejecutar
            self.vector_estado = self.simulador.ejecutar()

            # Calcular métricas
            self.metricas = self.simulador.calcular_metricas_finales()

            # Actualizar UI en el thread principal
            self.root.after(0, self._simulacion_completada)

        except Exception as e:
            self.root.after(0, lambda: self._simulacion_error(str(e)))

    def _simulacion_completada(self):
        """Callback cuando la simulación se completa"""
        self.progress.stop()
        self.btn_ejecutar.config(state='normal')
        self.simulacion_en_progreso = False

        # Actualizar métricas
        self._actualizar_metricas()

        # Actualizar tabla
        self._actualizar_tabla()

        # Actualizar gráficos
        self._actualizar_graficos()

        messagebox.showinfo("Éxito",
                           f"Simulación completada!\n\n"
                           f"Filas generadas: {len(self.vector_estado)}\n"
                           f"Tiempo simulado: {self.simulador.reloj:.2f} min")

    def _simulacion_error(self, error_msg):
        """Callback cuando hay un error en la simulación"""
        self.progress.stop()
        self.btn_ejecutar.config(state='normal')
        self.simulacion_en_progreso = False
        messagebox.showerror("Error", f"Error en la simulación:\n{error_msg}")

    def _actualizar_metricas(self):
        """Actualiza las métricas en el header"""
        if self.metricas:
            self.lbl_tiempo_sim.config(text=f"{self.metricas['tiempo_total_simulado']:.2f} min")
            self.lbl_personas.config(
                text=f"L: {self.metricas['total_personas_llegadas']} | "
                     f"S: {self.metricas['total_personas_salidas']}"
            )
            self.lbl_permanencia.config(text=f"{self.metricas['promedio_permanencia']:.2f} min")
            self.lbl_cerrada.config(text=f"{self.metricas['porcentaje_tiempo_cerrada']:.2f}%")

    def _actualizar_tabla(self):
        """Actualiza la tabla del vector de estado"""
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

        # Insertar filas
        for idx in filas_a_mostrar:
            fila = self.vector_estado[idx]

            # Próximo evento
            prox_evento = ""
            tiempo_prox = ""
            if fila.proximos_eventos:
                prox_evento = fila.proximos_eventos[0]['tipo'][:20]
                tiempo_prox = f"{fila.proximos_eventos[0]['tiempo']:.2f}"

            # Randoms usados
            rnd_texto = ""
            if fila.randoms_usados:
                rnd_texto = ", ".join([f"{k}:{v:.3f}" for k, v in list(fila.randoms_usados.items())[:2]])

            # Integraciones
            int_texto = ""
            if fila.integraciones:
                int_texto = ", ".join([f"{k}:{v.obtener_valor_actual():.1f}p"
                                      for k, v in list(fila.integraciones.items())[:2]])

            valores = (
                fila.numero_fila,
                f"{fila.reloj:.2f}",
                fila.evento[:20],
                prox_evento,
                tiempo_prox,
                fila.biblioteca['personas_dentro'],
                len(fila.biblioteca['cola_atencion']),
                len(fila.biblioteca['personas_leyendo']),
                "CERRADA" if fila.biblioteca['cerrada'] else "ABIERTA",
                fila.biblioteca['empleados'][0]['estado'][:10],
                fila.biblioteca['empleados'][0]['persona_atendiendo'] or "",
                fila.biblioteca['empleados'][1]['estado'][:10],
                fila.biblioteca['empleados'][1]['persona_atendiendo'] or "",
                fila.acumuladores['total_personas_llegadas'],
                fila.acumuladores['total_personas_salidas'],
                fila.acumuladores['total_libros_pedidos'],
                fila.acumuladores['total_libros_devueltos'],
                fila.acumuladores['total_consultas'],
                rnd_texto,
                int_texto
            )

            # Determinar tag
            if idx == ultima_idx and idx != filas_a_mostrar[0]:
                tag = 'lastrow'
            else:
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'

            self.tree_vector.insert('', 'end', values=valores, tags=(tag,))

    def _actualizar_graficos(self):
        """Actualiza todos los gráficos"""
        self._actualizar_combo_personas()
        self._actualizar_grafico_integracion()
        self._actualizar_graficos_analisis()

    def _actualizar_combo_personas(self):
        """Actualiza el combo de personas que leyeron"""
        if not self.vector_estado:
            return

        # Recolectar todas las personas que leyeron
        personas = set()
        for fila in self.vector_estado:
            if fila.integraciones:
                personas.update(fila.integraciones.keys())

        personas_list = sorted(list(personas), key=lambda x: int(x[1:]))  # Ordenar por número
        self.combo_personas['values'] = personas_list

        if personas_list:
            self.combo_personas.current(0)

    def _actualizar_grafico_integracion(self):
        """Actualiza el gráfico de integración de Euler"""
        # Limpiar frame
        for widget in self.frame_grafico_integracion.winfo_children():
            widget.destroy()

        if not self.vector_estado or not self.combo_personas.get():
            return

        persona_id = self.combo_personas.get()

        # Buscar el integrador de esta persona
        integrador = None
        for fila in self.vector_estado:
            if persona_id in fila.integraciones:
                integrador = fila.integraciones[persona_id]
                break

        if not integrador:
            return

        # Crear figura
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Obtener historial
        historial = integrador.obtener_historial()
        tiempos = [h[0] for h in historial]
        paginas = [h[1] for h in historial]

        # Graficar
        ax.plot(tiempos, paginas, 'b-', linewidth=2, label=f'Páginas leídas ({persona_id})')
        ax.axhline(y=integrador.K / 5 * max(tiempos) if tiempos else 0,
                  color='r', linestyle='--', alpha=0.5, label='Tendencia')
        ax.set_xlabel('Tiempo (min)', fontsize=11)
        ax.set_ylabel('Páginas Leídas', fontsize=11)
        ax.set_title(f'Integración Numérica de Euler - {persona_id}\n'
                    f'dP/dt = K/5, K={integrador.K}, h={integrador.h}',
                    fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Agregar anotación con información
        if tiempos:
            info_text = f'Tiempo total: {max(tiempos):.2f} min\n'
            info_text += f'Páginas finales: {paginas[-1]:.2f}\n'
            info_text += f'Pasos de integración: {len(historial)}'
            ax.text(0.02, 0.98, info_text,
                   transform=ax.transAxes,
                   fontsize=9,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        fig.tight_layout()

        # Mostrar en canvas
        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico_integracion)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _actualizar_graficos_analisis(self):
        """Actualiza los gráficos de análisis"""
        # Limpiar frame
        for widget in self.frame_graficos_analisis.winfo_children():
            widget.destroy()

        if not self.vector_estado or not self.metricas:
            return

        # Crear figura con subplots
        fig = Figure(figsize=(12, 8), dpi=100)

        # Subplot 1: Evolución de personas en el sistema
        ax1 = fig.add_subplot(2, 2, 1)
        relojes = [fila.reloj for fila in self.vector_estado]
        personas_dentro = [fila.biblioteca['personas_dentro'] for fila in self.vector_estado]

        ax1.plot(relojes, personas_dentro, 'b-', linewidth=1.5)
        ax1.axhline(y=self.config.CAPACIDAD_MAXIMA, color='r', linestyle='--',
                   label=f'Capacidad Máx ({self.config.CAPACIDAD_MAXIMA})')
        ax1.set_xlabel('Tiempo (min)')
        ax1.set_ylabel('Personas Dentro')
        ax1.set_title('Evolución de Personas en la Biblioteca')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Subplot 2: Estado de empleados
        ax2 = fig.add_subplot(2, 2, 2)
        empleados_ocupados = []
        for fila in self.vector_estado:
            ocupados = sum(1 for emp in fila.biblioteca['empleados']
                          if emp['estado'] == 'Ocupado')
            empleados_ocupados.append(ocupados)

        ax2.plot(relojes, empleados_ocupados, 'g-', linewidth=1.5)
        ax2.set_xlabel('Tiempo (min)')
        ax2.set_ylabel('Empleados Ocupados')
        ax2.set_title('Utilización de Empleados')
        ax2.set_ylim(-0.1, 2.1)
        ax2.grid(True, alpha=0.3)

        # Subplot 3: Cola y personas leyendo
        ax3 = fig.add_subplot(2, 2, 3)
        en_cola = [len(fila.biblioteca['cola_atencion']) for fila in self.vector_estado]
        leyendo = [len(fila.biblioteca['personas_leyendo']) for fila in self.vector_estado]

        ax3.plot(relojes, en_cola, 'r-', linewidth=1.5, label='En Cola')
        ax3.plot(relojes, leyendo, 'purple', linewidth=1.5, label='Leyendo')
        ax3.set_xlabel('Tiempo (min)')
        ax3.set_ylabel('Cantidad de Personas')
        ax3.set_title('Cola de Atención vs Personas Leyendo')
        ax3.grid(True, alpha=0.3)
        ax3.legend()

        # Subplot 4: Métricas finales (barras)
        ax4 = fig.add_subplot(2, 2, 4)
        categorias = ['Libros\nPedidos', 'Libros\nDevueltos', 'Consultas']
        valores = [
            self.metricas['total_personas_llegadas'] * self.config.PROB_PEDIR_LIBRO,
            self.metricas['total_personas_llegadas'] * self.config.PROB_DEVOLVER_LIBRO,
            self.metricas['total_personas_llegadas'] * self.config.PROB_CONSULTAR
        ]

        barras = ax4.bar(categorias, valores, color=['#0078D4', '#00B294', '#FFB900'])
        ax4.set_ylabel('Cantidad')
        ax4.set_title('Distribución de Tipos de Acción')
        ax4.grid(True, axis='y', alpha=0.3)

        # Agregar valores en las barras
        for barra in barras:
            height = barra.get_height()
            ax4.text(barra.get_x() + barra.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)

        fig.tight_layout()

        # Mostrar en canvas
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficos_analisis)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _buscar_fila(self):
        """Busca y va a una fila específica"""
        try:
            fila_num = int(self.entry_fila.get())
            if 0 <= fila_num < len(self.vector_estado):
                self.config.HORA_INICIO_MOSTRAR = fila_num
                self._actualizar_tabla()
            else:
                messagebox.showwarning("Aviso", f"La fila debe estar entre 0 y {len(self.vector_estado)-1}")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido")

    def _ir_primera_fila(self):
        """Va a la primera fila"""
        self.config.HORA_INICIO_MOSTRAR = 0
        self._actualizar_tabla()

    def _ir_ultima_fila(self):
        """Va a la última fila"""
        if self.vector_estado:
            self.config.HORA_INICIO_MOSTRAR = max(0, len(self.vector_estado) - self.config.FILAS_A_MOSTRAR)
            self._actualizar_tabla()

    def _exportar_excel(self):
        """Exporta los resultados a Excel"""
        if not self.vector_estado:
            messagebox.showwarning("Aviso", "No hay resultados para exportar")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="simulacion_biblioteca.xlsx"
        )

        if filename:
            try:
                exportador = ExportadorExcel(self.vector_estado, self.metricas)
                exportador.exportar(filename)
                messagebox.showinfo("Éxito", f"Archivo exportado correctamente:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def _exportar_integraciones(self):
        """Exporta las integraciones detalladas"""
        if not self.vector_estado:
            messagebox.showwarning("Aviso", "No hay resultados para exportar")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="integraciones_detalladas.xlsx"
        )

        if filename:
            try:
                exportador = ExportadorExcel(self.vector_estado, self.metricas)
                exportador.exportar_historial_integraciones_detallado(filename)
                messagebox.showinfo("Éxito", f"Integraciones exportadas correctamente:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def _mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        messagebox.showinfo(
            "Acerca de",
            "Simulación de Sistema de Biblioteca\n"
            "TP5 - Simulación de Sistemas\n\n"
            "Características:\n"
            "• Simulación por eventos discretos\n"
            "• Integración numérica por método de Euler\n"
            "• Vector de estado completo\n"
            "• Visualización gráfica\n"
            "• Exportación a Excel\n\n"
            "Desarrollado con Python + Tkinter + Matplotlib"
        )


def main():
    """Función principal"""
    root = tk.Tk()
    app = BibliotecaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
