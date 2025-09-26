# -*- coding: utf-8 -*-
'''
test_PlotData.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-25
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль содержит набор unit-тестов для класса PlotData, реализующего построение и управление графиками matplotlib в Qt-интерфейсе. 
Тесты охватывают добавление, удаление и получение линий, работу с параметрами осей, легендой, очисткой графика, а также обработку граничных и ошибочных ситуаций.

Список тестируемых функций и сценариев:
---------------------------------------
- plot_line(x, y, ...): Добавление линии с различными параметрами (масштабирование по x/y, стиль, цвет, add_mode, x_zoom, автогенерация label).
- get_all_lines(): Получение всех линий на графике, включая случай отсутствия оси.
- get_line_params(line): Получение параметров линии, включая обработку некорректных и "чужих" линий.
- clear_canvas(), clear(): Очистка графика разными способами.
- remove_line(index=None): Удаление линии по индексу, включая несуществующие и отрицательные индексы, а также по умолчанию (последняя линия).
- remove_active_line(): Удаление активной линии, в том числе при отсутствии линий.
- get_active_line(), get_active_line_params(): Получение активной линии и её параметров, включая случай отсутствия активной линии.
- get_index_active_line(): Получение индекса активной линии.
- set_axes_params(...): Установка и частичное обновление параметров осей, заголовков, подписей, сетки, с поддержкой дополнительных параметров для сетки.
- update_legend(add_scale_label=False, ...): Обновление легенды, в том числе при отсутствии линий и с дополнительными параметрами.
- Проверка корректной работы add_mode (добавление и замена линий).
- Проверка обработки граничных и ошибочных ситуаций (нет линий, нет оси, некорректные параметры, удаление всех линий, переключение активной линии).

# Список всех тестов (функций) в этом модуле:
# - test_plot_line_with_zoom_and_style
# - test_remove_line_invalid_index
# - test_remove_line_no_lines
# - test_remove_active_line_no_lines
# - test_get_active_line_params_no_active
# - test_get_line_params_invalid
# - test_set_axes_params_partial
# - test_update_legend_no_lines
# - test_plot_line_add_mode_false_clears
# - test_plot_line_add_mode_true_adds
# - test_get_index_active_line
# - test_get_all_lines_no_ax
# - test_get_line_params_not_in_ax
# - test_plot_line_and_get_lines
# - test_add_multiple_lines
# - test_remove_line_by_index
# - test_remove_active_line
# - test_set_axes_params
# - test_clear_and_clear_canvas
# - test_get_active_line_and_params
# - test_update_legend
# - test_plot_line_default_label
# - test_plot_line_with_x_zoom
# - test_plot_line_multiple_add_mode
# - test_remove_line_last_index
# - test_remove_line_negative_index
# - test_set_axes_params_grid_kwargs
# - test_update_legend_add_scale_label_false
# - test_plot_line_with_custom_color_and_linestyle
# - test_plot_line_and_remove_all_lines
# - test_get_active_line_switching
'''

# Пример запуска тестов:
# В командной строке из папки с тестами выполните:
#   pytest test_PlotData.py
# или для подробного вывода:
#   pytest -v test_PlotData.py

# Импорт стандартных и сторонних библиотек
import sys  # Для доступа к аргументам командной строки
import numpy as np  # Для работы с массивами и математикой
import pytest  # Для написания тестов

# Импорт PyQt6 для создания GUI-виджетов
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

# Импортируем тестируемый класс PlotData
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PlotData import PlotData

def test_plot_line_with_zoom_and_style(plot_widget):
    # Проверяем работу plot_line с масштабированием (y_zoom) и стилями линии
    x = np.linspace(0, 2, 20)
    y = np.exp(x)
    # Рисуем экспоненту с масштабом по y, красным цветом и пунктиром
    plot_widget.plot_line(x, y, label="exp", y_zoom=2.0, color="red", linestyle="--")
    lines = plot_widget.get_all_lines()
    assert len(lines) == 1  # Должна быть одна линия
    params = plot_widget.get_line_params(lines[0])
    # Проверяем, что цвет и стиль линии применились
    assert params["color"] == "red" or params["color"] == "#ff0000"
    assert params["linestyle"] == "--"
    assert "exp" in params["label"]
    # Проверяем, что данные по y действительно были умножены на y_zoom
    plotted_y = lines[0].get_ydata()
    assert np.allclose(plotted_y, np.exp(x) * 2.0)

