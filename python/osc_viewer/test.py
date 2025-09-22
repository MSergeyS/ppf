import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from PlotData import PlotData
import time

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Пример PlotData")
window.resize(800, 600)

layout = QVBoxLayout(window)

# Пример данных
x = np.linspace(0, 10, 100)
x1 = np.linspace(0, 100, 1000)

plotter = PlotData(window)

plotter.plot_line(x, np.sin(x))
plotter.plot_line(x, 2*np.sin(x) + np.cos(x/10), add_mode=True)
plotter.plot_line(x1, np.cos(x1), add_mode=True)
plotter.plot_line(x, np.sin(x + np.pi/4), add_mode=True)
window.setLayout(layout)
window.show()

from PyQt6.QtCore import QTimer

def step1():
    index_active_line = plotter.get_index_active_line()
    while index_active_line is not None:
        print(f'Удаляем линию с индексом {index_active_line}')
        # plotter.remove_active_line()
        plotter.remove_line(index_active_line)
        QTimer.singleShot(500, step1)
        break

    if index_active_line is None:
        QTimer.singleShot(500, step2)

def step2():
    # plotter.crear_canvas()
    QTimer.singleShot(2000, step3)

def step3():
    plotter.plot_line(x, np.sin(x))
    plotter.plot_line(x1, np.cos(x1), add_mode=True)
    plotter.plot_line(x, 2*np.sin(x) + np.cos(x/10), add_mode=True)
    plotter.plot_line(x, np.sin(x + np.pi/4), add_mode=True)
    # QTimer.singleShot(2000, app.quit)

QTimer.singleShot(1000, step1)

app.exec()


