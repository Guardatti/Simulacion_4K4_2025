import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QSpinBox, QMessageBox
)
from distribuciones import generar_uniforme, generar_exponencial, generar_normal
from histograma import HistogramaWidget
from tabla import TablaFrecuencias

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Variables Aleatorias")
        self.resize(900, 700)

        self.layout_principal = QVBoxLayout(self)

        # -------------------------
        # Formulario de parámetros
        # -------------------------
        form_layout = QHBoxLayout()

        # Distribución
        self.distribucion_combo = QComboBox()
        self.distribucion_combo.addItems(["Uniforme", "Exponencial", "Normal"])
        form_layout.addWidget(QLabel("Distribución:"))
        form_layout.addWidget(self.distribucion_combo)
        self.distribucion_combo.currentIndexChanged.connect(self.actualizar_placeholders)

        # Tamaño de muestra
        self.muestra_input = QLineEdit()
        self.muestra_input.setPlaceholderText("Tamaño de muestra (máx 1,000,000)")
        form_layout.addWidget(self.muestra_input)

        # Parámetro 1
        self.param1_input = QLineEdit()
        form_layout.addWidget(self.param1_input)

        # Parámetro 2
        self.param2_input = QLineEdit()
        form_layout.addWidget(self.param2_input)

        # Intervalos
        self.intervalos_spin = QSpinBox()
        self.intervalos_spin.setRange(5, 25)
        self.intervalos_spin.setSingleStep(5)
        form_layout.addWidget(QLabel("Intervalos:"))
        form_layout.addWidget(self.intervalos_spin)

        self.layout_principal.addLayout(form_layout)

        # Inicializar placeholders según distribución seleccionada
        self.actualizar_placeholders()

        # -------------------------
        # Botón generar
        # -------------------------
        self.btn_generar = QPushButton("Generar")
        self.layout_principal.addWidget(self.btn_generar)
        self.btn_generar.clicked.connect(self.generar)

        # -------------------------
        # Contenedor para resultados
        # -------------------------
        self.resultados_widget = QWidget()
        self.resultados_layout = QVBoxLayout(self.resultados_widget)
        self.layout_principal.addWidget(self.resultados_widget)

    # -------------------------
    # Método para actualizar placeholders
    # -------------------------
    def actualizar_placeholders(self):
        dist = self.distribucion_combo.currentText()
        if dist == "Uniforme":
            self.param1_input.setPlaceholderText("Ingrese el valor de A")
            self.param2_input.setPlaceholderText("Ingrese el valor de B")
            self.param2_input.setEnabled(True)
        elif dist == "Exponencial":
            self.param1_input.setPlaceholderText("Ingrese lambda")
            self.param2_input.setPlaceholderText("(No aplica)")
            self.param2_input.clear()
            self.param2_input.setEnabled(False)
        elif dist == "Normal":
            self.param1_input.setPlaceholderText("Ingrese la media μ")
            self.param2_input.setPlaceholderText("Ingrese la desviación σ")
            self.param2_input.setEnabled(True)

    # -------------------------
    # Método para generar datos
    # -------------------------
    def generar(self):
        try:
            n = int(self.muestra_input.text())
            if n <= 0 or n > 1000000:
                raise ValueError("El tamaño de muestra debe ser mayor a 0 y menor o igual a 1,000,000.")

            dist = self.distribucion_combo.currentText()
            param1_text = self.param1_input.text()
            param2_text = self.param2_input.text()

            if not param1_text:
                raise ValueError("Debe ingresar el parámetro 1.")
            param1 = float(param1_text)

            if dist in ["Uniforme", "Normal"] and not param2_text:
                raise ValueError("Debe ingresar el parámetro 2.")
            param2 = float(param2_text) if param2_text else None

            if dist == "Uniforme":
                a, b = param1, param2
                if b <= a:
                    raise ValueError("En la distribución uniforme, 'b' debe ser mayor que 'a'.")
                datos = generar_uniforme(n, a, b)
            elif dist == "Exponencial":
                lambd = param1
                if lambd <= 0:
                    raise ValueError("En la distribución exponencial, lambda debe ser mayor a 0.")
                datos = generar_exponencial(n, lambd)
            else:
                mu, sigma = param1, param2
                if sigma <= 0:
                    raise ValueError("En la distribución normal, la desviación estándar debe ser mayor a 0.")
                datos = generar_normal(n, mu, sigma)

            intervalos = self.intervalos_spin.value()

            # Limpiar resultados anteriores
            for i in reversed(range(self.resultados_layout.count())):
                widget = self.resultados_layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

            # Agregar histograma y tabla uno debajo del otro
            self.resultados_layout.addWidget(HistogramaWidget(datos, intervalos))
            self.resultados_layout.addWidget(TablaFrecuencias(datos, intervalos))

        except ValueError as ve:
            QMessageBox.warning(self, "Error de validación", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
