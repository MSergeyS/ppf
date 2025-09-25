# -*- coding: utf-8 -*-
'''
PlotData.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-25
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль реализует класс PlotData для отображения и интерактивного управления графиками на основе matplotlib в Qt-интерфейсе.
Класс предназначен для визуализации осциллограмм, спектров и других данных с возможностью масштабирования, управления линиями, настройки отображения и интеграции с PyQt6.

Список параметров и методов:
----------------------------
Параметры конструктора:
- parent_widget (QWidget): Родительский виджет, в котором размещается график.

Основные методы:
- plot(x, y, label=None, **kwargs): Построение линии на графике.
- plot_line(x, y, *, x_zoom=1, y_zoom=1, color=None, linestyle=None, label=None, add_scale_label=True, add_mode=False): Расширенное построение линии с поддержкой масштабирования и интерактивного управления.
- clear(): Очистка графика.
- clear_canvas(): Очистка текущей оси и обновление холста.
- remove_line(inx_line_to_remove=None): Удаление линии по индексу.
- remove_active_line(): Удаление активной линии.
- get_active_line(): Получение активной линии.
- get_index_active_line(): Получение индекса активной линии.
- get_active_line_params(): Получение параметров активной линии.
- get_all_lines(): Получение списка всех линий на графике.
- get_line_params(line): Получение параметров указанной линии.
- set_title(title): Установка заголовка графика.
- set_xlabel(label): Установка подписи оси X.
- set_ylabel(label): Установка подписи оси Y.
- set_xlim(left, right): Установка пределов оси X.
- set_grid(flag=True): Включение/отключение сетки.
- set_axes_params(...): Комплексная настройка параметров отображения графика.
- update_legend(add_scale_label=True): Обновление легенды с учётом имён и масштабных коэффициентов линий.
- create_canvas(): Инициализация холста и панели инструментов внутри родительского виджета.
'''

# Импортируем numpy для работы с массивами и числовыми операциями
import numpy as np

# Импортируем необходимые виджеты и классы из PyQt6 для построения интерфейса
from PyQt6.QtWidgets import (
    QMessageBox,   # Диалоговое окно для вывода сообщений и подтверждений
    QWidget,       # Базовый класс для всех виджетов
    QVBoxLayout,   # Вертикальный layout для размещения дочерних виджетов
    QApplication   # Класс приложения Qt, необходим для работы событий и модификаторов клавиш
)
from PyQt6.QtCore import Qt  # Для работы с модификаторами клавиш (например, Shift)

# Импортируем Figure и инструменты для интеграции matplotlib-графиков в Qt-интерфейс
from matplotlib.figure import Figure
import sys
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas  # Холст для отображения Figure в Qt
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar  # Панель инструментов для управления графиком


