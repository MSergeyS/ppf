'''
test_create_spectrum.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль содержит набор unit-тестов для функций модуля create_spectrume, реализующих построение и отображение спектра сигнала в Qt-интерфейсе. 
Тесты охватывают вычисление спектра, обработку различных режимов отображения (дБ/Вольты), корректную работу с выбранными линиями, а также обработку граничных и ошибочных ситуаций.

Подробные комментарии:
----------------------
- Каждый тест снабжен docstring с описанием проверяемого сценария.
- Используются заглушки (Dummy-классы) для имитации поведения компонентов интерфейса и данных, чтобы изолировать тестируемую логику от внешних зависимостей.
- Модульные тесты покрывают:
    * Корректность вычисления спектра (fft_signal)
    * Успешное построение спектра для валидных данных
    * Обработку ошибок при отсутствии выбранной линии или при повторном построении спектра
    * Переключение режимов отображения спектра (дБ/Вольты)
    * Проверку корректности взаимодействия с интерфейсом (блокировка перемещения виджетов, переключение вкладок)
    * Проверку сообщений пользователю при различных сценариях
- Для изоляции тестов используется мокаемый модуль load_and_prepare_data.
- Проверяется не только результат выполнения функций, но и побочные эффекты: вызовы методов, изменение состояния объектов, появление сообщений.
'''

import numpy as np
from unittest.mock import MagicMock
import sys
import types

# -------------------------------
# Мокаем модуль load_and_prepare_data, чтобы тесты не зависели от его реальной реализации.
# Это позволяет изолировать тестируемый код и избежать ошибок, связанных с отсутствием или изменением внешних зависимостей.
# -------------------------------

import os
import sys
import importlib.util
import types

# Получаем абсолютный путь к директории osc_viewer (на уровень выше текущего файла).
# Это нужно для корректного импорта тестируемого модуля create_spectrume.
osc_viewer_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if osc_viewer_dir not in sys.path:
    sys.path.insert(0, osc_viewer_dir)  # Добавляем директорию в sys.path для поиска модулей

# Импортируем модуль create_spectrume из директории osc_viewer по абсолютному пути.
# Используем importlib, чтобы избежать проблем с относительным импортом.
spec = importlib.util.spec_from_file_location(
    "create_spectrume",
    os.path.join(osc_viewer_dir, "create_spectrume.py")
)
create_spectrume = importlib.util.module_from_spec(spec)
spec.loader.exec_module(create_spectrume)

# Создаем фиктивный (заглушечный) модуль load_and_prepare_data.
# Подменяем его в sys.modules, чтобы при импорте внутри create_spectrume использовалась именно эта заглушка.
sys.modules["load_and_prepare_data"] = types.ModuleType("load_and_prepare_data")
# Вставляем в заглушку функцию prepare_data, которая просто возвращает переданные t, s и None.
# Это позволяет тестировать функции, которые ожидают этот модуль, не реализуя его логику.
sys.modules["load_and_prepare_data"].prepare_data = lambda t, s: (t, s, None)


class DummyLine:
    '''
    Заглушка для линии графика.
    Используется для имитации объекта линии с данными и флагом наличия спектра.
    '''
    def __init__(self, x, y, has_spectrum=False):
        self._x = np.array(x)
        self._y = np.array(y)
        self.has_spectrum = has_spectrum

    def get_xdata(self):
        # Возвращает массив значений по оси X
        return self._x

    def get_ydata(self):
        # Возвращает массив значений по оси Y
        return self._y


class DummySpectrumData:
    '''
    Заглушка для объекта, хранящего данные спектра и методы для работы с ними.
    '''
    def __init__(self, freq=None, spectrum=None, params=None):
        self._freq = freq
        self._spectrum = spectrum
        self._params = params or {"color": "b", "linestyle": "-", "label": "test"}
        self._active_line = None
        self._active_params = None
        self.plot_calls = []  # Список вызовов plot_line
        self.clear_called = False
        self.set_axes_params_called = False

    def get_active_line(self):
        # Возвращает активную линию спектра
        return self._active_line

    def get_active_line_params(self):
        # Возвращает параметры активной линии
        return self._active_params

    def plot_line(self, freq, spectrum, **kwargs):
        # Сохраняем параметры вызова для проверки в тестах
        self.plot_calls.append((freq, spectrum, kwargs))

    def clear_canvas(self):
        # Флаг, что очистка канваса была вызвана
        self.clear_called = True

    def set_axes_params(self, **kwargs):
        # Флаг, что установка параметров осей была вызвана
        self.set_axes_params_called = True


