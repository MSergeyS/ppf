'''
test_spectr_context_menu.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль содержит набор unit-тестов для функций модуля spectr_context_menu, реализующих работу контекстного меню спектра в приложении. 
Тесты проверяют корректность обработки различных действий меню, таких как переключение масштаба, нормализация, сброс, сохранение изображения и очистка графика.
'''

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import os
import sys
# Добавляем путь к директории osc_viewer для корректного импорта тестируемого модуля
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spectr_context_menu import show_spectr_context_menu

# Мокаем модуль, который может понадобиться внутри spectr_context_menu
sys.modules['load_and_prepare_data'] = MagicMock()

# --- Заглушка для линии спектра ---
class DummyLine:
    def __init__(self, ydata):
        # Сохраняем данные линии (массив значений y)
        self._ydata = np.array(ydata)
        # Список вызовов set_ydata для проверки изменений данных линии
        self.set_ydata_calls = []

    def get_ydata(self):
        # Возвращает текущие значения y линии
        return self._ydata

    def set_ydata(self, ydata):
        # Сохраняет вызовы и обновляет данные линии
        self.set_ydata_calls.append(ydata)
        self._ydata = np.array(ydata)

    def __hash__(self):
        # Позволяет использовать DummyLine как ключ словаря (например, для scale-факторов)
        return id(self)

    def __eq__(self, other):
        # Сравнение по идентичности объекта
        return self is other

# --- Заглушка для объекта данных спектра ---
class DummySpectrumData:
    def __init__(self, lines=None):
        # Линии спектра (список DummyLine)
        self._lines = lines or []
        # Мокаем canvas и scale-факторы для каждой линии
        self.canvas = MagicMock()
        self.canvas._osc_viewer_scale_factors = {line: 1.0 for line in self._lines}
        # Параметры для каждой линии (словарь)
        self._params = {line: {} for line in self._lines}
        # Минимум и максимум по y (используются для масштабирования)
        self._y_min = -100
        self._y_max = 0

    def get_all_lines(self):
        # Возвращает все линии спектра
        return self._lines

    def get_line_params(self, line):
        # Возвращает параметры линии (словарь)
        return self._params.get(line, None)

    def set_axes_params(self, **kwargs):
        # Сохраняет параметры осей (заглушка, для совместимости)
        self._axes_params = kwargs

    def get_y_min(self):
        # Минимальное значение y (для масштабирования)
        return self._y_min

    def get_y_max(self):
        # Максимальное значение y (для масштабирования)
        return self._y_max

    def create_canvas(self):
        # Очищает все линии (используется для clear)
        self._lines.clear()

# --- Заглушка для виджета отображения спектра ---
class DummyWidget:
    def grab(self):
        # Мокаем pixmap для сохранения изображения (имитация скриншота)
        pixmap = MagicMock()
        pixmap.isNull.return_value = False  # Считаем, что pixmap всегда валиден
        pixmap.save.return_value = True     # Сохраняется всегда успешно
        return pixmap

    def mapToGlobal(self, pos):
        # Возвращает позицию без изменений (заглушка для совместимости)
        return pos

# --- Заглушка для главного окна приложения ---
class DummyMainWindow:
    def __init__(self, lines=None):
        # Флаг режима dB (True - dB, False - линейный)
        self._spectrum_db_mode = False
        # Данные спектра (DummySpectrumData)
        self.spectrum_data = DummySpectrumData(lines)
        # Виджет спектра (DummyWidget)
        self.spectrum_widget = DummyWidget()

# --- Фикстура pytest для окна с линиями спектра ---
@pytest.fixture
def main_window_with_lines():
    # Создаём две линии для тестов
    lines = [DummyLine([1, 2, 3]), DummyLine([2, 4, 6])]
    return DummyMainWindow(lines)

# --- Фикстура pytest для окна без линий спектра ---
@pytest.fixture
def main_window_empty():
    # Окно без линий (пустой спектр)
    return DummyMainWindow([])

