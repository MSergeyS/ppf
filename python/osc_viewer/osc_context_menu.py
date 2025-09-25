# -*- coding: utf-8 -*-
'''
osc_context_menu.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-25
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль реализует контекстное меню для графика сигнала в приложении визуализации сигналов. 
Позволяет сохранять изображение графика, очищать график и строить спектр выбранной линии.

Список функций:
---------------
- show_plot_context_menu(main_window, pos)
    Отображает контекстное меню для графика сигнала с возможностью сохранить изображение, очистить график или построить спектр выбранной линии.
'''

from PyQt6.QtWidgets import QMenu, QFileDialog

from create_spectrume import add_spectrume        # Функция для добавления спектра

def show_plot_context_menu(main_window, pos):
    '''
    Отображает контекстное меню для графика сигнала.
    Позволяет:
        - Сохранить изображение графика (заглушка).
        - Очистить график.
        - Построить спектр по выбранной линии.
    Аргументы:
        pos (QPoint): Позиция вызова контекстного меню.
    '''
    menu = QMenu(main_window.plot_widget)
    action1 = menu.addAction("Сохранить как изображение")
    action2 = menu.addAction("Очистить график")
    action3 = menu.addAction("Построить спектр")
    action = menu.exec(main_window.plot_widget.mapToGlobal(pos))
    if action == action1:
        main_window.show_message("Сохранение изображения (заглушка)")
        pixmap = main_window.plot_widget.grab()
        filename, _ = QFileDialog.getSaveFileName(main_window.plot_widget, "Сохранить изображение", "", "PNG Files (*.png)")
        if filename:
            pixmap.save(filename, "PNG")
            main_window.show_message(f"Изображение сохранено: {filename}\n")
    elif action == action2:
        # Очистка графика через PlotData
        main_window.plot_data_signal.create_canvas()
        main_window.show_message("График очищен\n")
    elif action == action3:
        main_window.show_message("Построить спектр\n")
        # Получаем параметры активной линии
        params = main_window.plot_data_signal.get_active_line_params()
        if params is None:
            main_window.show_message("Нет активной линии для спектра\n")
            return
        # Получаем саму активную линию
        line = main_window.plot_data_signal.get_active_line()
        if line is None:
            main_window.show_message("Нет активной линии для спектра")
            return
        # Добавляем спектр по выбранной линии
        add_spectrume(main_window, line, params)
        # Проверяем наличие флага режима спектра
        if not hasattr(main_window, '_spectrum_db_mode'):
            main_window._spectrum_db_mode = False