def test_remove_line_invalid_index(plot_widget):
    # Проверяем, что попытка удалить линию по несуществующему индексу не вызывает ошибок
    plot_widget.clear_canvas()
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="test")
    before = len(plot_widget.get_all_lines())
    plot_widget.remove_line(5)  # Индекс вне диапазона (линия не существует)
    after = len(plot_widget.get_all_lines())
    assert before == after  # Количество линий не должно измениться

def test_remove_line_no_lines(plot_widget):
    # Проверяем, что удаление линии при отсутствии линий не вызывает ошибок
    plot_widget.clear_canvas()
    plot_widget.remove_line(0)  # Нет линий для удаления
    assert len(plot_widget.get_all_lines()) == 0

def test_remove_active_line_no_lines(plot_widget):
    # Проверяем, что remove_active_line не вызывает ошибок, если линий нет
    plot_widget.clear_canvas()
    plot_widget.remove_active_line()
    assert len(plot_widget.get_all_lines()) == 0

def test_get_active_line_params_no_active(plot_widget):
    # Проверяем, что get_active_line_params возвращает None, если активной линии нет
    plot_widget.clear_canvas()
    assert plot_widget.get_active_line_params() is None

def test_get_line_params_invalid(plot_widget):
    # Проверяем, что get_line_params возвращает None для некорректной (None) линии
    plot_widget.clear_canvas()
    assert plot_widget.get_line_params(None) is None

def test_set_axes_params_partial(plot_widget):
    # Проверяем, что можно установить только часть параметров осей (например, только xlim)
    plot_widget.clear_canvas()
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="test")
    plot_widget.set_axes_params(xlim=(0, 2))  # Устанавливаем только лимиты по X
    assert plot_widget.ax.get_xlim() == (0, 2)
    # Остальные параметры (например, title) должны остаться по умолчанию
    assert plot_widget.ax.get_title() != "Test"

def test_update_legend_no_lines(plot_widget):
    # Проверяем, что update_legend не вызывает ошибок, если линий нет
    plot_widget.clear_canvas()
    plot_widget.update_legend()
    assert plot_widget.ax.get_legend() is None  # Легенда не должна появиться

def test_plot_line_add_mode_false_clears(plot_widget):
    # Проверяем, что add_mode=False очищает график перед добавлением новой линии
    plot_widget.clear_canvas()
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="first")
    plot_widget.plot_line(x, -x, label="second", add_mode=False)  # Должен очистить график
    lines = plot_widget.get_all_lines()
    assert len(lines) == 1  # Должна остаться только одна линия
    assert "second" in lines[0].get_label()

def test_plot_line_add_mode_true_adds(plot_widget):
    # Проверяем, что add_mode=True добавляет линию, не очищая график
    plot_widget.clear_canvas()
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="first")
    plot_widget.plot_line(x, -x, label="second", add_mode=True)  # Добавляет вторую линию
    lines = plot_widget.get_all_lines()
    assert len(lines) == 2  # Две линии на графике
    labels = [l.get_label() for l in lines]
    assert any("first" in lbl for lbl in labels)
    assert any("second" in lbl for lbl in labels)

def test_get_index_active_line(plot_widget):
    # Проверяем получение индекса активной линии (должен быть 0 после первой линии)
    plot_widget.clear_canvas()
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="test")
    idx = plot_widget.get_index_active_line()
    assert idx == 0

def test_get_all_lines_no_ax(plot_widget):
    # Проверяем, что get_all_lines возвращает пустой список, если нет ax
    # Симулируем отсутствие атрибута ax у plot_widget
    orig_ax = plot_widget.ax
    delattr(plot_widget, "ax")
    assert plot_widget.get_all_lines() == []
    plot_widget.ax = orig_ax  # Восстанавливаем ax для других тестов