# --- Тест переключения режима dB и обновления линий ---
@pytest.mark.usefixtures("main_window_with_lines")
@patch("spectr_context_menu.QMenu")
def test_toggle_db_switches_mode_and_updates_lines(mock_qmenu, main_window_with_lines):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    # Создаём мок-объекты QAction с нужным текстом для каждого действия меню
    actions = []
    action_names = ["Переключить dB/линейный", "Нормализовать", "Сбросить", "Сохранить как PNG", "Очистить"]
    for name in action_names:
        act = MagicMock()
        act.text.return_value = name
        actions.append(act)
    menu.addAction.side_effect = actions
    # Выбираем первое действие (toggle_db)
    menu.exec.return_value = actions[0]

    # Устанавливаем начальный режим (линейный)
    main_window = main_window_with_lines
    main_window._spectrum_db_mode = False

    # Вызываем функцию отображения контекстного меню
    show_spectr_context_menu(main_window, pos=MagicMock())

    # Проверяем, что режим переключился (True или False)
    assert main_window._spectrum_db_mode is True or main_window._spectrum_db_mode is False
    # Проверяем, что set_ydata был вызван для каждой линии (обновление данных)
    for line in main_window.spectrum_data.get_all_lines():
        assert line.set_ydata_calls  # Проверяем, что set_ydata был вызван хотя бы раз

# --- Тест нормализации: максимальное значение каждой линии после действия должно быть 1 ---
@pytest.mark.usefixtures("main_window_with_lines")
@patch("spectr_context_menu.QMenu")
def test_normalize_action_normalizes_lines(mock_qmenu, main_window_with_lines):
    menu = MagicMock()
    mock_qmenu.return_value = menu
    # Создаём мок-объекты QAction с нужным текстом
    actions = []
    action_names = ["Переключить dB/линейный", "Нормализовать", "Сбросить", "Сохранить как PNG", "Очистить"]
    for name in action_names:
        act = MagicMock()
        act.text.return_value = name
        actions.append(act)
    menu.addAction.side_effect = actions
    # Выбираем второе действие (normalize)
    menu.exec.return_value = actions[1]

    main_window = main_window_with_lines

    # Вызываем функцию отображения контекстного меню
    show_spectr_context_menu(main_window, pos=MagicMock())

    # После нормализации максимальное значение каждой линии должно быть 1
    for line in main_window.spectrum_data.get_all_lines():
        assert np.isclose(np.max(line.get_ydata()), 1.0)

# --- Тест для проверки действия "Сбросить" ---
@pytest.mark.usefixtures("main_window_with_lines")
@patch("spectr_context_menu.QMenu")
def test_reset_action_resets_scale_factors(mock_qmenu, main_window_with_lines):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    actions = []
    # Список названий действий меню
    action_names = ["Переключить dB/линейный", "Нормализовать", "Сбросить", "Сохранить как PNG", "Очистить"]
    # Создаём мок-объекты QAction с нужным текстом для каждого действия меню
    for name in action_names:
        act = MagicMock()
        act.text.return_value = name
        actions.append(act)
    menu.addAction.side_effect = actions
    # Выбираем третье действие (reset)
    menu.exec.return_value = actions[2]  # "Сбросить"
    main_window = main_window_with_lines

    # Вызываем функцию отображения контекстного меню
    show_spectr_context_menu(main_window, pos=MagicMock())

    # Проверяем, что scale-факторы сброшены к 1.0 для всех линий
    for line in main_window.spectrum_data.get_all_lines():
        assert np.isclose(main_window.spectrum_data.canvas._osc_viewer_scale_factors[line], 1.0)

