# -*- coding: utf-8 -*-
'''
example_PlotData.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-25
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Демонстрационный пример использования класса PlotData для отображения и интерактивного управления графиками на основе matplotlib в Qt-интерфейсе. В примере показано добавление, удаление и повторное построение линий на графике с помощью различных методов PlotData.

Список используемых функций и сценариев:
----------------------------------------
- plot_line(x, y, add_mode=False): Добавление линии на график, с возможностью добавления к уже существующим.
- get_index_active_line(): Получение индекса активной (выделенной) линии.
- remove_line(index): Удаление линии по индексу.
- clear_canvas(): Очистка холста графика.
'''


import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from PlotData import PlotData
import time

# Создаем экземпляр приложения Qt
app = QApplication(sys.argv)

# Создаем главное окно приложения
window = QWidget()
window.setWindowTitle("Пример PlotData")
window.resize(800, 600)

# Создаем вертикальный layout для размещения виджетов
layout = QVBoxLayout(window)

# Генерируем примерные данные для построения графиков
x = np.linspace(0, 10, 100)         # 100 точек от 0 до 10
x1 = np.linspace(0, 100, 1000)      # 1000 точек от 0 до 100

# Создаем экземпляр PlotData, передавая ему окно как родителя
plotter = PlotData(window)

# Добавляем первую линию на график
plotter.plot_line(x, np.sin(x))
# Добавляем вторую линию, не очищая предыдущие (add_mode=True)
plotter.plot_line(x, 2*np.sin(x) + np.cos(x/10), add_mode=True)
# Добавляем третью линию с другим диапазоном x
plotter.plot_line(x1, np.cos(x1), add_mode=True)
# Добавляем четвертую линию
plotter.plot_line(x, np.sin(x + np.pi/4), add_mode=True)

# Устанавливаем layout для окна
window.setLayout(layout)
window.show()

from PyQt6.QtCore import QTimer

def step1():
    """
    Шаг 1: Удаляет активную линию с графика.
    Если активная линия есть, удаляет её и вызывает себя снова через 500 мс.
    Если линий не осталось, переходит к step2.
    """
    index_active_line = plotter.get_index_active_line()
    while index_active_line is not None:
        print(f'Удаляем линию с индексом {index_active_line}')
        # Удаляем линию по индексу
        plotter.remove_line(index_active_line)
        # Повторяем через 500 мс
        QTimer.singleShot(500, step1)
        break

    if index_active_line is None:
        # Если больше нет активных линий, переходим к следующему шагу
        QTimer.singleShot(500, step2)

def step2():
    """
    Шаг 2: (Зарезервировано для очистки холста, если нужно)
    Через 2 секунды переходит к step3.
    """
    # plotter.clear_canvas()  # Раскомментировать для очистки холста
    QTimer.singleShot(2000, step3)

def step3():
    """
    Шаг 3: Повторно строит все линии на графике.
    """
    plotter.plot_line(x, np.sin(x))
    plotter.plot_line(x1, np.cos(x1), add_mode=True)
    plotter.plot_line(x, 2*np.sin(x) + np.cos(x/10), add_mode=True)
    plotter.plot_line(x, np.sin(x + np.pi/4), add_mode=True)
    # QTimer.singleShot(2000, app.quit)  # Раскомментировать для автоматического выхода

# Запускаем step1 через 1 секунду после старта приложения
QTimer.singleShot(1000, step1)

# Запускаем главный цикл приложения
app.exec()
