from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class HistogramaWidget(QWidget):
    def __init__(self, datos, intervalos, parent=None):
        super().__init__(parent)
        self.datos = datos
        self.intervalos = intervalos

        layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.graficar()

    def graficar(self):
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.hist(self.datos, bins=self.intervalos, edgecolor="black")
        ax.set_title("Histograma de Frecuencias")
        ax.set_xlabel("Intervalos")
        ax.set_ylabel("Frecuencia")
        self.canvas.draw()
