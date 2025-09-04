from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
import numpy as np

class TablaFrecuencias(QWidget):
    def __init__(self, datos, intervalos, parent=None):
        super().__init__(parent)
        self.datos = datos
        self.intervalos = intervalos

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.generar_tabla()

    def generar_tabla(self):
        counts, bins = np.histogram(self.datos, bins=self.intervalos)
        n = len(self.datos)
        k = len(counts)
        freq_esperada = n / k  # frecuencia esperada uniforme

        self.table.setRowCount(k)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "N° Intervalo", "Límite Inferior", "Límite Superior",
            "Frecuencia Observada", "Frecuencia Esperada"
        ])

        for i in range(k):
            self.table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.table.setItem(i, 1, QTableWidgetItem(str(round(bins[i],4))))
            self.table.setItem(i, 2, QTableWidgetItem(str(round(bins[i+1],4))))
            self.table.setItem(i, 3, QTableWidgetItem(str(counts[i])))
            self.table.setItem(i, 4, QTableWidgetItem(str(round(freq_esperada,4))))
