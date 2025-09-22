import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt
from fft_signal import fft_signal
from load_and_prepare_data import prepare_data

def create_spectrume(self, line=None):
    """
    Создает спектр для выбранной линии на основном графике.
    Если линия не указана, используется активная линия.
    """

    if line is None:
        self.show_message("Нет выбранной линии для построения спектра")
        return None

    if not (hasattr(line, 'has_spectrum')) or (line.has_spectrum == False):
        t = line.get_xdata()
        s = line.get_ydata()
        t, s, _ = prepare_data(t/1000, s)  # oversampling_factor не используется
        with self.redirect_stdout_to_textedit():
            print(f"Длина сигнала = {len(s)}")
            print(f"Длительность сигнала = {(t[-1]-t[0])*1000:.2f} мс")
            print(f"Частота дискретизации = {1/(t[1]-t[0])/1e6:.2f} МГц")
        spectrum_y, _, _, _, spectrum_x = fft_signal(np.array(s), np.array(t))  # nsamp, fs, df не используются
        with self.redirect_stdout_to_textedit():
            print(f"Частота дискретизации = {(1/(t[1]-t[0]))/1e6:.2f} МГц")
        min_len = min(len(spectrum_x), len(spectrum_y))  # min_len определяем здесь
        # Найти индекс первого значения spectrum_x >= 0
        idx0 = np.argmax(spectrum_x >= 0)
        spectrum_x = spectrum_x[idx0:min_len]
        spectrum_y = spectrum_y[idx0:min_len]
    else:
        if not hasattr(line, 'has_spectrum'):
            self.show_message("У выбранной линии не установлен флаг has_spectrum — невозможно построить спектр.")
        elif line.has_spectrum:
            self.show_message("Для выбранной линии спектр уже построен.")
        self.show_message("Для выбранной линии спектр уже построен или не установлен флаг has_spectrum")
        return None

    return spectrum_x, spectrum_y

def set_spectrum_db_mode(self, db_mode: bool):
    """Установить режим отображения спектра: True - дБ, False - В"""
    self._spectrum_db_mode = db_mode
    # Обновить отображение спектра, если есть активная линия
    line = self.spectrum_data.get_active_line()
    params = self.spectrum_data.get_active_line_params()
    if line is None or params is None:
        return
    freq = line.get_xdata()
    spectrum = line.get_ydata()
    self.spectrum_data.clear_canvas()
    if self._spectrum_db_mode:
        spectrum_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
        self.spectrum_data.plot_line(freq, spectrum_db,
                     add_mode=True,
                     color=params['color'],
                     linestyle=params['linestyle'],
                     label=params['label'] + " (дБ)")
        self.spectrum_data.set_axes_params(xlim=(0, 4),
                           title="Спектр сигнала (дБ)",
                           ylabel='Амплитуда, дБ',
                           xlabel='Частота, МГц')
    else:
        spectrum_v = np.power(10, spectrum / 20)
        self.spectrum_data.plot_line(freq, spectrum_v,
                     add_mode=True,
                     color=params['color'],
                     linestyle=params['linestyle'],
                     label=params['label'])
        self.spectrum_data.set_axes_params(xlim=(0, 4),
                           title="Спектр сигнала",
                           ylabel='Амплитуда, В',
                           xlabel='Частота, МГц')

def add_spectrume(self, line, params):
    """
    Создает спектр для выбранной линии на основном графике.
    Если линия не указана, используется активная линия.
    Спектр отображается в отдельной вкладке.
    """
    def get_amplitude_and_ylabel(self, spectrum):
        if hasattr(self, '_spectrum_db_mode') and self._spectrum_db_mode:
            spectrum_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
            return spectrum_db, 'Амплитуда, дБ'
        else:
            return abs(spectrum), 'Амплитуда, В'
                
    # Строим спектр по активной линии
    freq, spectrum = create_spectrume(self, line)
    
    if freq is None or spectrum is None:
        return
    # Очищаем и строим спектр с теми же параметрами (цвет, стиль, имя, и т.д.)
    # self.spectrum_data.create_canvas()
    spectrum, ylabel = get_amplitude_and_ylabel(self, spectrum)
    self.spectrum_data.plot_line(freq/1e6, spectrum,
                                 add_mode=True,
                                 color=params['color'],
                                 linestyle=params['linestyle'],
                                 label=params['label'])
    self.spectrum_data.set_axes_params(xlim=(0, 4),
                                       title="Спектр сигнала",
                                       ylabel=ylabel,
                                       xlabel='Частота, МГц')
    # Блокируем изменение положения линий после построения (для спектра)
    layout = self.spectrum_widget.layout()
    if layout is not None:
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            widget._osc_viewer_move_locked = True
    self.tabs.setCurrentWidget(self.spectrum_widget)

    self.show_message("График построен")
    
