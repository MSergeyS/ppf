from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QTabWidget, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QSize, Qt
import sys

from open_csv_file import open_csv_file
from fft_signal import fft_signal
from load_and_prepare_data import prepare_data
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PlotData import PlotData  # Импортируем ваш класс
from create_spectrume import add_spectrume  # Импортируем функцию создания спектра

class QtOutput:
    def __init__(self, textedit):
        self.textedit = textedit
    def write(self, msg):
        cursor = self.textedit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.textedit.setTextCursor(cursor)
        self.textedit.insertPlainText(str(msg))
    def flush(self):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OscViewer")
        self.setMinimumSize(QSize(800, 500))

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)

        self.plot_widget = QWidget()
        self.plot_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.plot_widget.customContextMenuRequested.connect(self.show_plot_context_menu)

        # Создаем экземпляр PlotData для plot_widget
        self.plot_data_signal = PlotData(self.plot_widget)

        self.spectrum_widget = QWidget()  # Переместили сюда, чтобы использовать ниже
        # Подключаем обработчик события контекстного меню
        self.spectrum_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.spectrum_widget.customContextMenuRequested.connect(self.show_spectr_context_menu)
        self.spectrum_layout = QVBoxLayout(self.spectrum_widget)  # Устанавливаем layout для spectrum_widget

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget, stretch=3)
        # Создаем экземпляр PlotData для spectrum_widget
        self.spectrum_data = PlotData(self.spectrum_widget)
        layout.addWidget(self.status_text, 1)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.plot_widget, "График")
        self.tabs.addTab(self.status_text, "Сообщения")
        self.tabs.addTab(self.spectrum_widget, "Спектр")
        self.setCentralWidget(self.tabs)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        open_action = QAction("Открыть CSV...", self)
        open_action.triggered.connect(lambda: open_csv_file(self))
        file_menu.addAction(open_action)

        # self._old_stdout = sys.stdout
        # sys.stdout = QtOutput(self.status_text)
        self._spectrum_db_mode = False  # Initialize spectrum dB mode flag

    def show_message(self, text):
        self.status_text.append(text)

    # Context manager for temporary stdout redirection
    from contextlib import contextmanager
    @contextmanager
    def redirect_stdout_to_textedit(self):
        old_stdout = sys.stdout
        sys.stdout = QtOutput(self.status_text)
        try:
            yield
        finally:
            sys.stdout = old_stdout

    def closeEvent(self, event):
        # No need to restore sys.stdout since we do not redirect globally
        super().closeEvent(event)

    def show_plot_context_menu(self, pos):
        menu = QMenu(self.plot_widget)
        action1 = menu.addAction("Сохранить как изображение")
        action2 = menu.addAction("Очистить график")
        action3 = menu.addAction("Построить спектр")
        action = menu.exec(self.plot_widget.mapToGlobal(pos))
        if action == action1:
            self.show_message("Сохранение изображения (заглушка)")
            # Можно реализовать сохранение через self.plot_data
            #TODO
        elif action == action2:
            # Очищаем график через PlotData
            self.plot_data_signal.create_canvas()
            self.show_message("График очищен")
        elif action == action3:
            self.show_message("Построить спектр")
            # Получаем активную линию через PlotData
            # line = self.plot_data.get_active_line()
            # create_spectrume(self, line)
            # Получаем параметры активной линии (цвет, стиль, имяб и т.д.)
            params = self.plot_data_signal.get_active_line_params()
            if params is None:
                self.show_message("Нет активной линии для спектра")
                return
            # Получаем саму активную линию
            line = self.plot_data_signal.get_active_line()
            if line is None:
                self.show_message("Нет активной линии для спектра")
                return
            add_spectrume(self, line, params)
            # Признак режима отображения спектра: В (False) или дБ (True)
            if not hasattr(self, '_spectrum_db_mode'):
                self._spectrum_db_mode = False

    # Контекстное меню для вкладки "Спектр" (PyQt6-совместимо)
    def show_spectr_context_menu(self, pos):

        def toggle_db():
            # Проверяем, в каком режиме сейчас ось Y
            if not hasattr(self, '_spectrum_db_mode'):
                self._spectrum_db_mode = False
            self._spectrum_db_mode = not self._spectrum_db_mode

            # Получаем все линии спектра
            lines = self.spectrum_data.get_all_lines()
            if not lines:
                self.show_message("Нет данных спектра для переключения масштаба")
                return
            
            # Получаем параметры имен и масштабов линий из PlotData
            layout = self.spectrum_widget.layout()
            canvas = None
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, FigureCanvas):
                    canvas = widget
                    break
            # line_names = getattr(canvas, "_osc_viewer_line_names", {})
            # scale_factors = getattr(canvas, "_osc_viewer_scale_factors", {})

            self.spectrum_data.clear_canvas()
            for line in lines:
                freq = line.get_xdata()
                spectrum = line.get_ydata()
                params = self.spectrum_data.get_line_params(line)
                name = line_names.get(line, params['label'] if params else "График")
                scale = scale_factors.get(line, 1.0)
                if params is None:
                    continue
                if self._spectrum_db_mode:
                    spectrum_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
                    label = f"{name}"
                    ylabel = 'Амплитуда, дБ'
                    title = "Спектр сигнала (дБ)"
                    ydata = spectrum_db
                    print(f"Переключаем на дБ: {label}")
                else:
                    spectrum_v = np.power(10, spectrum / 20)
                    label = f"{name})"
                    ylabel = 'Амплитуда, В'
                    title = "Спектр сигнала"
                    ydata = spectrum_v
                    print(f"Переключаем на В: {label}")

                self.spectrum_data.plot_line(
                    freq, ydata,
                    add_mode=True,
                    color=params['color'],
                    linestyle=params['linestyle'],
                    label=label,
                    add_scale_label=True  # Не добавляем масштаб к имени линии, он уже в label
                )

            self.spectrum_data.set_axes_params(
                xlim=(0, 4),
                title=title,
                ylabel=ylabel,
                xlabel='Частота, МГц'
            )
                
        menu = QMenu(self.spectrum_widget)
        if (self._spectrum_db_mode):
            text_menu = "Переключить Y: дБ / В"
        else:
            text_menu = "Переключить Y: В / дБ"
        action_toggle_db = QAction(text_menu, self.spectrum_widget)
        menu.addAction(action_toggle_db)

        action_toggle_db.triggered.connect(toggle_db)
        menu.exec(self.spectrum_widget.mapToGlobal(pos))




    
# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