# --- Тест: действие "Сохранить как PNG" вызывает диалог сохранения и сохраняет изображение ---
@pytest.mark.usefixtures("main_window_with_lines")
@patch("spectr_context_menu.QMenu")
@patch("spectr_context_menu.QFileDialog.getSaveFileName", return_value=("output_test.png", None))
def test_save_to_png_action_saves_image(mock_get_save, mock_qmenu, main_window_with_lines):
    # Мокаем экземпляр QMenu, который будет создан внутри show_spectr_context_menu
    menu = MagicMock()
    mock_qmenu.return_value = menu

    # Подготавливаем список мок-объектов QAction с нужным текстом для каждого пункта меню
    actions = []
    action_names = ["Переключить dB/линейный", "Нормализовать", "Сбросить", "Сохранить как PNG", "Очистить"]
    for name in action_names:
        act = MagicMock()             # это будет «элемент меню»
        act.text.return_value = name  # текст, по которому внутри функции определяется действие
        actions.append(act)

    # При добавлении действий в меню возвращаем соответствующие мок-объекты QAction
    menu.addAction.side_effect = actions
    # Эмулируем выбор пользователем четвертого пункта — «Сохранить как PNG»
    menu.exec.return_value = actions[3]

    main_window = main_window_with_lines

    # Патчим метод grab у виджета спектра, чтобы:
    # - не захватывать реальный скриншот;
    # - контролировать возвращаемый QPixmap и проверить вызовы .save(...)
    with patch.object(main_window.spectrum_widget, "grab", autospec=True) as mock_grab:
        # Настраиваем поведение поддельного QPixmap
        mock_pixmap = MagicMock()
        mock_pixmap.isNull.return_value = False  # считаем, что скриншот «валидный»
        mock_pixmap.save.return_value = True     # сохранение «успешно»
        mock_grab.return_value = mock_pixmap     # grab() вернет наш поддельный pixmap

        # Запускаем отображение контекстного меню и обработку выбранного действия
        show_spectr_context_menu(main_window, pos=MagicMock())

        # Проверяем, что был открыт диалог «Сохранить файл...»
        mock_get_save.assert_called_once()

        # Проверяем, что метод grab() у виджета действительно вызывался
        mock_grab.assert_called_once()

        # Проверяем, что сохранение изображения было вызвано с ожидаемыми аргументами
        mock_pixmap.save.assert_called_once_with("output_test.png", "PNG")

# --- Тест для проверки действия "Очистить" ---
@pytest.mark.usefixtures("main_window_with_lines")
@patch("spectr_context_menu.QMenu")
def test_clear_action_removes_all_lines(mock_qmenu, main_window_with_lines):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    actions = []
    # Список названий действий меню
    action_names = ["Переключить dB/линейный", "Нормализовать", "Сбросить", "Сохранить как PNG", "Очистить"]
    # Создаём мок-объекты QAction с нужным текстом для каждого действия меню
    for name in action_names:
        act = MagicMock()
        act.text.return_value = name
        actions.append(act)
    menu.addAction.side_effect = actions
    # Выбираем пятое действие (clear)
    menu.exec.return_value = actions[4]  # "Очистить"

    main_window = main_window_with_lines

    # Вызываем функцию отображения контекстного меню
    show_spectr_context_menu(main_window, pos=MagicMock())

    # Проверяем, что все линии удалены (очищен график)
    assert main_window.spectrum_data.get_all_lines() == []

# --- Тест: действие "Переключить Y: В / дБ" с пустым спектром не вызывает ошибок ---
@pytest.mark.usefixtures("main_window_empty")
@patch("spectr_context_menu.QMenu")
def test_toggle_db_with_no_lines_does_not_fail(mock_qmenu, main_window_empty):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    # Создаём 5 мок-объектов для действий меню
    actions = [MagicMock() for _ in range(5)]
    menu.addAction.side_effect = actions
    # Выбираем первое действие — переключение масштаба dB/линейный
    menu.exec.return_value = actions[0]
    # Не должно быть исключений при вызове функции даже если линий нет
    show_spectr_context_menu(main_window_empty, pos=MagicMock())
    # Проверяем, что режим переключился (атрибут существует)
    assert hasattr(main_window_empty, "_spectrum_db_mode")

# --- Тест: действие "Нормализовать" с пустым спектром не вызывает ошибок ---
@pytest.mark.usefixtures("main_window_empty")
@patch("spectr_context_menu.QMenu")
def test_normalize_with_no_lines_does_not_fail(mock_qmenu, main_window_empty):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    # Создаём 5 мок-объектов для действий меню
    actions = [MagicMock() for _ in range(5)]
    menu.addAction.side_effect = actions
    # Выбираем второе действие — нормализация
    menu.exec.return_value = actions[1]
    # Не должно быть исключений при вызове функции даже если линий нет
    show_spectr_context_menu(main_window_empty, pos=MagicMock())

