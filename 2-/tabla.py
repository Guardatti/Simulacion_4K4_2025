from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
import numpy as np

class TablaFrecuencias(QWidget):
    def __init__(self, datos, intervalos, parent=None):
        super().__init__(parent)
        self.datos = datos
        self.intervalos = intervalos

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Permitir selección de celdas y múltiples rangos
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        # Generar tabla
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

    # -------------------------
    # Permitir copiar celdas al portapapeles
    # -------------------------
    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        selection = self.table.selectedRanges()
        if not selection:
            return
        s = ""
        for r in range(selection[0].topRow(), selection[0].bottomRow() + 1):
            row_data = []
            for c in range(selection[0].leftColumn(), selection[0].rightColumn() + 1):
                item = self.table.item(r, c)
                row_data.append(item.text() if item else "")
            s += "\t".join(row_data) + "\n"
        QApplication.clipboard().setText(s)