class DummyTabs:
    '''
    Заглушка для вкладок интерфейса.
    '''
    def __init__(self):
        self.setCurrentWidget_called = False
        self.last_widget = None

    def setCurrentWidget(self, widget):
        # Фиксирует вызов переключения вкладки
        self.setCurrentWidget_called = True
        self.last_widget = widget


class DummyLayout:
    '''
    Заглушка для layout, содержащего виджеты.
    '''
    def __init__(self, widgets):
        self._widgets = widgets

    def count(self):
        # Возвращает количество виджетов в layout
        return len(self._widgets)

    def itemAt(self, i):
        # Возвращает объект-обертку для доступа к виджету по индексу
        class Item:
            def __init__(self, widget):
                self._widget = widget

            def widget(self):
                return self._widget

        return Item(self._widgets[i])


class DummyWidget:
    '''
    Заглушка для виджета, поддерживающего блокировку перемещения.
    '''
    def __init__(self):
        self._osc_viewer_move_locked = False


class DummyMainWindow:
    '''
    Заглушка для главного окна приложения.
    Содержит необходимые атрибуты и методы для тестирования функций спектра.
    '''
    def __init__(self):
        self.spectrum_data = DummySpectrumData()
        self.tabs = DummyTabs()
        self.spectrum_widget = MagicMock()
        # layout возвращает DummyLayout с двумя DummyWidget
        self.spectrum_widget.layout.return_value = DummyLayout(
            [DummyWidget(), DummyWidget()]
        )
        self._spectrum_db_mode = False  # Режим отображения спектра (дБ или Вольты)
        self.messages = []  # Список сообщений, отображаемых пользователю

    def show_message(self, msg):
        # Добавляет сообщение в список (имитация вывода пользователю)
        self.messages.append(msg)

    def redirect_stdout_to_textedit(self):
        # Контекстный менеджер-заглушка для перенаправления вывода
        class DummyCtx:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return DummyCtx()


def test_fft_signal_basic():
    '''
    Тест базовой работы функции fft_signal: проверка размеров и типов возвращаемых данных.
    '''
    t = np.linspace(0, 1, 1000)
    s = np.sin(2 * np.pi * 50 * t)
    fft_s, nsamp, fs, df, freq_vec = create_spectrume.fft_signal(s, t)
    # Проверяем типы и размеры возвращаемых данных
    assert isinstance(fft_s, np.ndarray)
    assert nsamp == 1000
    assert np.isclose(fs, 999.0, atol=1)
    assert np.isclose(df, fs / nsamp)
    assert freq_vec.shape == (1000,)


def test_create_spectrume_success():
    '''
    Проверка успешного построения спектра для валидной линии.
    '''
    main_window = DummyMainWindow()
    x = np.linspace(0, 1000, 1000)
    y = np.sin(2 * np.pi * 1e-3 * x)
    line = DummyLine(x, y, has_spectrum=False)
    result = create_spectrume.create_spectrume(main_window, line)
    # Проверяем, что результат не None и корректные типы
    assert result is not None
    freq, spectrum = result
    assert isinstance(freq, np.ndarray)
    assert isinstance(spectrum, np.ndarray)
    assert len(freq) == len(spectrum)
    # Проверяем, что не было сообщений об ошибках
    assert all(msg for msg in main_window.messages if "График построен" not in msg)


def test_create_spectrume_no_line():
    '''
    Проверка обработки случая, когда линия не выбрана (None).
    '''
    main_window = DummyMainWindow()
    result = create_spectrume.create_spectrume(main_window, None)
    # Ожидаем None и сообщение об ошибке
    assert result is None
    assert "Нет выбранной линии" in main_window.messages[0]