def test_get_line_params_not_in_ax(plot_widget):
    # Проверяем, что get_line_params возвращает None, если линия не принадлежит текущей оси
    plot_widget.clear_canvas()
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="test")
    import matplotlib.lines as mlines
    fake_line = mlines.Line2D([], [])  # Линия, не добавленная на ax
    assert plot_widget.get_line_params(fake_line) is None

# Фикстура для создания экземпляра QApplication (один на модуль)
# PyQt требует, чтобы QApplication был создан только один раз за приложение.
@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()  # Проверяем, существует ли уже экземпляр
    if app is None:
        app = QApplication(sys.argv)  # Если нет — создаём новый
    yield app  # Возвращаем экземпляр для использования в тестах

# Фикстура для создания виджета PlotData для каждого теста
@pytest.fixture
def plot_widget(qapp):
    window = QWidget()  # Создаём главное окно для теста
    layout = QVBoxLayout(window)  # Добавляем вертикальный layout
    plotter = PlotData(window)  # Создаём экземпляр PlotData (наш тестируемый виджет)
    window.setLayout(layout)  # Устанавливаем layout окну
    window.show()  # Показываем окно (необходимо для корректной работы некоторых функций)
    yield plotter  # Возвращаем PlotData для теста
    window.close()  # После теста закрываем окно

def test_plot_line_and_get_lines(plot_widget):
    # Тестируем добавление линии и получение всех линий
    x = np.linspace(0, 5, 50)
    y = np.sin(x)
    plot_widget.plot_line(x, y, label="sin")  # Рисуем синус
    lines = plot_widget.get_all_lines()  # Получаем все линии на графике
    assert len(lines) == 1  # Должна быть одна линия
    params = plot_widget.get_line_params(lines[0])  # Получаем параметры линии
    # Проверяем наличие ключевых параметров
    assert "color" in params and "linestyle" in params and "label" in params
    assert "sin" in params["label"]  # Проверяем, что label содержит "sin"

def test_add_multiple_lines(plot_widget):
    # Тестируем добавление нескольких линий
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 5, 50)
    plot_widget.plot_line(x, np.sin(x), label="sin")  # Первая линия
    plot_widget.plot_line(x, np.cos(x), label="cos", add_mode=True)  # Вторая линия (add_mode=True)
    lines = plot_widget.get_all_lines()
    assert len(lines) == 2  # Должно быть две линии
    labels = [l.get_label() for l in lines]
    assert any("sin" in lbl for lbl in labels)  # Одна из линий — sin
    assert any("cos" in lbl for lbl in labels)  # Другая — cos

def test_remove_line_by_index(plot_widget):
    # Тестируем удаление линии по индексу
    plot_widget.clear_canvas()
    x = np.linspace(0, 5, 50)
    plot_widget.plot_line(x, np.sin(x), label="sin")
    plot_widget.plot_line(x, np.cos(x), label="cos", add_mode=True)
    assert len(plot_widget.get_all_lines()) == 2
    plot_widget.remove_line(0)  # Удаляем первую линию
    lines = plot_widget.get_all_lines()
    assert len(lines) == 1  # Осталась одна линия
    assert "cos" in lines[0].get_label()  # Это должна быть cos

def test_remove_active_line(plot_widget):
    # Тестируем удаление активной линии
    plot_widget.clear_canvas()
    x = np.linspace(0, 5, 50)
    plot_widget.plot_line(x, np.sin(x), label="sin")
    plot_widget.plot_line(x, np.cos(x), label="cos", add_mode=True)
    assert len(plot_widget.get_all_lines()) == 2
    plot_widget.remove_active_line()  # Удаляем активную линию
    assert len(plot_widget.get_all_lines()) == 1  # Должна остаться одна линия

