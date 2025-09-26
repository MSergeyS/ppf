'''
test_py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль содержит набор unit-тестов для функций модуля osc_context_menu, реализующих работу контекстного меню графика в приложении.
Тесты проверяют корректность обработки различных действий меню, таких как сохранение изображения, очистка графика, построение спектра и обрезка данных по оси X.
'''

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Устанавливаем корректный путь для импорта тестируемых модулей
osc_viewer_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if osc_viewer_dir not in sys.path:
    sys.path.insert(0, osc_viewer_dir)

from osc_context_menu import (
    show_plot_context_menu,
    create_spectrum,
    clip_data_x_axis,
    save_to_png,
)

# Фикстура для создания поддельного главного окна приложения
@pytest.fixture
def main_window():
    mw = MagicMock()
    mw.plot_widget = MagicMock()
    mw.plot_data_signal = MagicMock()
    # Возвращаемое значение для метода получения границ оси X
    mw.plot_data_signal.ax.get_xlim.return_value = (0.0, 10.0)
    return mw

# Тест: Проверка обработки действия "Сохранить изображение"
def test_show_plot_context_menu_save_image(main_window):
    with patch("osc_context_menu.QMenu") as MockMenu, patch(
        "osc_context_menu.save_to_png"
    ) as mock_save, patch("osc_context_menu.print_c") as mock_print:
        menu_instance = MockMenu.return_value
        action1 = MagicMock()
        # Эмулируем добавление действий в меню
        menu_instance.addAction.side_effect = [
            action1,
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        # Эмулируем выбор первого действия (сохранение)
        menu_instance.exec.return_value = action1
        show_plot_context_menu(main_window, MagicMock())
        # Проверяем, что функция сохранения была вызвана
        mock_save.assert_called_once_with(main_window)
        # Проверяем, что был выведен правильный текст
        mock_print.assert_called_with("Сохранение изображения графика\n")

# Тест: Проверка обработки действия "Очистить график"
def test_show_plot_context_menu_clear_plot(main_window):
    with patch("osc_context_menu.QMenu") as MockMenu, patch(
        "osc_context_menu.print_c"
    ) as mock_print:
        menu_instance = MockMenu.return_value
        action2 = MagicMock()
        # Эмулируем добавление действий в меню
        menu_instance.addAction.side_effect = [
            MagicMock(),
            action2,
            MagicMock(),
            MagicMock(),
        ]
        # Эмулируем выбор второго действия (очистка)
        menu_instance.exec.return_value = action2
        show_plot_context_menu(main_window, MagicMock())
        # Проверяем, что был вызван метод очистки графика
        main_window.plot_data_signal.create_canvas.assert_called_once()
        # Проверяем, что был выведен правильный текст
        mock_print.assert_called_with("График очищен\n")

# Тест: Проверка обработки действия "Построить спектр"
def test_show_plot_context_menu_create_spectrum(main_window):
    with patch("osc_context_menu.QMenu") as MockMenu, patch(
        "osc_context_menu.create_spectrum"
    ) as mock_spectrum, patch("osc_context_menu.print_c") as mock_print:
        menu_instance = MockMenu.return_value
        action3 = MagicMock()
        # Эмулируем добавление действий в меню
        menu_instance.addAction.side_effect = [
            MagicMock(),
            MagicMock(),
            action3,
            MagicMock(),
        ]
        # Эмулируем выбор третьего действия (спектр)
        menu_instance.exec.return_value = action3
        show_plot_context_menu(main_window, MagicMock())
        # Проверяем, что функция построения спектра была вызвана
        mock_spectrum.assert_called_once_with(main_window)
        # Проверяем, что был выведен правильный текст
        mock_print.assert_called_with("Построить спектр\n")

# Тест: Проверка обработки действия "Обрезать данные по оси X"
def test_show_plot_context_menu_clip_data_x_axis(main_window):
    with patch("osc_context_menu.QMenu") as MockMenu, patch(
        "osc_context_menu.clip_data_x_axis"
    ) as mock_clip, patch("osc_context_menu.print_c") as mock_print:
        menu_instance = MockMenu.return_value
        action4 = MagicMock()
        # Эмулируем добавление действий в меню
        menu_instance.addAction.side_effect = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            action4,
        ]
        # Эмулируем выбор четвертого действия (обрезка)
        menu_instance.exec.return_value = action4
        show_plot_context_menu(main_window, MagicMock())
        # Проверяем, что функция обрезки данных была вызвана
        mock_clip.assert_called_once_with(main_window)
        # Проверяем, что был выведен правильный текст
        mock_print.assert_called_with("Обрезать данные по оси х\n")

