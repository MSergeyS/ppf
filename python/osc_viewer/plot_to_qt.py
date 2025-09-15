import numpy as np  # Для работы с массивами
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QMessageBox


def on_press(event):
    print('press', event.key)
    # The following code referenced an undefined variable 'xl' and has been removed or should be implemented if needed.
    # if event.key == '<':
    #     visible = xl.get_visible()
    #     xl.set_visible(not visible)
    #     fig.canvas.draw()


def plot_signal_to_qt(parent_widget, t, s, add_mode=False):
    """
    Строит график осциллограммы и выводит его в главное окно Qt.
    parent_widget — QWidget, в который будет встроен график.
    t, s — массивы времени и сигнала.
    add_mode — если True, добавляет график поверх существующего, иначе очищает область.
    """
    t_ms = np.array(t) * 1000
    s_arr = np.array(s)

    layout = parent_widget.layout()
    if layout is None:
        layout = QVBoxLayout(parent_widget)
        parent_widget.setLayout(layout)

    # Если add_mode=False, очищаем область и создаём новую Figure
    if not add_mode:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        fig = Figure(figsize=(5, 3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        toolbar = NavigationToolbar(canvas, parent_widget)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
    else:
        # Если add_mode=True, ищем существующий FigureCanvas
        canvas = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas is None:
            # Если нет, создаём новый
            fig = Figure(figsize=(5, 3))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            toolbar = NavigationToolbar(canvas, parent_widget)
            layout.addWidget(toolbar)
            layout.addWidget(canvas)
        else:
            fig = canvas.figure
            ax = fig.gca()

    # Добавляем график
    ax.plot(t_ms, s_arr)

    # Добавляем обработчик клавиш для смещения только последнего добавленного графика
    def on_key(event):
        # Получаем только последний добавленный Line2D (активный график)
        if not hasattr(canvas, "_osc_viewer_active_line"):
            if not ax.lines:
                return
            canvas._osc_viewer_active_line = ax.lines[-1]
            canvas._osc_viewer_active_index = len(ax.lines) - 1
        line = canvas._osc_viewer_active_line
        xdata = line.get_xdata()
        # Получаем текущий видимый диапазон оси X
        xlim = ax.get_xlim()
        delta = (xlim[1] - xlim[0]) * 0.01  # 1% от текущего масштаба

        if event.key in ['left', '<']:
            xdata = xdata - delta
            line.set_xdata(xdata)
            ax.relim()
            ax.autoscale_view()
            canvas.draw()
        elif event.key in ['right', '>']:
            xdata = xdata + delta
            line.set_xdata(xdata)
            ax.relim()
            ax.autoscale_view()
            canvas.draw()
        elif event.key == ' ':
            # Переключение активного графика по пробелу
            num_lines = len(ax.lines)
            if num_lines == 0:
                return
            # Получаем текущий индекс
            if len(ax.lines) == 0:
                return
            idx = getattr(canvas, "_osc_viewer_active_index", len(ax.lines) - 1)
            if idx is None:
                idx = len(ax.lines) - 1
            # Следующий индекс (циклически)
            idx = (idx + 1) % num_lines
            # Обновляем активный график и индекс
            canvas._osc_viewer_active_line = ax.lines[idx]
            canvas._osc_viewer_active_index = idx
            # Сбросить стиль всех линий
            for _, l in enumerate(ax.lines):
                l.set_zorder(1)
                l.set_linewidth(1.0)
                l.set_alpha(0.7)
            # Активная линия — поверх и толще
            ax.lines[idx].set_zorder(10)
            ax.lines[idx].set_linewidth(2.5)
            ax.lines[idx].set_alpha(1.0)
            # Перерисовать
            fig.canvas.draw_idle()
        elif event.key == 'delete':
            # Удаление активной линии с подтверждением
            num_lines = len(ax.lines)
            if num_lines == 0:
                return
            idx = getattr(canvas, "_osc_viewer_active_index", len(ax.lines) - 1)
            if idx is None:
                idx = len(ax.lines) - 1
            if idx < 0 or idx >= len(ax.lines):
                return
            msg = QMessageBox(parent_widget)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Удалить график")
            msg.setText("Вы действительно хотите удалить выбранный график?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            ret = msg.exec()
            if ret == QMessageBox.StandardButton.Yes:
                line_to_remove = ax.lines[idx]
                line_to_remove.remove()
                # Не нужно явно удалять line_to_remove, matplotlib сам управляет памятью
                # Обновить активную линию и индекс
                if ax.lines:
                    # Сбросить стиль всех линий
                    for i, l in enumerate(ax.lines):
                        l.set_zorder(1)
                        l.set_linewidth(1.0)
                        l.set_alpha(0.7)
                    # Выбрать новую активную линию (первая в списке)
                    new_idx = 0
                    canvas._osc_viewer_active_line = ax.lines[new_idx]
                    canvas._osc_viewer_active_index = new_idx
                    # Активная линия — поверх и толще
                    ax.lines[new_idx].set_zorder(10)
                    ax.lines[new_idx].set_linewidth(2.5)
                    ax.lines[new_idx].set_alpha(1.0)
                else:
                    canvas._osc_viewer_active_line = None
                    canvas._osc_viewer_active_index = None
                fig.canvas.draw_idle()
    # Сохраняем ссылку на последний добавленный график
    canvas._osc_viewer_active_line = ax.lines[-1]

    # Удаляем предыдущий обработчик, если он был
    if hasattr(canvas, "_osc_viewer_key_cid"):
        canvas.mpl_disconnect(canvas._osc_viewer_key_cid)
    canvas._osc_viewer_key_cid = canvas.mpl_connect('key_press_event', on_key)
    # Устанавливаем фокус на canvas для получения событий клавиатуры
    canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    canvas.setFocus()
    canvas.setFocus()

    ax.set_xlabel("time, ms")
    ax.set_ylabel("U,V")
    ax.set_title("Осциллограмма сигнала")
    ax.grid(True)
    if len(t_ms) > 0:
        ax.set_xlim(min(t_ms), t_ms[-1])
    canvas.draw()
