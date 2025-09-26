# -*- coding: utf-8 -*-
'''
osc_context_menu.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.1

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
- create_spectrum(main_window)
    Создает спектр по активной линии графика сигнала.
- clip_data_x_axis(main_window)
    Обрезает данные всех линий графика по видимой области оси X.
- save_to_png(main_window)
    Сохраняет текущее изображение графика в PNG-файл.
'''

from PyQt6.QtWidgets import QMenu, QFileDialog

from create_spectrume import add_spectrume  # Функция для добавления спектра
from load_and_prepare_data import print_c   # Функция для печати сообщений в консоль приложения

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
    action4 = menu.addAction("Обрезать данные по видемой области")
    action = menu.exec(main_window.plot_widget.mapToGlobal(pos))
    if action == action1:
        print_c('Сохранение изображения графика\n')
        save_to_png(main_window)
    elif action == action2:
        # Очистка графика через PlotData
        main_window.plot_data_signal.create_canvas()
        print_c("График очищен\n")
    elif action == action3:
        print_c("Построить спектр\n")
        create_spectrum(main_window)
       
    elif action == action4:
        print_c("Обрезать данные по оси х\n")
        clip_data_x_axis(main_window)

def create_spectrum(main_window):
    '''
    Создает спектр по активной линии графика сигнала.
    '''
     # Получаем параметры активной линии
    params = main_window.plot_data_signal.get_active_line_params()
    if params is None:
        print_c("Нет активной линии для спектра\n")
        return
    # Получаем саму активную линию
    line = main_window.plot_data_signal.get_active_line()
    if line is None:
        print_c("Нет активной линии для спектра")
        return
    # Добавляем спектр по выбранной линии
    add_spectrume(main_window, line, params)
    # Проверяем наличие флага режима спектра
    if not hasattr(main_window, '_spectrum_db_mode'):
        main_window._spectrum_db_mode = False

def clip_data_x_axis(main_window):
    '''
    Обрезает данные всех линий графика по видимой области оси X.
    Используется для удаления данных вне текущего диапазона отображения.
    '''
    # Получаем текущие пределы по оси X с графика
    xlim = main_window.plot_data_signal.ax.get_xlim()
    # Обрезаем данные всех линий по этим пределам
    main_window.plot_data_signal.clip_data_x_axis(xlim[0], xlim[1])
    print_c(f"Данные обрезаны по X: {xlim[0]:.3f} ... {xlim[1]:.3f}\n")

def save_to_png(main_window):
    '''
    Сохраняет текущее изображение графика в PNG-файл.
    '''
    # Получаем изображение (скриншот) виджета графика
    pixmap = main_window.plot_widget.grab()
    # Открываем диалог для выбора имени файла и пути сохранения
    filename, _ = QFileDialog.getSaveFileName(
        main_window.plot_widget,
        'Сохранить изображение',
        '',
        'PNG Files (*.png)'
    )
    # Если пользователь выбрал файл, сохраняем изображение
    if filename:
        pixmap.save(filename, "PNG")
    # Сообщаем пользователю о результате сохранения
    print_c(f'Изображение сохранено: {filename}\n')