import numpy as np  # Для работы с массивами
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QMessageBox


class PlotData:
    def __init__(self, parent_widget, data=None):
        """
        Initializes the PlotData object.

        Args:
            parent_widget: The parent widget to which this object belongs.
            data (optional): The data to be associated with this object. Defaults to None.
        """
        self.parent_widget = parent_widget
        self.data = data

    def get_data(self):
        return self.data

    def remove_line(self, inx_line_to_remove=None):
        """
        Removes a line from the plot displayed in the parent widget's FigureCanvas.

        Parameters:
            inx_line_to_remove (int, optional): The index of the line to remove from the plot.
                If None, removes the last (topmost) line. Defaults to None.

        Behavior:
            - Locates the FigureCanvas within the parent widget's layout.
            - Removes the specified line from the plot's Axes.
            - Updates the active line and its index if the removed line was active.
            - Removes associated metadata (line names and scale factors) if present.
            - Updates the plot legend to reflect the current lines.
            - Redraws the canvas to reflect changes.

        Notes:
            - If the layout, canvas, or lines are not found, the function returns without action.
            - If the specified index is out of bounds, the function returns without action.
        """
        layout = self.parent_widget.layout()
        if layout is None:
            return
        # Find the FigureCanvas
        canvas = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas is None:
            return
        ax = canvas.figure.gca()
        if not ax.lines:
            return
        # By default, remove the top (last) line
        if inx_line_to_remove is None:
            inx_line_to_remove = len(ax.lines) - 1
        if inx_line_to_remove < 0 or inx_line_to_remove >= len(ax.lines):
            return
        line_to_remove = ax.lines[inx_line_to_remove]
        line_to_remove.remove()
        # Update active line/index if needed
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
        # Remove from legend helpers if present
        if hasattr(canvas, "_osc_viewer_line_names"):
            canvas._osc_viewer_line_names.pop(line_to_remove, None)
        if hasattr(canvas, "_osc_viewer_scale_factors"):
            canvas._osc_viewer_scale_factors.pop(line_to_remove, None)

        # Update legend if function exists
        def update_legend():
            for l in ax.lines:
                name = getattr(canvas, "_osc_viewer_line_names", {}).get(l, "График")
                scale = getattr(canvas, "_osc_viewer_scale_factors", {}).get(l, 1.0)
                l.set_label(f"{name} (x{scale:.2f})")
            if ax.lines:
                ax.legend(loc="best")
            else:
                ax.legend_.remove() if hasattr(ax, "legend_") and ax.legend_ else None
            canvas.draw_idle()

        update_legend()
        canvas.draw_idle()

    def create_canvas(self):
        """
        Creates and initializes a Matplotlib canvas and toolbar within the parent widget.

        This method checks if the parent widget has a layout; if not, it creates a QVBoxLayout.
        It then clears any existing widgets from the layout, creates a new Matplotlib Figure and FigureCanvas,
        adds a subplot to the figure, and adds both the Matplotlib navigation toolbar and the canvas to the layout.

        Side Effects:
            - Modifies the layout of the parent widget by removing existing widgets and adding a new toolbar and canvas.
        """
        layout = self.parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(self.parent_widget)
            self.parent_widget.setLayout(layout)
        # Если add_mode=False, очищаем область и создаём новую Figure
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        fig = Figure(figsize=(5, 3))
        canvas = FigureCanvas(fig)
        fig.add_subplot(111)
        toolbar = NavigationToolbar(canvas, self.parent_widget)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

    def get_index_active_line(self):
        """
        Retrieves the index of the currently active line in the plot.

        This method searches for a FigureCanvas widget within the parent widget's layout.
        If found, it returns the value of the '_osc_viewer_active_index' attribute from the canvas,
        which represents the index of the active line. If the layout, canvas, or attribute is not found,
        returns None.

        Returns:
            int or None: The index of the active line if available, otherwise None.
        """
        layout = self.parent_widget.layout()
        if layout is None:
            return None
        # Find the FigureCanvas
        canvas = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas is None:
            return None
        return getattr(canvas, "_osc_viewer_active_index", None)

    def get_active_line(self):
        """
        Retrieves the currently active line from the FigureCanvas within the parent widget's layout.

        Returns:
            The active line object if found, otherwise None.
        """
        layout = self.parent_widget.layout()
        if layout is None:
            return None
        # Find the FigureCanvas
        canvas = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas is None:
            return None
        return getattr(canvas, "_osc_viewer_active_line", None)

    def remove_active_line(self):
        layout = self.parent_widget.layout()
        if layout is None:
            return
        # Find the FigureCanvas
        canvas = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas is None:
            return
        ax = canvas.figure.gca()
        if not ax.lines:
            return
        line_to_remove = getattr(canvas, "_osc_viewer_active_line", None)
        if line_to_remove is None or line_to_remove not in ax.lines:
            return
        line_to_remove.remove()
        # Update active line/index if needed
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
        # Remove from legend helpers if present
        if hasattr(canvas, "_osc_viewer_line_names"):
            canvas._osc_viewer_line_names.pop(line_to_remove, None)
        if hasattr(canvas, "_osc_viewer_scale_factors"):
            canvas._osc_viewer_scale_factors.pop(line_to_remove, None)

        # Update legend if function exists
        def update_legend():
            for l in ax.lines:
                name = getattr(canvas, "_osc_viewer_line_names", {}).get(l, "График")
                scale = getattr(canvas, "_osc_viewer_scale_factors", {}).get(l, 1.0)
                l.set_label(f"{name} (x{scale:.2f})")
            ax.legend(loc="best")
            canvas.draw_idle()

        update_legend(add_scale_label=False)
        canvas.draw_idle()

    def clear_canvas(self):
        layout = self.parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(self.parent_widget)
            self.parent_widget.setLayout(layout)
        # Очищаем область и удаляем все виджеты
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def get_active_line_params(self):
        """
        Возвращает параметры активной линии: цвет, стиль, имя (label).
        """
        line = self.get_active_line()
        if line is None:
            return None
        color = line.get_color()
        linestyle = line.get_linestyle()
        label = line.get_label()
        return {"color": color, "linestyle": linestyle, "label": label}

    def plot_line(
        self,
        x,
        y,
        *,
        x_zoom=1,
        y_zoom=1,
        add_mode=False,
        color=None,
        linestyle=None,
        label=None,
        add_scale_label=True,
    ):
        """
        Строит линию с возможностью задания параметров (цвет, стиль, имя) и масштабирования.
        """
        # Для каждой линии графика будет храниться scale-фактор в словаре canvas._osc_viewer_scale_factors.
        # Этот scale будет обновляться при масштабировании (on_scroll) и отображаться в легенде.
        print(
            "Строим линию с параметрами:",
            f"x_zoom={x_zoom}, y_zoom={y_zoom}, add_mode={add_mode}, color={color}, linestyle={linestyle}, label={label}",
        )
        x = np.array(x) * x_zoom
        y = np.array(y) * y_zoom
        layout = self.parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(self.parent_widget)
            self.parent_widget.setLayout(layout)

        if add_mode:
            canvas = None
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, FigureCanvas):
                    canvas = widget
                    break
            if canvas is not None:
                fig = canvas.figure
                ax = fig.gca()
            else:
                fig = Figure(figsize=(5, 3))
                canvas = FigureCanvas(fig)
                ax = fig.add_subplot(111)
                toolbar = NavigationToolbar(canvas, self.parent_widget)
                layout.addWidget(toolbar)
                layout.addWidget(canvas)
        else:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            fig = Figure(figsize=(5, 3))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            toolbar = NavigationToolbar(canvas, self.parent_widget)
            layout.addWidget(toolbar)
            layout.addWidget(canvas)

        # Добавляем график с параметрами
        scale = y_zoom  # или другой актуальный scale-фактор

        # При добавлении линии (plot_line)
        (line,) = ax.plot(
            x,
            y,
            color=color,
            linestyle=linestyle,
            label=f"{label} (x{scale:.2f})" if add_scale_label else label,
        )
        # --- Сохраняем file_name и scale-фактор для линии ---
        if not hasattr(canvas, "_osc_viewer_file_names"):
            canvas._osc_viewer_file_names = {}
        canvas._osc_viewer_file_names[line] = label  # file_name — имя файла для этой линии

        if not hasattr(canvas, "_osc_viewer_scale_factors"):
            canvas._osc_viewer_scale_factors = {}
        canvas._osc_viewer_scale_factors[line] = scale  # scale — scale-фактор для этой линии
        line.selected = True

        # Сохраняем ссылку на последний добавленный график
        canvas._osc_viewer_active_line = line
        canvas._osc_viewer_active_index = len(ax.lines) - 1

        # Легенда и имена линий
        if not hasattr(canvas, "_osc_viewer_line_names"):
            canvas._osc_viewer_line_names = {}
        if not hasattr(canvas, "_osc_viewer_scale_factors"):
            canvas._osc_viewer_scale_factors = {}

        is_new_line = line not in canvas._osc_viewer_line_names
        if is_new_line:
            canvas._osc_viewer_line_names[line] = (
                label if label else f"График {len(ax.lines)}"
            )
        if line not in canvas._osc_viewer_scale_factors:
            canvas._osc_viewer_scale_factors[line] = 1.0

        def format_line_label(name, scale, add_scale_label=True):
            if add_scale_label:
                return f"{name} (x{scale:.2f})"
            else:
                return f"{name}"

        def update_legend():
            for l in ax.lines:
                name = canvas._osc_viewer_line_names.get(l, "График")
                scale = canvas._osc_viewer_scale_factors.get(l, 1.0)
                l.set_label(f"{name} (x{scale:.2f})")
            ax.legend(loc="best")
            canvas.draw_idle()

        # Настройка осей и сетки
        ax.set_xlabel("time, ms")
        ax.set_ylabel("U,V")
        ax.set_title("Осциллограмма сигнала")
        ax.grid(True)
        if len(x) > 0:
            ax.set_xlim(min(x), x[-1])
        canvas.draw()

        # Обработчики событий (клавиши, колесо, двойной клик)
        def on_key(event):
            if not hasattr(canvas, "_osc_viewer_active_line"):
                if not ax.lines:
                    return
                canvas._osc_viewer_active_line = ax.lines[-1]
                canvas._osc_viewer_active_index = len(ax.lines) - 1
            line = canvas._osc_viewer_active_line
            xdata = line.get_xdata()
            xlim = ax.get_xlim()
            delta_x = (xlim[1] - xlim[0]) * 0.01
            ydata = line.get_ydata()
            ylim = ax.get_ylim()
            delta_y = (ylim[1] - ylim[0]) * 0.01

            if event.key == " ":
                num_lines = len(ax.lines)
                if num_lines == 0:
                    return
                idx = getattr(canvas, "_osc_viewer_active_index", len(ax.lines) - 1)
                if idx is None:
                    idx = len(ax.lines) - 1
                idx = (idx + 1) % num_lines
                canvas._osc_viewer_active_line = ax.lines[idx]
                canvas._osc_viewer_active_index = idx
                for l in ax.lines:
                    l.set_zorder(1)
                    l.set_linewidth(1.0)
                    l.set_alpha(0.7)
                    l.selected = False
                ax.lines[idx].set_zorder(10)
                ax.lines[idx].set_linewidth(2.5)
                ax.lines[idx].set_alpha(1.0)
                ax.lines[idx].selected = True
                fig.canvas.draw_idle()
            elif event.key == "delete":
                num_lines = len(ax.lines)
                if num_lines == 0:
                    return
                idx = getattr(canvas, "_osc_viewer_active_index", len(ax.lines) - 1)
                if idx is None:
                    idx = len(ax.lines) - 1
                if idx < 0 or idx >= len(ax.lines):
                    return
                msg = QMessageBox(self.parent_widget)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Удалить график")
                msg.setText("Вы действительно хотите удалить выбранный график?")
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                ret = msg.exec()
                if ret == QMessageBox.StandardButton.Yes:
                    line_to_remove = ax.lines[idx]
                    if hasattr(canvas, "_osc_viewer_line_names"):
                        canvas._osc_viewer_line_names.pop(line_to_remove, None)
                    if hasattr(canvas, "_osc_viewer_scale_factors"):
                        canvas._osc_viewer_scale_factors.pop(line_to_remove, None)
                    line_to_remove.remove()
                    if ax.lines:
                        for l in ax.lines:
                            l.set_zorder(1)
                            l.set_linewidth(1.0)
                            l.set_alpha(0.7)
                            l.selected = False
                        new_idx = 0
                        canvas._osc_viewer_active_line = ax.lines[new_idx]
                        canvas._osc_viewer_active_index = new_idx
                        ax.lines[new_idx].set_zorder(10)
                        ax.lines[new_idx].set_linewidth(2.5)
                        ax.lines[new_idx].set_alpha(1.0)
                        ax.lines[new_idx].selected = True
                    else:
                        canvas._osc_viewer_active_line = None
                        canvas._osc_viewer_active_index = None
                    update_legend()
                    fig.canvas.draw_idle()

            # Проверяем, заблокировано ли перемещение линий
            if (
                hasattr(canvas, "_osc_viewer_move_locked")
                and canvas._osc_viewer_move_locked
            ):
                return
            if event.key in ["left"]:
                xdata = xdata - delta_x
                line.set_xdata(xdata)
                ax.relim()
                ax.autoscale_view()
                canvas.draw()
            elif event.key in ["right"]:
                xdata = xdata + delta_x
                line.set_xdata(xdata)
                ax.relim()
                ax.autoscale_view()
                canvas.draw()
            elif event.key in ["up"]:
                ydata = ydata + delta_y
                line.set_ydata(ydata)
                ax.relim()
                ax.autoscale_view()
                canvas.draw()
            elif event.key in ["down"]:
                ydata = ydata - delta_y
                line.set_ydata(ydata)
                ax.relim()
                ax.autoscale_view()
                canvas.draw()

        if hasattr(canvas, "_osc_viewer_key_cid"):
            canvas.mpl_disconnect(canvas._osc_viewer_key_cid)
        canvas._osc_viewer_key_cid = canvas.mpl_connect("key_press_event", on_key)

        # Сохраняем ссылку на последний добавленный график
        canvas._osc_viewer_active_line = ax.lines[-1]

        # Удаляем предыдущий обработчик, если он был
        if hasattr(canvas, "_osc_viewer_key_cid"):
            canvas.mpl_disconnect(canvas._osc_viewer_key_cid)
        canvas._osc_viewer_key_cid = canvas.mpl_connect("key_press_event", on_key)
        # Устанавливаем фокус на canvas для получения событий клавиатуры
        canvas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        canvas.setFocus()
        # настраиваем оси и сетку
        ax.set_xlabel("time, ms")
        ax.set_ylabel("U,V")
        ax.set_title("Осциллограмма сигнала")
        ax.grid(True)
        if len(x) > 0:
            ax.set_xlim(min(x), x[-1])
        canvas.draw()

        # Удаляем из легенды подпись удалённой линии при удалении линии
        def remove_line_from_legend(line):
            if hasattr(canvas, "_osc_viewer_line_names"):
                canvas._osc_viewer_line_names.pop(line, None)
            if hasattr(canvas, "_osc_viewer_scale_factors"):
                canvas._osc_viewer_scale_factors.pop(line, None)

        # Переопределяем обработчик удаления линии, чтобы убирать подпись из легенды
        orig_on_key = on_key

        def on_key_with_legend(event):
            if event.key == "delete":
                num_lines = len(ax.lines)
                if num_lines == 0:
                    return
                idx = getattr(canvas, "_osc_viewer_active_index", len(ax.lines) - 1)
                if idx is None:
                    idx = len(ax.lines) - 1
                if idx < 0 or idx >= len(ax.lines):
                    return
                msg = QMessageBox(self.parent_widget)
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Удалить график")
                msg.setText("Вы действительно хотите удалить выбранный график?")
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                ret = msg.exec()
                if ret == QMessageBox.StandardButton.Yes:
                    line_to_remove = ax.lines[idx]
                    remove_line_from_legend(line_to_remove)
                    line_to_remove.remove()
                    if ax.lines:
                        for l in ax.lines:
                            l.set_zorder(1)
                            l.set_linewidth(1.0)
                            l.set_alpha(0.7)
                        new_idx = 0
                        canvas._osc_viewer_active_line = ax.lines[new_idx]
                        canvas._osc_viewer_active_index = new_idx
                        ax.lines[new_idx].set_zorder(10)
                        ax.lines[new_idx].set_linewidth(2.5)
                        ax.lines[new_idx].set_alpha(1.0)
                    else:
                        canvas._osc_viewer_active_line = None
                        canvas._osc_viewer_active_index = None
                    update_legend()
                    fig.canvas.draw_idle()
            else:
                orig_on_key(event)

        # Переподключаем обработчик клавиш
        if hasattr(canvas, "_osc_viewer_key_cid"):
            canvas.mpl_disconnect(canvas._osc_viewer_key_cid)
        canvas._osc_viewer_key_cid = canvas.mpl_connect(
            "key_press_event", on_key_with_legend
        )
        # Добавляем обработчик колесика мыши для масштабирования по оси Y при зажатом Shift
        # Словарь для хранения коэффициентов масштабирования для каждой линии
        if not hasattr(canvas, "_osc_viewer_scale_factors"):
            canvas._osc_viewer_scale_factors = {}
        # Устанавливаем коэффициент масштабирования для новой линии
        line = getattr(canvas, "_osc_viewer_active_line", None)
        if line is None and ax.lines:
            line = ax.lines[-1]
            canvas._osc_viewer_active_line = line
            canvas._osc_viewer_active_index = len(ax.lines) - 1
        # Устанавливаем коэффициент масштабирования для новой линии
        if line not in canvas._osc_viewer_scale_factors:
            canvas._osc_viewer_scale_factors[line] = 1.0

        # Назначаем имя линии (например, "График 1", "График 2" и т.д.)
        if not hasattr(canvas, "_osc_viewer_line_names"):
            canvas._osc_viewer_line_names = {}
        if line not in canvas._osc_viewer_line_names:
            canvas._osc_viewer_line_names[line] = f"График {len(ax.lines)}"
        # Устанавливаем label для линии
        # Добавляем scale только если линия новая
        add_scale = add_scale_label if is_new_line else False
        line.set_label(
            format_line_label(
                canvas._osc_viewer_line_names[line],
                canvas._osc_viewer_scale_factors[line],
                add_scale,
            )
        )
        ax.legend(loc="best")

        def on_double_click(event):
            if event.dblclick and event.inaxes == ax:
                all_x = np.concatenate(
                    [line.get_xdata() for line in ax.lines if line.get_xdata().size > 0]
                )
                if all_x.size > 0:
                    ax.set_xlim(np.min(all_x), np.max(all_x))
                    canvas.draw_idle()

        if hasattr(canvas, "_osc_viewer_double_click_cid"):
            canvas.mpl_disconnect(canvas._osc_viewer_double_click_cid)
        canvas._osc_viewer_double_click_cid = canvas.mpl_connect(
            "button_press_event", on_double_click
        )

        def on_scroll(event):
            if event.inaxes != ax:
                return
            modifiers = QApplication.keyboardModifiers()
            if not (modifiers & Qt.KeyboardModifier.ShiftModifier):
                return
            # Получаем активную линию
            active_line = getattr(canvas, "_osc_viewer_active_line", None)
            if active_line is None or active_line not in ax.lines:
                return
            step = getattr(event, "step", None)
            if step is None:
                if hasattr(event, "button"):
                    step = 1 if event.button == "up" else -1
                elif hasattr(event, "delta"):
                    step = 1 if event.delta > 0 else -1
                else:
                    step = 1
            scale = 1.2 if step > 0 else 1 / 1.2
            ydata = active_line.get_ydata()
            ycenter = np.mean(ydata)
            ydata_scaled = (ydata - ycenter) * scale + ycenter
            active_line.set_ydata(ydata_scaled)
            # --- Обновляем scale-фактор ---
            canvas._osc_viewer_scale_factors[active_line] *= scale
            # --- Обновляем подпись линии ---
            name = canvas._osc_viewer_line_names.get(active_line, "График")
            new_scale = canvas._osc_viewer_scale_factors[active_line]
            active_line.set_label(f"{name} (x{new_scale:.2f})")
            ax.legend()
            canvas.draw()

        if hasattr(canvas, "_osc_viewer_scroll_cid"):
            canvas.mpl_disconnect(canvas._osc_viewer_scroll_cid)
        canvas._osc_viewer_scroll_cid = canvas.mpl_connect("scroll_event", on_scroll)

        # Обновляем легенду при переключении активной линии или удалении
        update_legend()

    def set_axes_params(
        self,
        xlim=None,
        ylim=None,
        grid=True,
        legend=True,
        title=None,
        xlabel=None,
        ylabel=None,
        grid_kwargs=None,
    ):
        """
        Устанавливает параметры области вывода графиков: пределы по осям, параметры сетки, названия и подписи.
        Args:
            xlim (tuple, optional): Пределы по оси X (min, max).
            ylim (tuple, optional): Пределы по оси Y (min, max).
            grid (bool, optional): Включить или выключить сетку. По умолчанию True.
            legend (bool, optional): Показывать легенду. По умолчанию True.
            grid_kwargs (dict, optional): Дополнительные параметры для сетки (например, {'linestyle': '--', 'color': 'gray'}).
            title (str, optional): Название графика.
            xlabel (str, optional): Подпись оси X.
            ylabel (str, optional): Подпись оси Y.
        """
        layout = self.parent_widget.layout()
        if layout is None:
            return
        canvas = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas is None:
            return
        ax = canvas.figure.gca()
        if xlim is not None:
            ax.set_xlim(*xlim)
        if ylim is not None:
            ax.set_ylim(*ylim)
        if title is not None:
            ax.set_title(title)
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if legend:
            ax.legend()
        if grid_kwargs is None:
            grid_kwargs = {}
        ax.grid(grid, **grid_kwargs)
        canvas.draw_idle()

    # Добавим методы для работы с линиями спектра через PlotData
    def get_all_lines(self):
        layout = self.parent_widget.layout()
        if layout is None:
            return []
        canvas = None
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas is None:
            return []
        ax = canvas.figure.gca()
        return list(ax.lines)

    @staticmethod
    def get_line_params(line):
        color = line.get_color()
        linestyle = line.get_linestyle()
        label = line.get_label()
        return {"color": color, "linestyle": linestyle, "label": label}


# from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# from PyQt6.QtWidgets import QWidget, QVBoxLayout

# class PlotData(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.figure = Figure(figsize=(5, 3))
#         self.canvas = FigureCanvas(self.figure)
#         self.ax = self.figure.add_subplot(111)
#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)
#         self.setLayout(layout)

#     def clear(self):
#         self.ax.clear()
#         self.canvas.draw()

#     def plot(self, x, y, label=None, **kwargs):
#         self.ax.plot(x, y, label=label, **kwargs)
#         if label:
#             self.ax.legend()
#         self.canvas.draw()

#     def set_title(self, title):
#         self.ax.set_title(title)
#         self.canvas.draw()

#     def set_xlabel(self, label):
#         self.ax.set_xlabel(label)
#         self.canvas.draw()

#     def set_ylabel(self, label):
#         self.ax.set_ylabel(label)
#         self.canvas.draw()

#     def set_xlim(self, left, right):
#         self.ax.set_xlim(left, right)
#         self.canvas.draw()

#     def set_grid(self, flag=True):
#         self.ax.grid(flag)
#         self.canvas.draw()

#     def get_lines(self):
#         return self.ax.lines
