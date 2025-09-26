# -*- coding: utf-8 -*-
'''
main.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.1

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Главный модуль приложения OscViewer для визуализации сигналов и их спектров. 
Реализует графический интерфейс на PyQt6, управление вкладками, отображение графиков, спектров, сообщений, 
контекстные меню и обработку открытия CSV-файлов с сигналами.

Список классов и функций:
-------------------------
- QtOutput
    Класс для перенаправления вывода print в QTextEdit.
- MainWindow
    Главное окно приложения, реализует интерфейс, вкладки, меню, обработку событий и отображение данных.
- if __name__ == "__main__":
    Точка входа в приложение, запуск основного окна.
'''

# Импортируем необходимые библиотеки
import numpy as np
import sys

# Импортируем виджеты и классы из PyQt6 для создания GUI
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt

# Импортируем FigureCanvas для отображения графиков matplotlib в PyQt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# Импортируем пользовательские модули и функции
from PlotData import PlotData  # Класс для работы с графиками (сигнал/спектр)
from load_and_prepare_data import open_csv_file  # Функция для открытия CSV-файлов
from osc_context_menu import (
    show_plot_context_menu,
)  # Контекстное меню для графика сигнала
from spectr_context_menu import show_spectr_context_menu  # Контекстное меню для спектра


# Класс для перенаправления вывода print в QTextEdit
class QtOutput:
    '''
    Класс QtOutput предназначен для перенаправления текстового вывода в виджет QTextEdit в приложениях на PyQt/PySide.
    Атрибуты:
        textedit (QTextEdit): Ссылка на виджет QTextEdit, в который будет выводиться текст.
    Методы:
        __init__(self, textedit):
            Инициализирует объект QtOutput, сохраняя ссылку на переданный QTextEdit.
        write(self, msg):
            Добавляет сообщение msg в конец текста QTextEdit, перемещая курсор в конец перед вставкой.
        flush(self):
            Метод-заглушка для совместимости с интерфейсом файлового объекта; не выполняет никаких действий.
    '''

    def __init__(self, textedit):
        self.textedit = textedit  # Сохраняем ссылку на QTextEdit

    def write(self, msg):
        # Перемещаем курсор в конец текста
        cursor = self.textedit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.textedit.setTextCursor(cursor)
        # Вставляем новое сообщение: если это HTML, используем insertHtml, иначе insertPlainText
        msg_str = str(msg)
        if msg_str.strip().startswith("<span"):
            self.textedit.insertHtml(msg_str)
        else:
            self.textedit.insertPlainText(msg_str)

    def flush(self):
        # Метод flush нужен для совместимости, но здесь ничего делать не нужно
        pass