def test_set_axes_params(plot_widget):
    # Тестируем установку параметров осей
    plot_widget.clear_canvas()
    x = np.linspace(0, 5, 50)
    plot_widget.plot_line(x, np.sin(x), label="sin")
    # Устанавливаем параметры осей и заголовки
    plot_widget.set_axes_params(xlim=(0, 10), ylim=(-2, 2), title="Test", xlabel="X", ylabel="Y", grid=False)
    ax = plot_widget.ax
    assert ax.get_xlim() == (0, 10)  # Проверяем лимиты по X
    assert ax.get_ylim() == (-2, 2)  # Проверяем лимиты по Y
    assert ax.get_title() == "Test"  # Проверяем заголовок
    assert ax.get_xlabel() == "X"  # Проверяем подпись оси X
    assert ax.get_ylabel() == "Y"  # Проверяем подпись оси Y

def test_clear_and_clear_canvas(plot_widget):
    # Тестируем очистку графика разными способами
    x = np.linspace(0, 5, 50)
    plot_widget.plot_line(x, np.sin(x), label="sin")
    assert len(plot_widget.get_all_lines()) == 1
    plot_widget.clear()  # Очищаем график (метод clear)
    assert len(plot_widget.get_all_lines()) == 0
    plot_widget.plot_line(x, np.cos(x), label="cos")
    assert len(plot_widget.get_all_lines()) == 1
    plot_widget.clear_canvas()  # Очищаем график (метод clear_canvas)
    assert len(plot_widget.get_all_lines()) == 0

def test_get_active_line_and_params(plot_widget):
    # Тестируем получение активной линии и её параметров
    plot_widget.clear_canvas()
    x = np.linspace(0, 5, 50)
    plot_widget.plot_line(x, np.sin(x), label="sin")
    line = plot_widget.get_active_line()  # Получаем активную линию
    params = plot_widget.get_active_line_params()  # Получаем параметры активной линии
    assert line is not None
    assert params is not None
    assert "sin" in params["label"]  # Проверяем, что label содержит "sin"

def test_update_legend(plot_widget):
    # Тестируем обновление легенды
    plot_widget.clear_canvas()
    x = np.linspace(0, 5, 50)
    plot_widget.plot_line(x, np.sin(x), label="sin")
    plot_widget.update_legend(add_scale_label=True)  # Обновляем легенду с дополнительной подписью
    legend = plot_widget.ax.get_legend()
    assert legend is not None  # Легенда должна быть создана
    labels = [t.get_text() for t in legend.get_texts()]  # Получаем все подписи в легенде
    # Здесь можно добавить дополнительные проверки для labels

def test_plot_line_default_label(plot_widget):
    # Проверяем, что если label не задан, используется автогенерируемое имя
    plot_widget.clear_canvas()  # Очищаем график перед тестом
    x = [0, 1, 2]
    y = [1, 2, 3]
    plot_widget.plot_line(x, y)  # Добавляем линию без label
    lines = plot_widget.get_all_lines()  # Получаем все линии
    assert len(lines) == 1  # Должна быть одна линия
    label = lines[0].get_label()  # Получаем label линии
    # Проверяем, что label содержит автогенерируемое имя ("График" или "Graph")
    assert "График" in label or "Graph" in label

def test_plot_line_with_x_zoom(plot_widget):
    # Проверяем масштабирование по оси X (x_zoom)
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    y = np.ones_like(x)
    plot_widget.plot_line(x, y, x_zoom=2.0, label="zoomx")  # Масштабируем по X
    lines = plot_widget.get_all_lines()
    # Проверяем, что данные по X действительно были умножены на x_zoom
    assert np.allclose(lines[0].get_xdata(), x * 2.0)

def test_plot_line_multiple_add_mode(plot_widget):
    # Проверяем, что несколько линий добавляются с add_mode=True
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="a", add_mode=True)      # Первая линия
    plot_widget.plot_line(x, -x, label="b", add_mode=True)     # Вторая линия
    plot_widget.plot_line(x, x**2, label="c", add_mode=True)   # Третья линия
    lines = plot_widget.get_all_lines()
    assert len(lines) == 3  # Должно быть три линии
    labels = [l.get_label() for l in lines]
    # Проверяем, что все заданные label присутствуют среди линий
    assert all(any(lbl in l for l in labels) for lbl in ["a", "b", "c"])

