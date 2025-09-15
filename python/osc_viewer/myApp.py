# Установка PyQt:
# !pip install pyqt6
# и на будущее
# !pip install pyqt-tools

# импортируем классы PyQt для приложения:
# QApplication - это обработчик приложения
# QWidget - базовый пустой виджет графического интерфейса (оба из модуля QtWidgets)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import sys # Только для доступа к аргументам командной строки


# мои функции
from open_csv_file import open_csv_file

import sys# Установка PyQt:
# !pip install pyqt6
# и на будущее
# !pip install pyqt-tools

# импортируем классы PyQt для приложения:
# QApplication - это обработчик приложения
# QWidget - базовый пустой виджет графического интерфейса (оба из модуля QtWidgets)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize

from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import sys # Только для доступа к аргументам командной строки


# мои функции
from open_csv_file import open_csv_file

# # Для корректной работы PyQt в Jupyter
# %gui qt

import sys
from PyQt6.QtWidgets import QTabWidget

class QtOutput:
    def __init__(self, textedit):
        self.textedit = textedit
    def write(self, msg):
        # Добавляем текст в конец QTextEdit
        cursor = self.textedit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.textedit.setTextCursor(cursor)
        self.textedit.insertPlainText(str(msg))
    def flush(self):
        pass

# Подкласс QMainWindow для настройки главного окна приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.format_ver = 1 # версия формата CSV файла
        # self.inx_start = 0 # начальный индекс для отображения
        # self.inx_stop = None # конечный индекс для отображения
        # self.downsampling_factor = 100 # коэффициент даунсемплинга

        self.setWindowTitle("OscViwer")
        self.setMinimumSize(QSize(800, 500))

        # Текстовое поле для сообщений
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)

        # Виджет для графика
        self.plot_widget = QWidget()

        # # Layout: горизонтально — слева график, справа сообщения
        # layout = QHBoxLayout()
        # layout.addWidget(self.plot_widget, 3)
        # layout.addWidget(self.status_text, 1)
        # central_widget = QWidget()
        # central_widget.setLayout(layout)
        # self.setCentralWidget(central_widget)

        # Layout: горизонтально — слева сообщения, справа график
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget, 3)
        layout.addWidget(self.status_text, 1)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        # Добавим вкладки (QTabWidget) на рабочий стол

        self.tabs = QTabWidget()
        self.spectrum_widget = QWidget()  # Добавляем определение spectrum_widget
        self.tabs.addTab(self.plot_widget, "График")
        self.tabs.addTab(self.status_text, "Сообщения")
        self.tabs.addTab(self.spectrum_widget, "Спектр")

        # Установим QTabWidget как центральный виджет
        self.setCentralWidget(self.tabs)
        # Меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        # пункт меню "Открыть" (открыть CSV файл)
        open_action = QAction("Открыть CSV...", self)
        open_action.triggered.connect(lambda: open_csv_file(self))
        file_menu.addAction(open_action)

        self._old_stdout = sys.stdout
        # Перенаправляем stdout на QtOutput
        sys.stdout = self._old_stdout
        sys.stdout = QtOutput(self.status_text)

    def show_message(self, text):
        self.status_text.append(text)

    def closeEvent(self, event):
        # стандартный вывод будет возвращён обратно в терминал
        sys.stdout = self._old_stdout
        super().closeEvent(event)

# Запуск приложения (вне Jupyter)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

class QtOutput:
    def __init__(self, textedit):
        self.textedit = textedit
    def write(self, msg):
        # Добавляем текст в конец QTextEdit
        cursor = self.textedit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.textedit.setTextCursor(cursor)
        self.textedit.insertPlainText(str(msg))
    def flush(self):
        pass

# Подкласс QMainWindow для настройки главного окна приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.format_ver = 1 # версия формата CSV файла
        # self.inx_start = 0 # начальный индекс для отображения
        # self.inx_stop = None # конечный индекс для отображения
        # self.downsampling_factor = 100 # коэффициент даунсемплинга

        self.setWindowTitle("OscViwer")
        self.setMinimumSize(QSize(800, 500))

        # Текстовое поле для сообщений
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)

        # Виджет для графика
        self.plot_widget = QWidget()

        # # Layout: горизонтально — слева график, справа сообщения
        # layout = QHBoxLayout()
        # layout.addWidget(self.plot_widget, 3)
        # layout.addWidget(self.status_text, 1)
        # central_widget = QWidget()
        # central_widget.setLayout(layout)
        # self.setCentralWidget(central_widget)

        # Layout: горизонтально — слева сообщения, справа график
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget, 3)
        layout.addWidget(self.status_text, 1)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        # пункт меню "Открыть" (открыть CSV файл)
        open_action = QAction("Открыть CSV...", self)
        open_action.triggered.connect(lambda: open_csv_file(self))
        file_menu.addAction(open_action)

        self._old_stdout = sys.stdout
        # Перенаправляем stdout на QtOutput
        sys.stdout = self._old_stdout
        sys.stdout = QtOutput(self.status_text)

    def show_message(self, text):
        self.status_text.append(text)

    def closeEvent(self, event):
        # стандартный вывод будет возвращён обратно в терминал
        sys.stdout = self._old_stdout
        super().closeEvent(event)

# Запуск приложения (вне Jupyter)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()