class MainWindow(QMainWindow):
    '''
    Класс MainWindow реализует главное окно приложения OscViewer для визуализации сигналов и их спектров.
    Основные возможности:
    - Отображение графика сигнала и его спектра на отдельных вкладках.
    - Вывод сообщений и логов в отдельной вкладке "Сообщения".
    - Контекстные меню для графика и спектра с возможностью:
        - Сохранять изображение графика (заглушка).
        - Очищать график.
        - Строить спектр по выбранной линии.
        - Переключать масштаб оси Y спектра между Вольтами и децибелами.
    - Перенаправление вывода stdout в текстовое поле сообщений.
    - Работа с несколькими линиями графика и спектра, поддержка их параметров (цвет, стиль, подпись).
    - Гибкая настройка интерфейса через QTabWidget и QVBoxLayout.
    - Меню приложения с возможностью открытия CSV-файлов.
    Атрибуты:
        status_text (QTextEdit): Текстовое поле для вывода сообщений.
        plot_widget (QWidget): Виджет для отображения графика сигнала.
        plot_data_signal (PlotData): Объект для работы с данными графика сигнала.
        spectrum_widget (QWidget): Виджет для отображения спектра сигнала.
        spectrum_layout (QVBoxLayout): Layout для размещения элементов спектра.
        spectrum_data (PlotData): Объект для работы с данными спектра.
        tabs (QTabWidget): Вкладки приложения.
        _spectrum_db_mode (bool): Флаг режима отображения спектра (В или дБ).
    Методы:
        show_message(text): Выводит сообщение в текстовое поле.
        redirect_stdout_to_textedit(): Контекстный менеджер для перенаправления stdout в QTextEdit.
        closeEvent(event): Обрабатывает событие закрытия окна.
        show_plot_context_menu(pos): Показывает контекстное меню для графика сигнала.
        show_spectr_context_menu(pos): Показывает контекстное меню для вкладки "Спектр" с возможностью переключения масштаба Y.
    '''

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OscViewer")
        self.setMinimumSize(QSize(800, 500))

        # Текстовое поле для вывода сообщений
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)

        # Виджет для графика сигнала
        # Создаем QWidget, который будет содержать график сигнала
        self.plot_widget = QWidget()
        # Устанавливаем политику контекстного меню для plot_widget (по запросу пользователя)
        self.plot_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # Подключаем обработчик для показа контекстного меню с перенаправлением вывода в QTextEdit
        self.plot_widget.customContextMenuRequested.connect(
            self.show_plot_context_menu_with_redirect
        )

        # Экземпляр PlotData для работы с графиком сигнала
        self.plot_data_signal = PlotData(self.plot_widget)

        # Виджет для спектра
        self.spectrum_widget = QWidget()
        self.spectrum_widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.spectrum_widget.customContextMenuRequested.connect(
            self.show_spectr_context_menu_with_redirect
        )
        self.spectrum_layout = QVBoxLayout(self.spectrum_widget)  # Layout для спектра
        self._spectrum_db_mode = False

        # Основной layout окна
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget, stretch=3)
        # Экземпляр PlotData для работы со спектром
        self.spectrum_data = PlotData(self.spectrum_widget)
        layout.addWidget(self.status_text, 1)

        # Вкладки приложения
        self.tabs = QTabWidget()
        self.tabs.addTab(self.plot_widget, "График")
        self.tabs.addTab(self.status_text, "Сообщения")
        self.tabs.addTab(self.spectrum_widget, "Спектр")
        self.setCentralWidget(self.tabs)
                
        # Меню приложения
        # Создаем меню приложения
        menubar = self.menuBar()  # Получаем объект меню
        file_menu = menubar.addMenu("Файл")  # Добавляем пункт "Файл" в меню

        # Создаем действие "Открыть CSV..."
        open_action = QAction("Открыть CSV...", self)
        # Подключаем обработчик для открытия CSV-файла с выводом сообщений в QTextEdit
        open_action.triggered.connect(self.open_csv_with_redirect)
        # Добавляем действие в меню "Файл"
        file_menu.addAction(open_action)

    def show_message(self, text):
        '''
        Выводит сообщение в текстовое поле "Сообщения" на вкладке приложения.
        Аргументы:
            text (str): Текст сообщения для отображения.
        '''
        self.status_text.append(text)

    # Контекстный менеджер для временного перенаправления stdout в QTextEdit
    from contextlib import contextmanager

    @contextmanager
    def redirect_stdout_to_textedit(self):
        '''
        Контекстный менеджер для перенаправления стандартного вывода (stdout)
        в текстовое поле сообщений QTextEdit. Используется для вывода print-сообщений
        непосредственно в GUI.
        '''
        old_stdout = sys.stdout
        sys.stdout = QtOutput(self.status_text)
        try:
            yield
        finally:
            sys.stdout = old_stdout

    def open_csv_with_redirect(self):
        '''
        Этот метод вызывает диалоговое окно для выбора CSV-файла. 
        Все сообщения, выводимые через функцию print внутри open_csv_file, 
        будут отображаться во вкладке "Сообщения" приложения, а не в стандартном выводе консоли.
        Использует контекстный менеджер для перенаправления stdout в QTextEdit.
        Примечание:
            Функция open_csv_file должна реализовывать логику открытия и обработки выбранного CSV-файла.
        '''
        '''
        Открывает CSV-файл с перенаправлением вывода в QTextEdit.

        Этот метод вызывает диалог открытия CSV-файла, а все сообщения,
        которые выводятся через print внутри open_csv_file, будут отображаться
        во вкладке "Сообщения" приложения, а не в стандартном выводе консоли.
        '''
        # Используем контекстный менеджер для перенаправления stdout в QTextEdit
        with self.redirect_stdout_to_textedit():
            # Открываем CSV-файл (функция open_csv_file реализует логику открытия и обработки)
            open_csv_file(self)

    def show_plot_context_menu_with_redirect(self, pos):
        '''
        Показывает контекстное меню для графика сигнала с перенаправлением вывода в QTextEdit.

        Описание:
            Этот метод отображает контекстное меню для графика сигнала (вкладка "График").
            Все сообщения, выводимые через функцию print внутри обработчиков контекстного меню,
            будут отображаться во вкладке "Сообщения" приложения, а не в стандартном выводе консоли.

        Аргументы:
            pos (QPoint): Координаты точки, в которой должно появиться контекстное меню.

        Пример использования:
            Вызывается автоматически при запросе контекстного меню на графике сигнала.
        '''
        with self.redirect_stdout_to_textedit():
            show_plot_context_menu(self, pos)

    def show_spectr_context_menu_with_redirect(self, pos):
        '''
        Показывает контекстное меню для вкладки "Спектр" с перенаправлением вывода в QTextEdit.

        Описание:
            Этот метод отображает контекстное меню для вкладки "Спектр".
            Все сообщения, выводимые через функцию print внутри обработчиков контекстного меню,
            будут отображаться во вкладке "Сообщения" приложения, а не в стандартном выводе консоли.

        Аргументы:
            pos (QPoint): Координаты точки, в которой должно появиться контекстное меню.
        '''
        with self.redirect_stdout_to_textedit():
            show_spectr_context_menu(self, pos)

    def closeEvent(self, event):
        '''
        Обработчик события закрытия главного окна.
        Вызывает стандартный обработчик родительского класса.
        '''
        super().closeEvent(event)


# =========================
# Точка входа в приложение
# =========================
if __name__ == "__main__":
    # Создаем экземпляр приложения Qt
    app = QApplication(sys.argv)
    # Создаем главное окно приложения
    window = MainWindow()
    # Показываем главное окно
    window.show()
    # Запускаем главный цикл приложения
    app.exec()