# Тест: Проверка построения спектра при отсутствии активной линии (нет параметров)
def test_create_spectrum_no_active_line_params(main_window):
    main_window.plot_data_signal.get_active_line_params.return_value = None
    with patch("osc_context_menu.print_c") as mock_print:
        create_spectrum(main_window)
        # Проверяем, что был выведен текст об отсутствии активной линии
        mock_print.assert_called_with("Нет активной линии для спектра\n")

# Тест: Проверка построения спектра при отсутствии активной линии (нет объекта линии)
def test_create_spectrum_no_active_line(main_window):
    main_window.plot_data_signal.get_active_line_params.return_value = {"dummy": 1}
    main_window.plot_data_signal.get_active_line.return_value = None
    with patch("osc_context_menu.print_c") as mock_print:
        create_spectrum(main_window)
        # Проверяем, что был выведен текст об отсутствии активной линии
        mock_print.assert_called_with("Нет активной линии для спектра")

# Тест: Проверка успешного построения спектра
def test_create_spectrum_success(main_window):
    main_window.plot_data_signal.get_active_line_params.return_value = {"dummy": 1}
    main_window.plot_data_signal.get_active_line.return_value = "line"
    with patch("osc_context_menu.add_spectrume") as mock_add, patch(
        "osc_context_menu.print_c"
    ):
        # Удаляем атрибут _spectrum_db_mode, если он есть
        if hasattr(main_window, "_spectrum_db_mode"):
            delattr(main_window, "_spectrum_db_mode")
        create_spectrum(main_window)
        # Проверяем, что функция добавления спектра была вызвана
        mock_add.assert_called_once_with(main_window, "line", {"dummy": 1})
        # Проверяем, что атрибут _spectrum_db_mode был установлен
        assert hasattr(main_window, "_spectrum_db_mode")

def test_clip_data_x_axis(main_window):
    with patch("osc_context_menu.print_c") as mock_print:
        clip_data_x_axis(main_window)
        # Проверяем, что были вызваны методы получения границ и обрезки
        main_window.plot_data_signal.ax.get_xlim.assert_called_once()
        main_window.plot_data_signal.clip_data_x_axis.assert_called_once_with(0.0, 10.0)
        # Проверяем, что был выведен правильный текст
        mock_print.assert_called_with("Данные обрезаны по X: 0.000 ... 10.000\n")
        mock_print.assert_called_with("Данные обрезаны по X: 0.000 ... 10.000\n")

def test_save_to_png_user_selects_file(main_window):
    pixmap = MagicMock()
    main_window.plot_widget.grab.return_value = pixmap
    with patch(
        "osc_context_menu.QFileDialog.getSaveFileName",
        return_value=("file.png", ""),
    ), patch("osc_context_menu.print_c") as mock_print:
        save_to_png(main_window)
        # Проверяем, что изображение было сохранено
        pixmap.save.assert_called_once_with("file.png", "PNG")
        # Проверяем, что был выведен правильный текст
        mock_print.assert_called_with("Изображение сохранено: file.png\n")
        mock_print.assert_called_with("Изображение сохранено: file.png\n")

def test_save_to_png_user_cancels(main_window):
    pixmap = MagicMock()
    main_window.plot_widget.grab.return_value = pixmap
    with patch(
        "osc_context_menu.QFileDialog.getSaveFileName", return_value=("", "")
    ), patch("osc_context_menu.print_c") as mock_print:
        save_to_png(main_window)
        # Проверяем, что изображение не было сохранено
        pixmap.save.assert_not_called()
        # Проверяем, что был выведен правильный текст (пустое имя файла)
        mock_print.assert_called_with("Изображение сохранено: \n")
        mock_print.assert_called_with("Изображение сохранено: \n")