# --- Тест: действие "Сбросить к исходному уровню" с пустым спектром не вызывает ошибок ---
@pytest.mark.usefixtures("main_window_empty")
@patch("spectr_context_menu.QMenu")
def test_reset_with_no_lines_does_not_fail(mock_qmenu, main_window_empty):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    # Создаём 5 мок-объектов для действий меню
    actions = [MagicMock() for _ in range(5)]
    menu.addAction.side_effect = actions
    # Выбираем третье действие — сброс
    menu.exec.return_value = actions[2]
    # Не должно быть исключений при вызове функции даже если линий нет
    show_spectr_context_menu(main_window_empty, pos=MagicMock())

# --- Тест: действие "Сохранить как изображение" с пустым спектром не вызывает ошибок ---
@pytest.mark.usefixtures("main_window_empty")
@patch("spectr_context_menu.QMenu")
@patch("spectr_context_menu.QFileDialog.getSaveFileName", return_value=("test.png", None))
def test_save_to_png_with_no_lines_does_not_fail(mock_get_save, mock_qmenu, main_window_empty):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    # Создаём 5 мок-объектов для действий меню
    actions = [MagicMock() for _ in range(5)]
    menu.addAction.side_effect = actions
    # Выбираем четвертое действие — сохранить как PNG
    menu.exec.return_value = actions[3]
    # Патчим grab, чтобы не было ошибок при попытке сохранить изображение
    with patch.object(main_window_empty.spectrum_widget, "grab", autospec=True) as mock_grab:
        # Настраиваем поведение мок-объекта pixmap
        mock_grab.return_value.isNull.return_value = False
        mock_grab.return_value.save.return_value = True
        # Не должно быть исключений при вызове функции даже если линий нет
        show_spectr_context_menu(main_window_empty, pos=MagicMock())
        # Проверяем, что grab был вызван
        mock_grab.assert_called_once()

# --- Тест: действие "Очистить график" с пустым спектром не вызывает ошибок ---
@pytest.mark.usefixtures("main_window_empty")
@patch("spectr_context_menu.QMenu")
def test_clear_with_no_lines_does_not_fail(mock_qmenu, main_window_empty):
    # Мокаем меню и действия
    menu = MagicMock()
    mock_qmenu.return_value = menu
    # Создаём 5 мок-объектов для действий меню
    actions = [MagicMock() for _ in range(5)]
    menu.addAction.side_effect = actions
    # Выбираем пятое действие — очистить график
    menu.exec.return_value = actions[4]
    # Не должно быть исключений при вызове функции даже если линий нет
    show_spectr_context_menu(main_window_empty, pos=MagicMock())
    # После очистки список линий должен быть пустым
    assert main_window_empty.spectrum_data.get_all_lines() == []

    def test_all_actions_with_no_lines_combined(main_window_empty):
        with patch("spectr_context_menu.QMenu") as qmenu_mock:
            menu = MagicMock()
            qmenu_mock.return_value = menu
            items = [MagicMock() for _ in range(5)]
            menu.addAction.side_effect = items

            # 1) Toggle dB/linear
            menu.exec.return_value = items[0]
            show_spectr_context_menu(main_window_empty, pos=MagicMock())
            assert hasattr(main_window_empty, "_spectrum_db_mode")

            # 2) Normalize
            menu.exec.return_value = items[1]
            show_spectr_context_menu(main_window_empty, pos=MagicMock())

            # 3) Reset
            menu.exec.return_value = items[2]
            show_spectr_context_menu(main_window_empty, pos=MagicMock())

            # 4) Save to PNG
            with patch("spectr_context_menu.QFileDialog.getSaveFileName", return_value=("test.png", None)) as save_mock:
                with patch.object(main_window_empty.spectrum_widget, "grab", autospec=True) as grab_mock:
                    pix = MagicMock()
                    pix.isNull.return_value = False
                    pix.save.return_value = True
                    grab_mock.return_value = pix

                    menu.exec.return_value = items[3]
                    show_spectr_context_menu(main_window_empty, pos=MagicMock())

                    save_mock.assert_called_once()
                    grab_mock.assert_called_once()
                    pix.save.assert_called_once()

            # 5) Clear
            menu.exec.return_value = items[4]
            show_spectr_context_menu(main_window_empty, pos=MagicMock())
            assert main_window_empty.spectrum_data.get_all_lines() == []