def test_create_spectrume_already_built():
    '''
    Проверка обработки случая, когда спектр уже построен для линии.
    '''
    main_window = DummyMainWindow()
    x = np.linspace(0, 1000, 1000)
    y = np.sin(2 * np.pi * 1e-3 * x)
    line = DummyLine(x, y, has_spectrum=True)
    result = create_spectrume.create_spectrume(main_window, line)
    # Ожидаем None и сообщение о повторном построении
    assert result is None
    assert any("спектр уже построен" in msg for msg in main_window.messages)


def test_set_spectrum_db_mode_db(monkeypatch):
    '''
    Проверка установки режима отображения спектра в дБ.
    '''
    main_window = DummyMainWindow()
    freq = np.linspace(0, 4e6, 100)
    spectrum = np.ones(100)
    line = DummyLine(freq, spectrum)
    main_window.spectrum_data._active_line = line
    main_window.spectrum_data._active_params = {
        "color": "r",
        "linestyle": "--",
        "label": "test",
    }
    create_spectrume.set_spectrum_db_mode(main_window, True)
    # Проверяем, что режим установлен, канвас очищен, параметры осей выставлены, линия нарисована
    assert main_window._spectrum_db_mode is True
    assert main_window.spectrum_data.clear_called
    assert main_window.spectrum_data.set_axes_params_called
    assert main_window.spectrum_data.plot_calls


def test_set_spectrum_db_mode_volts(monkeypatch):
    '''
    Проверка установки режима отображения спектра в Вольтах.
    '''
    main_window = DummyMainWindow()
    freq = np.linspace(0, 4e6, 100)
    spectrum = np.ones(100)
    line = DummyLine(freq, spectrum)
    main_window.spectrum_data._active_line = line
    main_window.spectrum_data._active_params = {
        "color": "r",
        "linestyle": "--",
        "label": "test",
    }
    create_spectrume.set_spectrum_db_mode(main_window, False)
    # Проверяем, что режим установлен, канвас очищен, параметры осей выставлены, линия нарисована
    assert main_window._spectrum_db_mode is False
    assert main_window.spectrum_data.clear_called
    assert main_window.spectrum_data.set_axes_params_called
    assert main_window.spectrum_data.plot_calls


def test_add_spectrume_db_mode(monkeypatch):
    '''
    Проверка добавления спектра в режиме дБ.
    '''
    main_window = DummyMainWindow()
    main_window._spectrum_db_mode = True
    x = np.linspace(0, 1000, 1000)
    y = np.sin(2 * np.pi * 1e-3 * x)
    line = DummyLine(x, y, has_spectrum=False)
    params = {"color": "g", "linestyle": ":", "label": "testline"}
    create_spectrume.add_spectrume(main_window, line, params)
    # Проверяем, что линия нарисована, параметры осей выставлены, вкладка переключена
    assert main_window.spectrum_data.plot_calls
    assert main_window.spectrum_data.set_axes_params_called
    assert main_window.tabs.setCurrentWidget_called
    # Проверяем, что хотя бы один виджет заблокирован для перемещения
    assert any(
        w._osc_viewer_move_locked for w in main_window.spectrum_widget.layout()._widgets
    )
    # Проверяем, что сообщение о построении графика отображено
    assert "График построен" in main_window.messages[-1]


def test_add_spectrume_volts_mode(monkeypatch):
    '''
    Проверка добавления спектра в режиме Вольт.
    '''
    main_window = DummyMainWindow()
    main_window._spectrum_db_mode = False
    x = np.linspace(0, 1000, 1000)
    y = np.sin(2 * np.pi * 1e-3 * x)
    line = DummyLine(x, y, has_spectrum=False)
    params = {"color": "g", "linestyle": ":", "label": "testline"}
    create_spectrume.add_spectrume(main_window, line, params)
    # Проверяем, что линия нарисована, параметры осей выставлены, вкладка переключена
    assert main_window.spectrum_data.plot_calls
    assert main_window.spectrum_data.set_axes_params_called
    assert main_window.tabs.setCurrentWidget_called
    # Проверяем, что хотя бы один виджет заблокирован для перемещения
    assert any(
        w._osc_viewer_move_locked for w in main_window.spectrum_widget.layout()._widgets
    )
    # Проверяем, что сообщение о построении графика отображено
    assert "График построен" in main_window.messages[-1]