def test_remove_line_last_index(plot_widget):
    # Проверяем удаление последней линии по умолчанию (index=None)
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="first")  # Первая линия
    plot_widget.plot_line(x, -x, label="second", add_mode=True)  # Вторая линия
    before = len(plot_widget.get_all_lines())
    plot_widget.remove_line()  # Должна удалить последнюю (second)
    lines = plot_widget.get_all_lines()
    assert len(lines) == before - 1  # Количество линий уменьшилось на 1
    # Проверяем, что осталась только первая линия
    assert "first" in lines[0].get_label()

def test_remove_line_negative_index(plot_widget):
    # Проверяем, что отрицательный индекс не приводит к удалению линии
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="test")
    before = len(plot_widget.get_all_lines())
    plot_widget.remove_line(-1)  # Пытаемся удалить по отрицательному индексу
    after = len(plot_widget.get_all_lines())
    # Количество линий не должно измениться
    assert before == after

def test_set_axes_params_grid_kwargs(plot_widget):
    # Проверяем передачу дополнительных параметров для сетки через grid_kwargs
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="test")
    # Включаем сетку с дополнительными параметрами (стиль и цвет)
    plot_widget.set_axes_params(grid=True, grid_kwargs={"linestyle": ":", "color": "gray"})
    # Проверяем, что сетка включена (визуально стиль не проверяем, но ошибок быть не должно)
    # Используем публичный API для проверки наличия сетки
    x_gridlines = plot_widget.ax.get_xgridlines()
    y_gridlines = plot_widget.ax.get_ygridlines()
    assert any(line.get_visible() for line in x_gridlines + y_gridlines)

def test_update_legend_add_scale_label_false(plot_widget):
    # Проверяем, что update_legend работает с add_scale_label=False
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="test")
    plot_widget.update_legend(add_scale_label=False)  # Обновляем легенду без дополнительной подписи
    legend = plot_widget.ax.get_legend()
    assert legend is not None  # Легенда должна быть создана
    labels = [t.get_text() for t in legend.get_texts()]
    # Проверяем, что label "test" присутствует в легенде
    assert any("test" in lbl for lbl in labels)

def test_plot_line_with_custom_color_and_linestyle(plot_widget):
    # Проверяем, что цвет и стиль линии применяются корректно
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    y = np.sin(x)
    plot_widget.plot_line(x, y, color="#00ff00", linestyle=":", label="green")  # Зеленая пунктирная линия
    params = plot_widget.get_line_params(plot_widget.get_all_lines()[0])
    # Проверяем, что цвет и стиль совпадают с заданными
    assert params["color"] == "#00ff00"
    assert params["linestyle"] == ":"

def test_plot_line_and_remove_all_lines(plot_widget):
    # Проверяем последовательное удаление всех линий с помощью remove_active_line
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    # Добавляем три линии
    for i in range(3):
        plot_widget.plot_line(x, x + i, label=f"line{i}", add_mode=True)
    # Удаляем все линии по одной
    while plot_widget.get_all_lines():
        plot_widget.remove_active_line()
    # После удаления всех линий график должен быть пуст
    assert len(plot_widget.get_all_lines()) == 0

def test_get_active_line_switching(plot_widget):
    # Проверяем, что активная линия обновляется при добавлении новых линий
    plot_widget.clear_canvas()  # Очищаем график
    x = np.linspace(0, 1, 10)
    plot_widget.plot_line(x, x, label="first")  # Добавляем первую линию
    first = plot_widget.get_active_line()  # Получаем активную линию (должна быть первая)
    plot_widget.plot_line(x, -x, label="second", add_mode=True)  # Добавляем вторую линию
    second = plot_widget.get_active_line()  # Теперь активной должна быть вторая линия
    # Проверяем, что обе линии существуют и активная линия изменилась
    assert first is not None and second is not None and first != second