class PlotData(QWidget):
    '''
    Класс PlotData
    Класс PlotData реализует виджет для отображения и интерактивного управления графиками на основе matplotlib в Qt-интерфейсе. Предназначен для визуализации осциллограмм, спектров и других временных или спектральных данных с возможностью масштабирования, управления линиями и настройки отображения.
    Основные возможности:
    - Инициализация и размещение matplotlib Figure, FigureCanvas и панели инструментов NavigationToolbar внутри родительского Qt-виджета.
    - Построение графиков с возможностью масштабирования данных по осям X и Y.
    - Добавление, удаление и выделение активной линии на графике.
    - Управление линиями с помощью клавиатуры (переключение, удаление, сдвиг по осям).
    - Автоматическое масштабирование оси X по двойному клику мыши.
    - Хранение и отображение имён и масштабных коэффициентов для каждой линии.
    - Гибкая настройка параметров осей, сетки, подписей и легенды.
    - Методы для получения и изменения параметров линий, а также для очистки и обновления графика.
    Аргументы конструктора:
        parent_widget (QWidget): Родительский виджет, в котором размещается график.
    Основные методы:
        - plot(x, y, label=None, **kwargs): Построение линии на графике.
        - plot_line(...): Расширенное построение линии с поддержкой масштабирования и интерактивного управления.
        - clear(), clear_canvas(): Очистка графика.
        - remove_line(...), remove_active_line(): Удаление линии по индексу или активной линии.
        - get_active_line(), get_index_active_line(), get_active_line_params(): Получение информации об активной линии.
        - get_all_lines(), get_line_params(line): Получение списка всех линий и их параметров.
        - set_title(), set_xlabel(), set_ylabel(), set_xlim(), set_grid(): Настройка параметров осей.
        - set_axes_params(...): Комплексная настройка параметров отображения графика.
        - update_legend(...): Обновление легенды с учётом имён и масштабных коэффициентов линий.
        - create_canvas(): Инициализация холста и панели инструментов внутри родительского виджета.
    Особенности:
    - Для каждой линии сохраняются имя и коэффициент масштабирования, которые отображаются в легенде.
    - Поддерживается интерактивное управление графиком с помощью клавиатуры и мыши.
    - Класс интегрируется с Qt через FigureCanvas и NavigationToolbar, обеспечивая нативное поведение в приложениях PyQt/PySide.
    Пример использования:
        plot_widget = PlotData(parent_widget)
        plot_widget.plot_line(x, y, label="Сигнал", y_zoom=2.0)
        plot_widget.set_axes_params(title="Осциллограмма", xlabel="Время, мс", ylabel="U, В")
    '''
    def __init__(main_window, parent_widget):
        '''
        Инициализация экземпляра PlotData.

        Аргументы:
            parent_widget (QWidget): Родительский виджет, в котором будет размещён график.

        Описание:
            Конструктор вызывает инициализацию базового класса QWidget, сохраняет ссылку на родительский виджет,
            инициализирует объекты Figure, FigureCanvas и ось для построения графиков с помощью matplotlib.
            Организует вертикальный layout для размещения графика и панели инструментов внутри виджета.
            Добавляет панель инструментов NavigationToolbar для управления графиком.
        '''

        # Вызов конструктора родительского класса, чтобы корректно инициализировать базовый класс (например, QWidget).
        # Это важно для правильной работы наследования в PyQt/PySide.
        super().__init__(parent_widget)
        # Сохраняет ссылку на родительский виджет для дальнейшего использования.
        main_window.parent_widget = parent_widget

        # Инициализация Figure, Canvas и Toolbar для отображения графика внутри виджета.
        # Этот метод создаёт matplotlib Figure, FigureCanvas и панель инструментов,
        # а также размещает их в layout родительского виджета.
        main_window.create_canvas()

    def clear(main_window):
        main_window.ax.clear()
        main_window.canvas.draw()

    def plot(main_window, x, y, label=None, **kwargs):
        main_window.ax.plot(x, y, label=label, **kwargs)
        if label:
            main_window.ax.legend()
        main_window.canvas.draw()

    def set_title(main_window, title):
        main_window.ax.set_title(title)
        main_window.canvas.draw()

    def set_xlabel(main_window, label):
        main_window.ax.set_xlabel(label)
        main_window.canvas.draw()

    def set_ylabel(main_window, label):
        main_window.ax.set_ylabel(label)
        main_window.canvas.draw()

    def set_xlim(main_window, left, right):
        main_window.ax.set_xlim(left, right)
        main_window.canvas.draw()

    def set_grid(main_window, flag=True):
        main_window.ax.grid(flag)
        main_window.canvas.draw()

    def get_lines(main_window):
        return main_window.ax.lines

    def remove_line(main_window, inx_line_to_remove=None):
        '''
        Удаляет линию с графика, отображаемого на FigureCanvas родительского виджета.
        Параметры:
            inx_line_to_remove (int, необязательный): Индекс линии для удаления с графика.
            Если None, удаляется последняя (верхняя) линия. По умолчанию None.
        Описание поведения:
            - Находит FigureCanvas в layout родительского виджета.
            - Удаляет указанную линию из Axes графика.
            - Если удаляемая линия была активной, обновляет активную линию и её индекс.
            - Удаляет связанные метаданные (имя линии и scale-фактор), если они присутствуют.
            - Обновляет легенду графика в соответствии с текущими линиями.
            - Перерисовывает canvas для отображения изменений.
        Примечания:
            - Если layout, canvas или линии не найдены, функция завершает выполнение без действий.
            - Если указанный индекс выходит за пределы допустимых значений, функция завершает выполнение без действий.
        '''
        # Используем атрибуты, инициализированные в __init__
        ax = main_window.ax
        canvas = main_window.canvas

        if not ax.lines:
            return
        # Получаем индекс активной линии, если не задан явно
        if inx_line_to_remove is None:
            inx_line_to_remove = main_window.get_index_active_line()
        # Если индекс всё ещё None, удаляем последнюю (верхнюю) линию
        if inx_line_to_remove is None:
            inx_line_to_remove = len(ax.lines) - 1
        # Проверяем корректность индекса
        if inx_line_to_remove < 0 or inx_line_to_remove >= len(ax.lines):
            return
        # Получаем ссылку на удаляемую линию
        line_to_remove = ax.lines[inx_line_to_remove]
        # Удаляем линию с графика
        line_to_remove.remove()
        # Если удаляемая линия была активной — обновляем активную линию и индекс
        if (
            hasattr(canvas, "_osc_viewer_active_line")
            and canvas._osc_viewer_active_line is line_to_remove
        ):
            if ax.lines:
                canvas._osc_viewer_active_line = ax.lines[-1]
                canvas._osc_viewer_active_index = len(ax.lines) - 1
            else:
                canvas._osc_viewer_active_line = None
                canvas._osc_viewer_active_index = None
        # Удаляем метаданные линии (имя, scale-фактор) если они есть
        if hasattr(canvas, "_osc_viewer_line_names"):
            canvas._osc_viewer_line_names.pop(line_to_remove, None)
        # Удаляем scale-фактор линии, если он есть
        if hasattr(canvas, "_osc_viewer_scale_factors"):
            canvas._osc_viewer_scale_factors.pop(line_to_remove, None)

        # Обновляем легенду после удаления линии
        main_window.update_legend()
        
        # Перерисовываем canvas для отображения изменений
        canvas.draw_idle()

    def update_legend(main_window, add_scale_label=True):
        '''
        Обновляет легенду на графике, отображая имена и масштабные коэффициенты линий.
        Если у холста (`canvas`) присутствуют атрибуты `_osc_viewer_line_names` и `_osc_viewer_scale_factors`,
        обновляет подписи всех линий на графике с учётом их имён и масштабных коэффициентов.
        При необходимости добавляет к подписи масштабный коэффициент.
        Если на графике есть линии, отображает легенду в оптимальном месте.
        Если линий нет — удаляет легенду.
        После обновления перерисовывает холст для отображения изменений.
        Параметры:
            add_scale_label (bool): Добавлять ли к подписи линии масштабный коэффициент (по умолчанию True).
        '''
        # Получаем объекты оси и холста, если они существуют
        ax = main_window.ax if hasattr(main_window, "ax") else None
        canvas = main_window.canvas if hasattr(main_window, "canvas") else None
        if ax is None or canvas is None:
            return

        # Если есть имена и scale-факторы линий, обновляем подписи линий для легенды
        if hasattr(canvas, "_osc_viewer_line_names") and hasattr(canvas, "_osc_viewer_scale_factors"):
            for l in ax.lines:
                name = canvas._osc_viewer_line_names.get(l, "График")
                scale = canvas._osc_viewer_scale_factors.get(l, 1.0)
                # Формируем подпись с учётом scale-фактора, если требуется
                if add_scale_label:
                    l.set_label(f"{name} (x{scale:.2f})")
                else:
                    l.set_label(f"{name}")

        # Если есть линии — отображаем легенду, иначе удаляем её
        if ax.lines:
            ax.legend(loc="best")
        else:
            if hasattr(ax, "legend_") and ax.legend_:
                ax.legend_.remove()
        # Перерисовываем холст для отображения изменений
        canvas.draw_idle()

    def create_canvas(main_window):
        '''
        Создаёт и инициализирует холст Matplotlib и панель инструментов внутри родительского виджета.
        Метод проверяет наличие layout у родительского виджета; если его нет — создаёт QVBoxLayout.
        Затем очищает layout от существующих виджетов, создаёт новый объект Figure и FigureCanvas,
        добавляет subplot к Figure и размещает панель инструментов Matplotlib и сам холст в layout.
        Побочные эффекты:
            - Модифицирует layout родительского виджета: удаляет старые виджеты, добавляет новую панель инструментов и холст.
        '''
        # Инициализация Figure, Canvas и Toolbar для отображения графика внутри виджета.

        # Получаем layout родительского виджета (если его нет — создаём новый QVBoxLayout)
        layout = main_window.parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(main_window.parent_widget)
            main_window.parent_widget.setLayout(layout)
        # Если add_mode=False, очищаем область и создаём новую Figure
        # Удаляем все существующие виджеты из layout (например, старые графики и toolbar)
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        # Создаём объект Figure (контейнер для графиков) размером 5x3 дюйма
        main_window.figure = Figure(figsize=(5, 3))
        # Оборачиваем Figure в FigureCanvas для интеграции matplotlib-графика в Qt-интерфейс
        main_window.canvas = FigureCanvas(main_window.figure)
        # Добавляем одну область построения (ось) к Figure (1 строка, 1 столбец, 1-я позиция)
        main_window.ax = main_window.figure.add_subplot(111)
        # Создаём панель инструментов (Toolbar) для управления графиком
        toolbar = NavigationToolbar(main_window.canvas, main_window.parent_widget)
        # Добавляем toolbar и canvas (график) в layout
        layout.addWidget(toolbar)
        layout.addWidget(main_window.canvas)

    def get_index_active_line(main_window):
        '''
        Возвращает индекс активной линии на холсте.

        Метод получает значение атрибута '_osc_viewer_active_index' из объекта canvas.
        Если атрибут отсутствует, возвращает None.
        '''
        return getattr(main_window.canvas, "_osc_viewer_active_index", None)

    def get_active_line(main_window):
        '''
        Возвращает текущую активную линию из FigureCanvas, находящегося в layout родительского виджета.
        Возвращает:
            Объект активной линии, если он найден, иначе None.
        '''
        # Используем атрибуты экземпляра класса для доступа к canvas и активной линии
        if not hasattr(main_window, "canvas"):
            return None
        return getattr(main_window.canvas, "_osc_viewer_active_line", None)
    
    def get_active_line_params(main_window):
        '''
        Возвращает параметры активной линии графика.

        Метод получает активную линию с помощью main_window.get_active_line() и возвращает её параметры:
        цвет, стиль линии и подпись (label) в виде словаря. Если активная линия не найдена,
        возвращает None.

        Returns:
            dict | None: Словарь с параметрами линии {'color': цвет, 'linestyle': стиль, 'label': подпись}
            или None, если активная линия отсутствует.
        '''

        # Получаем активную линию
        line = main_window.get_active_line()
        if line is None:
            # Если активная линия не найдена, возвращаем None
            return None
        # Получаем параметры линии: цвет, стиль, подпись (label)
        color = line.get_color()
        linestyle = line.get_linestyle()
        label = line.get_label()
        # Возвращаем параметры в виде словаря
        return {"color": color, "linestyle": linestyle, "label": label}

    def remove_active_line(main_window):
        '''
        Удаляет активную линию с графика.
        Метод выполняет следующие действия:
        - Проверяет наличие линий на графике. Если линий нет — ничего не делает.
        - Определяет активную линию с помощью метода get_active_line(). Если активная линия не найдена или отсутствует среди линий оси — ничего не делает.
        - Удаляет активную линию с графика.
        - Если удалённая линия была активной, обновляет ссылку на активную линию и её индекс: если остались другие линии — делает последнюю активной, иначе сбрасывает активную линию и индекс.
        - Удаляет связанные с линией метаданные (имя, scale-фактор), если они присутствуют.
        - Обновляет легенду графика без учёта scale-фактора.
        - Перерисовывает холст для отображения изменений.
        '''
        # Получаем объекты оси и холста
        ax = main_window.ax
        canvas = main_window.canvas

        # Если нет линий на графике — ничего не делаем
        if not ax.lines:
            return

        # Получаем активную линию
        line_to_remove = main_window.get_active_line()
        # Если активная линия не найдена или её нет среди линий — ничего не делаем
        if line_to_remove is None or line_to_remove not in ax.lines:
            return

        # Удаляем линию с графика
        line_to_remove.remove()

        # Если удаляемая линия была активной — обновляем активную линию и её индекс
        if (
            hasattr(canvas, "_osc_viewer_active_line")
            and canvas._osc_viewer_active_line is line_to_remove
        ):
            if ax.lines:
                # Если остались линии — делаем последнюю активной
                canvas._osc_viewer_active_line = ax.lines[-1]
                canvas._osc_viewer_active_index = len(ax.lines) - 1
            else:
                # Если линий не осталось — сбрасываем активную линию и индекс
                canvas._osc_viewer_active_line = None
                canvas._osc_viewer_active_index = None

        # Удаляем метаданные линии (имя, scale-фактор) если они есть
        if hasattr(canvas, "_osc_viewer_line_names"):
            canvas._osc_viewer_line_names.pop(line_to_remove, None)
        if hasattr(canvas, "_osc_viewer_scale_factors"):
            canvas._osc_viewer_scale_factors.pop(line_to_remove, None)

        # Обновляем легенду без scale-фактора
        main_window.update_legend(add_scale_label=False)
        # Перерисовываем холст для отображения изменений
        canvas.draw_idle()

    def clear_canvas(main_window):
        '''
        Очищает текущую ось графика и обновляет холст.

        Этот метод удаляет все элементы с текущей оси (main_window.ax) и инициирует перерисовку холста (main_window.canvas)
        без задержки, чтобы отобразить изменения. Используется для сброса содержимого графика перед построением новых данных.
        '''
        # Очищаем ось и перерисовываем холст с помощью атрибутов экземпляра
        main_window.ax.clear()
        main_window.canvas.draw_idle()

    def set_axes_params(
        main_window,
        xlim=None,
        ylim=None,
        grid=True,
        legend=True,
        title=None,
        xlabel=None,
        ylabel=None,
        grid_kwargs=None,
    ):
        '''
        Устанавливает параметры отображения графика: пределы по осям, сетку, легенду, заголовок и подписи осей.

        Параметры:
            xlim (tuple, optional): Пределы по оси X (min, max).
            ylim (tuple, optional): Пределы по оси Y (min, max).
            grid (bool, optional): Включить или выключить сетку (по умолчанию True).
            legend (bool, optional): Показывать легенду (по умолчанию True).
            title (str, optional): Заголовок графика.
            xlabel (str, optional): Подпись оси X.
            ylabel (str, optional): Подпись оси Y.
            grid_kwargs (dict, optional): Дополнительные параметры для сетки (например, {'linestyle': '--', 'color': 'gray'}).

        Описание:
            Позволяет комплексно настроить внешний вид графика: задать пределы осей, включить/выключить сетку, 
            отобразить легенду, установить заголовок и подписи осей. Поддерживает передачу дополнительных параметров 
            для настройки внешнего вида сетки через grid_kwargs.
        '''
        # Получаем объекты оси и холста, если они существуют
        ax = main_window.ax if hasattr(main_window, "ax") else None
        canvas = main_window.canvas if hasattr(main_window, "canvas") else None
        if ax is None or canvas is None:
            return

        # Устанавливаем пределы по оси X, если указаны
        if xlim is not None:
            ax.set_xlim(*xlim)
        # Устанавливаем пределы по оси Y, если указаны
        if ylim is not None:
            ax.set_ylim(*ylim)
        # Устанавливаем заголовок графика, если указан
        if title is not None:
            ax.set_title(title)
        # Устанавливаем подпись оси X, если указана
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        # Устанавливаем подпись оси Y, если указана
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        # Включаем или отключаем сетку, поддерживаем дополнительные параметры для сетки
        if grid:
            if grid_kwargs is not None:
                ax.grid(True, **grid_kwargs)
            else:
                ax.grid(True)
        else:
            ax.grid(False)
        # Показываем легенду, если требуется
        if legend:
            main_window.update_legend()
        # Перерисовываем холст для отображения изменений
        canvas.draw_idle()

    # Добавим методы для работы с линиями спектра через PlotData
    def get_all_lines(main_window):
        '''
        Возвращает список всех линий на текущей оси графика.
        Использует атрибуты main_window.ax.
        '''
        if not hasattr(main_window, "ax"):
            return []
        return list(main_window.ax.lines)

    def get_line_params(main_window, line):
        '''
        Возвращает параметры указанной линии графика.

        Args:
            line: matplotlib Line2D объект.

        Returns:
            dict: Словарь с параметрами линии {'color': цвет, 'linestyle': стиль, 'label': подпись}.
        '''
        if line is None or not hasattr(main_window, "ax") or line not in main_window.ax.lines:
            return None
        color = line.get_color()
        linestyle = line.get_linestyle()
        label = line.get_label()
        return {"color": color, "linestyle": linestyle, "label": label}

    def plot_line(
        main_window,
        x,
        y,
        *,
        x_zoom=1,
        y_zoom=1,
        color=None,
        linestyle=None,
        label=None,
        add_scale_label=True,
        add_mode=False,
    ):
        '''
        Строит линию на графике с возможностью задания параметров отображения и масштабирования.
        Параметры:
            x (array-like): Массив значений по оси X.
            y (array-like): Массив значений по оси Y.
            x_zoom (float, optional): Коэффициент масштабирования по оси X (по умолчанию 1).
            y_zoom (float, optional): Коэффициент масштабирования по оси Y (по умолчанию 1).
            color (str или None, optional): Цвет линии (по умолчанию None — выбирается автоматически).
            linestyle (str или None, optional): Стиль линии (по умолчанию None — сплошная линия).
            label (str или None, optional): Имя линии для легенды (по умолчанию None).
            add_scale_label (bool, optional): Добавлять ли к имени линии коэффициент масштабирования (по умолчанию True).
            add_mode (bool, optional): Если True — добавляет линию к уже существующим, если False — очищает холст перед добавлением (по умолчанию False).
        Функциональность:
            - Масштабирует входные данные по X и Y.
            - Добавляет линию на график с заданными параметрами.
            - Позволяет управлять активной линией с помощью клавиатуры:
                * Пробел — переключение между линиями.
                * Delete — удаление активной линии с подтверждением.
                * Стрелки — сдвиг активной линии по X или Y.
            - Масштабирование активной линии по оси Y с помощью колесика мыши при зажатом Shift.
            - Двойной клик мыши по графику — авто-масштабирование по оси X.
            - Обновляет легенду и визуальное выделение активной линии.
            - Сохраняет имена и коэффициенты масштабирования для каждой линии.
        Использует:
            - Методы и параметры класса PlotData.
            - Внутренние атрибуты canvas для хранения состояния линий.
        # Масштабируем входные данные по X и Y
        x = np.array(x) * x_zoom
        y = np.array(y) * y_zoom
        '''
        # Масштабируем входные данные по X и Y
        x = np.array(x) * x_zoom
        y = np.array(y) * y_zoom

        # --- Вспомогательные обработчики событий для plot_line ---
        # Обработчик нажатия клавиш для управления активной линией
        def on_key(event):
            '''
            Обрабатывает нажатия клавиш для управления активной линией на графике.
            Функциональность:
            - Пробел (" "): Переключает активную линию среди всех линий на графике. Активная линия визуально выделяется (увеличенная толщина, непрозрачность, z-порядок).
            - Delete: Запрашивает подтверждение и удаляет активную линию с графика.
            - Стрелки (влево, вправо, вверх, вниз): Сдвигают активную линию по оси X или Y на 1% диапазона текущей оси.
            - Если активная линия не выбрана, автоматически выбирает последнюю добавленную линию.
            - Перемещение линий может быть заблокировано внешней логикой (через атрибут _osc_viewer_move_locked).
            Параметры:
                event: объект события клавиатуры (обычно matplotlib.backend_bases.KeyEvent), содержащий информацию о нажатой клавише.
            Примечания:
                Для удаления линии используется диалог подтверждения (QMessageBox).
                Для корректной работы требуется наличие атрибутов main_window.canvas, main_window.ax и main_window.parent_widget.
            '''
            # Проверяем, что активная линия существует, иначе делаем последнюю активной
            if (
                not hasattr(main_window.canvas, "_osc_viewer_active_line")
                or main_window.canvas._osc_viewer_active_line not in main_window.ax.lines
            ):
                if not main_window.ax.lines:
                    return
                main_window.canvas._osc_viewer_active_line = main_window.ax.lines[-1]
                main_window.canvas._osc_viewer_active_index = len(main_window.ax.lines) - 1

            line = main_window.canvas._osc_viewer_active_line
            xdata = line.get_xdata()
            xlim = main_window.ax.get_xlim()
            delta_x = (xlim[1] - xlim[0]) * 0.01  # Шаг сдвига по X (1% диапазона)
            ydata = line.get_ydata()
            ylim = main_window.ax.get_ylim()
            delta_y = (ylim[1] - ylim[0]) * 0.01  # Шаг сдвига по Y (1% диапазона)

            # Пробел — переключение активной линии
            if event.key == " ":
                num_lines = len(main_window.ax.lines)
                if num_lines == 0:
                    return
                idx = getattr(main_window.canvas, "_osc_viewer_active_index", len(main_window.ax.lines) - 1)
                if idx is None:
                    idx = len(main_window.ax.lines) - 1
                idx = (idx + 1) % num_lines  # Следующая линия по кругу
                main_window.canvas._osc_viewer_active_line = main_window.ax.lines[idx]
                main_window.canvas._osc_viewer_active_index = idx
                # Визуально выделяем активную линию (толще, выше z-порядок, непрозрачная)
                for l in main_window.ax.lines:
                    l.set_zorder(1)
                    l.set_linewidth(1.0)
                    l.set_alpha(0.7)
                main_window.ax.lines[idx].set_zorder(10)
                main_window.ax.lines[idx].set_linewidth(2.5)
                main_window.ax.lines[idx].set_alpha(1.0)
                main_window.canvas.draw_idle()
            # Delete — удаление активной линии с подтверждением
            elif event.key == "delete":
                num_lines = len(main_window.ax.lines)
                if num_lines == 0:
                    return
                idx = getattr(main_window.canvas, "_osc_viewer_active_index", len(main_window.ax.lines) - 1)
                if idx is None:
                    idx = len(main_window.ax.lines) - 1
                if idx < 0 or idx >= len(main_window.ax.lines):
                    return
                # Показываем диалог подтверждения удаления
                msg = QMessageBox(main_window.parent_widget)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Удалить график")
                msg.setText("Вы действительно хотите удалить выбранный график?")
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                ret = msg.exec()
                if ret == QMessageBox.StandardButton.Yes:
                    main_window.remove_line(idx)
            # Проверяем, заблокировано ли перемещение линий (например, внешней логикой)
            if (
                hasattr(main_window.canvas, "_osc_viewer_move_locked")
                and main_window.canvas._osc_viewer_move_locked
            ):
                return
            # Стрелки — сдвиг активной линии по X или Y
            if event.key in ["left"]:
                xdata = xdata - delta_x  # Сдвиг по X влево
                line.set_xdata(xdata)
                main_window.ax.relim()
                main_window.ax.autoscale_view()
                main_window.canvas.draw_idle()
            elif event.key in ["right"]:
                xdata = xdata + delta_x  # Сдвиг по X вправо
                line.set_xdata(xdata)
                main_window.ax.relim()
                main_window.ax.autoscale_view()
                main_window.canvas.draw_idle()
            elif event.key in ["up"]:
                ydata = ydata + delta_y  # Сдвиг по Y вверх
                line.set_ydata(ydata)
                main_window.ax.relim()
                main_window.ax.autoscale_view()
                main_window.canvas.draw_idle()
            elif event.key in ["down"]:
                ydata = ydata - delta_y  # Сдвиг по Y вниз
                line.set_ydata(ydata)
                main_window.ax.relim()
                main_window.ax.autoscale_view()
                main_window.canvas.draw_idle()

        # Обработчик колесика мыши для масштабирования по оси Y при зажатом Shift
        def on_scroll(event):
            '''
            Обрабатывает событие прокрутки колесика мыши для масштабирования активной линии на графике.

            Параметры:
                event: объект события прокрутки мыши, предоставляемый matplotlib или соответствующим backend'ом.

            Описание:
                - Функция реагирует только если курсор находится в области осей (main_window.ax) и зажат модификатор Shift.
                - Определяет направление прокрутки (увеличение или уменьшение масштаба) с учетом особенностей разных backend'ов.
                - Масштабирует данные активной линии относительно её центра.
                - Обновляет коэффициент масштабирования и подпись линии, если соответствующие атрибуты присутствуют.
                - Перерисовывает легенду и график для отображения изменений.

            Примечание:
                Для корректной работы требуется наличие атрибутов _osc_viewer_active_line, _osc_viewer_scale_factors и _osc_viewer_line_names у canvas.
            '''
            # Проверяем, что событие произошло в области осей графика
            if event.inaxes != main_window.ax:
                return
            # Проверяем, что зажат модификатор Shift
            modifiers = QApplication.keyboardModifiers()
            if not (modifiers & Qt.KeyboardModifier.ShiftModifier):
                return
            # Получаем активную линию
            active_line = getattr(main_window.canvas, "_osc_viewer_active_line", None)
            if active_line is None or active_line not in main_window.ax.lines:
                return
            # Определяем направление прокрутки (вверх/вниз) для разных backend'ов
            step = getattr(event, "step", None)
            if step is None:
                # Для некоторых backend'ов event.button — 'up' или 'down'
                if hasattr(event, "button") and isinstance(event.button, str):
                    step = 1 if event.button == "up" else -1
                # Для Qt backend event.delta — int
                elif hasattr(event, "delta"):
                    step = 1 if event.delta > 0 else -1
                else:
                    step = 1  # По умолчанию увеличиваем масштаб
            # Выбираем коэффициент масштабирования
            scale = 1.2 if step > 0 else 1 / 1.2
            # Получаем данные по Y и центрируем их
            ydata = active_line.get_ydata()
            ycenter = np.mean(ydata)
            # Масштабируем данные относительно центра
            ydata_scaled = (ydata - ycenter) * scale + ycenter
            active_line.set_ydata(ydata_scaled)
            # Обновляем масштабный коэффициент и подпись линии, если есть соответствующие атрибуты
            if hasattr(main_window.canvas, "_osc_viewer_scale_factors"):
                main_window.canvas._osc_viewer_scale_factors[active_line] *= scale
                name = main_window.canvas._osc_viewer_line_names.get(active_line, "График") if hasattr(main_window.canvas, "_osc_viewer_line_names") else "График"
                new_scale = main_window.canvas._osc_viewer_scale_factors[active_line]
                active_line.set_label(f"{name} (x{new_scale:.2f})")
            # Обновляем легенду и перерисовываем график
            main_window.ax.legend()
            main_window.canvas.draw_idle()

        # Обработчик двойного клика мыши для авто-масштабирования по X
        def on_double_click(event):
            '''
            Обрабатывает двойной клик мыши по области графика для автоматического масштабирования оси X.

            Параметры:
            event: объект события мыши matplotlib (MouseEvent).

            Описание:
            - Если событие — двойной клик (event.dblclick) и курсор находится в области осей (event.inaxes == main_window.ax),
              вычисляет минимальное и максимальное значение X среди всех линий на графике.
            - Устанавливает пределы оси X (set_xlim) по этим значениям.
            - Перерисовывает холст для отображения изменений.
            '''
            if event.dblclick and event.inaxes == main_window.ax:
                # Собираем все X-координаты всех линий на графике, если они не пустые
                x_arrays = [line.get_xdata() for line in main_window.ax.lines if hasattr(line, "get_xdata") and getattr(line.get_xdata(), "size", 0) > 0]
                if x_arrays:
                    all_x = np.concatenate(x_arrays)
                    if all_x.size > 0:
                        # Устанавливаем пределы оси X по минимальному и максимальному значению
                        main_window.ax.set_xlim(np.min(all_x), np.max(all_x))
                        # Перерисовываем холст для отображения изменений
                        main_window.canvas.draw_idle()

        # --------------------------------------------------------------

        # Если add_mode=False, очищаем холст перед добавлением новой линии
        if not add_mode:
            main_window.clear_canvas()

        # Добавляем график с заданными параметрами
        scale = y_zoom
        (line,) = main_window.ax.plot(
            x,
            y,
            color=color,
            linestyle=linestyle,
            label=f"{label} (x{scale:.2f})" if add_scale_label and label else label,
        )

        # --- Сохраняем имя и scale-фактор для линии ---
        if not hasattr(main_window.canvas, "_osc_viewer_line_names"):
            main_window.canvas._osc_viewer_line_names = {}
        if not hasattr(main_window.canvas, "_osc_viewer_scale_factors"):
            main_window.canvas._osc_viewer_scale_factors = {}

        # Сохраняем имя и масштабный коэффициент для линии
        main_window.canvas._osc_viewer_line_names[line] = label if label else f"График {len(main_window.ax.lines)}"
        main_window.canvas._osc_viewer_scale_factors[line] = scale

        # Сохраняем активную линию и её индекс
        main_window.canvas._osc_viewer_active_line = line
        main_window.canvas._osc_viewer_active_index = len(main_window.ax.lines) - 1

        # Настройка подписей осей, заголовка и сетки
        main_window.ax.set_xlabel("time, ms")
        main_window.ax.set_ylabel("U,V")
        main_window.ax.set_title("Осциллограмма сигнала")
        main_window.ax.grid(True)
        # Устанавливаем пределы по X, если есть данные
        if len(x) > 0:
            main_window.ax.set_xlim(min(x), x[-1])
        main_window.canvas.draw_idle()

        # Подключаем обработчик клавиш, отключая предыдущий если был
        if hasattr(main_window.canvas, "_osc_viewer_key_cid"):
            main_window.canvas.mpl_disconnect(main_window.canvas._osc_viewer_key_cid)
        main_window.canvas._osc_viewer_key_cid = main_window.canvas.mpl_connect("key_press_event", on_key)
        main_window.canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_window.canvas.setFocus()

        # Подключаем обработчик двойного клика, отключая предыдущий если был
        if hasattr(main_window.canvas, "_osc_viewer_double_click_cid"):
            main_window.canvas.mpl_disconnect(main_window.canvas._osc_viewer_double_click_cid)
        main_window.canvas._osc_viewer_double_click_cid = main_window.canvas.mpl_connect(
            "button_press_event", on_double_click
        )

        # Подключаем обработчик колесика мыши, отключая предыдущий если был
        if hasattr(main_window.canvas, "_osc_viewer_scroll_cid"):
            main_window.canvas.mpl_disconnect(main_window.canvas._osc_viewer_scroll_cid)
        main_window.canvas._osc_viewer_scroll_cid = main_window.canvas.mpl_connect("scroll_event", on_scroll)

        # Обновляем легенду графика
        main_window.update_legend()
