# -*- coding: utf-8 -*-
'''
spectr_context_menu.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.1

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль реализует контекстное меню для вкладки "Спектр" в приложении визуализации сигналов.
Позволяет переключать масштаб оси Y между Вольтами и децибелами, сохранять изображение графика и очищать график спектра.

Список функций:
---------------
- show_spectr_context_menu(main_window, pos)
    Отображает контекстное меню для вкладки "Спектр" с возможностью переключения масштаба Y, сохранения изображения и очистки графика.
'''

import numpy as np

from PyQt6.QtWidgets import QMenu, QFileDialog

from load_and_prepare_data import print_c    # Функция для печати сообщений в консоль приложения


def show_spectr_context_menu(main_window, pos):
    '''
    Отображает контекстное меню для вкладки "Спектр".
    Позволяет переключать масштаб оси Y между Вольтами и децибелами (дБ).
    Аргументы:
        main_window: Главное окно приложения, содержащее виджет спектра и данные.
        pos (QPoint): Позиция вызова контекстного меню.
    '''

    def toggle_db():
        '''
        Переключает масштаб оси Y спектра между Вольтами и децибелами.
        Перерисовывает все линии спектра в выбранном масштабе.
        '''
        # Проверяем, определён ли режим отображения (дБ или В)
        if not hasattr(main_window, "_spectrum_db_mode"):
            main_window._spectrum_db_mode = False
        # Инвертируем режим отображения
        main_window._spectrum_db_mode = not main_window._spectrum_db_mode

        # Получаем все линии спектра для обновления данных
        lines = main_window.spectrum_data.get_all_lines()
        if not lines:
            print_c("Нет данных спектра для переключения масштаба")
            return

        # Инициализируем пределы по оси Y
        ylim = {"min": 1_000, "max": -1_000}
        for line in lines:
            spectrum = line.get_ydata()  # Получаем текущие значения Y
            params = main_window.spectrum_data.get_line_params(line)
            if params is None:
                continue
            if main_window._spectrum_db_mode:
                # Переводим значения в дБ (20*log10)
                ydata = 20 * np.log10(np.abs(spectrum) + 1e-12)
                ylabel = "Амплитуда, дБ"
                title = "Спектр сигнала (дБ)"
            else:
                # Переводим значения обратно в В (10^(x/20))
                ydata = np.power(10, spectrum / 20)
                ylabel = "Амплитуда, В"
                title = "Спектр сигнала"
            # Обновляем минимальные и максимальные значения для оси Y
            if ylim["min"] > np.min(ydata):
                ylim["min"] = min(ylim["min"], np.min(ydata))
            if ylim["max"] < np.max(ydata):
                ylim["max"] = max(ylim["max"], np.max(ydata))
            # Устанавливаем новые значения Y для линии
            line.set_ydata(ydata)
        # Перерисовываем холст
        main_window.spectrum_data.canvas.draw_idle()

        # Устанавливаем параметры осей (границы, подписи)
        main_window.spectrum_data.set_axes_params(
            xlim=(0, 4),
            ylim=(ylim["min"], ylim["max"]),
            title=title,
            ylabel=ylabel,
            xlabel="Частота, МГц",
        )

    def save_to_png():
        '''
        Сохраняет текущее изображение спектра в PNG-файл.
        '''
        print_c("Сохранение изображения (заглушка)")
        # Получаем изображение виджета спектра
        pixmap = main_window.spectrum_widget.grab()
        # Открываем диалог сохранения файла
        filename, _ = QFileDialog.getSaveFileName(
            main_window.spectrum_widget,
            "Сохранить изображение",
            "",
            "PNG Files (*.png)",
        )
        if filename:
            try:
                # Проверяем, что изображение получено корректно
                if pixmap and not pixmap.isNull():
                    pixmap.save(str(filename), "PNG")
                    print_c(f"Изображение сохранено: {filename}")
                else:
                    print_c("Ошибка: не удалось получить изображение для сохранения.")
            except Exception as e:
                print_c(f"Ошибка при сохранении изображения: {e}")

    def normalize():
        '''
        Нормализует спектр: максимальное значение становится 1 (В) или 0 (дБ).
        '''
        lines = main_window.spectrum_data.get_all_lines()
        if not lines:
            print_c("Нет данных спектра для нормализации")
            return

        for line in lines:
            ydata = line.get_ydata()
            if ydata is None or len(ydata) == 0:
                continue
            max_val = np.max(ydata)
            if max_val == 0:
                continue
            if main_window._spectrum_db_mode:
                # В дБ максимальный уровень должен быть 0 дБ (смещение)
                ydata_norm = ydata - max_val
                # scale_factor в разах (для обратного преобразования)
                scale_factor = 10 ** ((0-max_val) / 20) if max_val != 0 else 1.0
            else:
                # В В максимальный уровень должен быть 1 (деление)
                ydata_norm = ydata / max_val
                scale_factor = 1.0 / max_val if max_val != 0 else 1.0
            line.set_ydata(ydata_norm)
            # Сохраняем scale-фактор для линии (для сброса)
            if hasattr(main_window.spectrum_data.canvas, "_osc_viewer_scale_factors"):
                main_window.spectrum_data.canvas._osc_viewer_scale_factors[line] = scale_factor
        # Перерисовываем холст
        main_window.spectrum_data.canvas.draw_idle()
        # Устанавливаем пределы по оси Y в зависимости от режима
        if main_window._spectrum_db_mode:
            main_window.spectrum_data.set_axes_params(ylim=(-100, 0))
        else:
            main_window.spectrum_data.set_axes_params(ylim=(0, 1))
        print_c("Спектр нормализован")
        
    def reset():
        '''
        Сбрасывает нормализацию спектра, возвращая данные к исходному масштабу.
        '''
        lines = main_window.spectrum_data.get_all_lines()
        if not lines:
            print_c("Нет данных спектра для сброса")
            return

        for line in lines:
            ydata = line.get_ydata()
            if ydata is None or len(ydata) == 0:
                continue
            scale_factor = 1.0
            # Получаем сохранённый scale-фактор для линии
            if hasattr(main_window.spectrum_data.canvas, "_osc_viewer_scale_factors"):
                scale_factors = main_window.spectrum_data.canvas._osc_viewer_scale_factors
                if line in scale_factors:
                    scale_factor = scale_factors[line]
            # Приводим данные к исходному масштабу (scale factor = 1.0)
            if main_window._spectrum_db_mode:
                ydata_reset = ydata - 20 * np.log10(scale_factor)
            else:
                ydata_reset = np.array(ydata/scale_factor)
            line.set_ydata(ydata_reset)
            # Устанавливаем scale factor = 1.0 для линии
            if hasattr(main_window.spectrum_data.canvas, "_osc_viewer_scale_factors"):
                main_window.spectrum_data.canvas._osc_viewer_scale_factors[line] = 1.0
        # Перерисовываем холст
        main_window.spectrum_data.canvas.draw_idle()
        # Устанавливаем пределы по оси Y в зависимости от режима
        if main_window._spectrum_db_mode:
            ylim = (main_window.spectrum_data.get_y_min(), main_window.spectrum_data.get_y_max())
            main_window.spectrum_data.set_axes_params(ylim=ylim)
        else:
            ylim = (0, main_window.spectrum_data.get_y_max())
            main_window.spectrum_data.set_axes_params(ylim=ylim)
        print_c("Спектр сброшен к исходному уровню")

    # Создаем контекстное меню для спектра
    menu = QMenu(main_window.spectrum_widget)
    # Гарантируем, что _spectrum_db_mode определён
    if not hasattr(main_window, "_spectrum_db_mode"):
        main_window._spectrum_db_mode = False
    # В зависимости от текущего режима задаем текст для переключения масштаба
    if main_window._spectrum_db_mode:
        text_menu = "Переключить Y: дБ / В"
    else:
        text_menu = "Переключить Y: В / дБ"
    # Добавляем действия в меню
    action1 = menu.addAction(text_menu)  # Переключение масштаба Y
    action2 = menu.addAction("Нормализовать")  # Нормализация спектра
    action3 = menu.addAction("Сбросить к исходному уровню")  # Сброс нормализации
    action4 = menu.addAction("Сохранить как изображение")  # Сохранение изображения
    action5 = menu.addAction("Очистить график")  # Очистка графика
    # Отображаем меню и получаем выбранное действие
    action = menu.exec(main_window.spectrum_widget.mapToGlobal(pos))

    # Выполняем действие в зависимости от выбора пользователя
    if action == action1:
        toggle_db()
    elif action == action2:
        normalize()
    elif action == action3:
        reset()
    elif action == action4:
        save_to_png()
    elif action == action5:
        # Очистка графика через PlotData
        main_window.spectrum_data.create_canvas()
        print_c("График очищен")

