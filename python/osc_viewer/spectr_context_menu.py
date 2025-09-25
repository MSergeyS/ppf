# -*- coding: utf-8 -*-
'''
spectr_context_menu.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-25
Версия:       1.0.0

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

def show_spectr_context_menu(main_window, pos):
    '''
    Отображает контекстное меню для вкладки "Спектр".
    Позволяет переключать масштаб оси Y между Вольтами и децибелами (дБ).
    Аргументы:
        pos (QPoint): Позиция вызова контекстного меню.
    '''
    def toggle_db():
        '''
        Переключает масштаб оси Y спектра между Вольтами и децибелами.
        Перерисовывает все линии спектра в выбранном масштабе.
        '''
        # Проверяем текущий режим
        if not hasattr(main_window, '_spectrum_db_mode'):
            main_window._spectrum_db_mode = False
        main_window._spectrum_db_mode = not main_window._spectrum_db_mode

        # Получаем все линии спектра
        lines = main_window.spectrum_data.get_all_lines()
        if not lines:
            main_window.show_message("Нет данных спектра для переключения масштаба")
            return

        ylim = {'min': 1_000, 'max': -1_000}
        for line in lines:
            spectrum = line.get_ydata()
            params = main_window.spectrum_data.get_line_params(line)
            if params is None:
                continue
            if main_window._spectrum_db_mode:
                # Переводим в дБ
                ydata = 20 * np.log10(np.abs(spectrum) + 1e-12)
                ylabel = 'Амплитуда, дБ'
                title = "Спектр сигнала (дБ)"
            else:
                # Переводим обратно в В
                ydata = np.power(10, spectrum / 20)
                ylabel = 'Амплитуда, В'
                title = "Спектр сигнала"
            if ylim['min'] > np.min(ydata):
                ylim['min'] = min(ylim['min'], np.min(ydata))
            if ylim['max'] < np.max(ydata):
                ylim['max'] = max(ylim['max'], np.max(ydata))
            # Меняем только значения y у линии
            line.set_ydata(ydata)
        main_window.spectrum_data.canvas.draw_idle()

        # Устанавливаем параметры осей
        main_window.spectrum_data.set_axes_params(
            xlim=(0, 4),
            ylim=(ylim['min'], ylim['max']),
            title=title,
            ylabel=ylabel,
            xlabel='Частота, МГц'
        )

    # Создаем контекстное меню для спектра
    menu = QMenu(main_window.spectrum_widget)
    # В зависимости от текущего режима задаем текст для переключения масштаба
    if (main_window._spectrum_db_mode):
        text_menu = "Переключить Y: дБ / В"
    else:
        text_menu = "Переключить Y: В / дБ"
    action1 = menu.addAction(text_menu)  # Добавляем действие для переключения масштаба Y
    action2 = menu.addAction("Сохранить как изображение")
    action3 = menu.addAction("Очистить график")
    action = menu.exec(main_window.spectrum_widget.mapToGlobal(pos))
    
    if action == action1:
        toggle_db()
    elif action == action2:
        main_window.show_message("Сохранение изображения (заглушка)")
        pixmap = main_window.spectrum_widget.grab()
        filename, _ = QFileDialog.getSaveFileName(main_window.spectrum_widget, "Сохранить изображение", "", "PNG Files (*.png)")
        if filename:
            pixmap.save(filename, "PNG")
            main_window.show_message(f"Изображение сохранено: {filename}")
    elif action == action3:
        # Очистка графика через PlotData
        main_window.spectrum_data.create_canvas()
        main_window.show_message("График очищен")