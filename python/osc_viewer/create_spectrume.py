# -*- coding: utf-8 -*-
'''
create_spectrume.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-25
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль для вычисления и отображения спектра сигнала с помощью БПФ (быстрого преобразования Фурье) в составе приложения визуализации сигналов. 
Содержит функции для вычисления спектра, отображения его в различных режимах (В/дБ), управления построением и отображением спектров на графиках.

Список функций:
---------------
- fft_signal(s: np.ndarray, t: np.ndarray)
- create_spectrume(main_window, line=None)
    Проверяет, был ли уже построен спектр для данной линии, и если нет — вычисляет спектр и возвращает массивы частот и амплитуд.
- set_spectrum_db_mode(main_window, db_mode: bool)
    Устанавливает режим отображения спектра: в децибелах (дБ) или в вольтах (В), и перерисовывает активный спектр.
- add_spectrume(main_window, line, params)
    Создает и отображает спектр выбранной линии на отдельной вкладке, с учетом выбранного режима отображения (дБ/В).
'''

'''
Модуль для вычисления и отображения спектра сигнала с помощью БПФ, а также для управления контекстными меню графиков и спектров.
Содержит функции и методы:
- fft_signal(s: np.ndarray, t: np.ndarray): Вычисляет спектр сигнала, параметры спектра и вектор частот по временным отсчетам и значениям сигнала.
- show_plot_context_menu(self, pos): Отображает контекстное меню для графика сигнала, позволяя сохранить изображение, очистить график или построить спектр по выбранной линии.
- show_spectr_context_menu(self, pos): Отображает контекстное меню для вкладки "Спектр", позволяя переключать масштаб оси Y между Вольтами и децибелами (дБ).
Комментарии:
- Все функции снабжены подробными комментариями на русском языке, поясняющими назначение аргументов, возвращаемых значений и этапов вычислений.
- В функции fft_signal приведены пояснения к каждому этапу обработки сигнала: вычисление БПФ, нормировка, вычисление параметров спектра и формирование вектора частот.
- Методы show_plot_context_menu и show_spectr_context_menu содержат комментарии к каждому действию контекстного меню и этапам обработки пользовательских команд.
'''

# Импортируем необходимые библиотеки и функции
import numpy as np

# Импорт функции для подготовки данных (например, интерполяция, фильтрация)
from load_and_prepare_data import prepare_data  # Функция для подготовки данных

def fft_signal(s: np.ndarray, t: np.ndarray):
    '''
    Вычисляет спектр сигнала с помощью БПФ и возвращает спектр, параметры и вектор частот.

    Аргументы:
        s (np.ndarray): Массив значений сигнала.
        t (np.ndarray): Массив временных отсчетов.

    Возвращает:
        fft_s (np.ndarray): Спектр сигнала после fftshift и нормировки.
        nsamp (int): Количество отсчетов (длина сигнала).
        fs (float): Частота дискретизации.
        df (float): Частотное разрешение.
        freq_vec (np.ndarray): Вектор частот (ось X для спектра).
    '''
    # Вычисляем БПФ сигнала
    fft_s = np.fft.fft(s)

    # Сдвигаем спектр так, чтобы нулевая частота была по центру
    fft_s = np.fft.fftshift(fft_s)

    # Определяем длину сигнала
    nsamp = len(t)

    # Вычисляем частоту дискретизации
    fs = 1.0 / (t[1] - t[0])

    # Вычисляем частотный шаг (разрешение по частоте)
    df = fs / nsamp

    # Нормируем амплитуду спектра
    fft_s = fft_s / nsamp

    # Выводим параметры спектра для отладки
    print(f"Частота дискретизации = {round(fs/1e6)}  МГц")
    print(f"Разрешение по частоте = {round(df)}  Гц")

    # Формируем вектор частот для оси X
    freq_vec = np.linspace(-fs/2, fs/2, nsamp)

    return fft_s, nsamp, fs, df, freq_vec

def create_spectrume(main_window, line=None):
    '''
    Функция проверяет, был ли уже построен спектр для данной линии (по флагу has_spectrum).
    Если спектр еще не построен, вычисляет спектр с помощью БПФ (FFT) и возвращает массивы частот и амплитуд.
    В случае ошибок или если спектр уже построен, выводит соответствующее сообщение и возвращает None.
    Параметры:
        line (object, optional): Объект линии, для которой строится спектр. 
                                 Должен иметь методы get_xdata(), get_ydata() и атрибут has_spectrum.
                                 Если не указан, используется активная линия.
    Возвращает:
        tuple: (spectrum_x, spectrum_y) — массивы частот и амплитуд спектра.
        None: В случае ошибки или если спектр уже построен.
    Комментарии:
        - Использует функцию prepare_data для предобработки данных сигнала.
        - Использует функцию fft_signal для вычисления спектра.
        - Выводит параметры сигнала и спектра в текстовый редактор через redirect_stdout_to_textedit().
        - Работает только с линиями, у которых не установлен флаг has_spectrum.
        - Для корректной работы требуется, чтобы line имел методы get_xdata(), get_ydata() и атрибут has_spectrum.
    '''
    # Проверяем, передана ли линия для построения спектра
    if line is None:
        main_window.show_message("Нет выбранной линии для построения спектра")
        return None

    # Проверяем, установлен ли атрибут has_spectrum и не построен ли уже спектр
    if not (hasattr(line, 'has_spectrum')) or (line.has_spectrum == False):
        # Получаем данные сигнала (время и значения)
        t = line.get_xdata()
        s = line.get_ydata()
        # Предобрабатываем данные (например, интерполяция, фильтрация)
        t, s, _ = prepare_data(t/1000, s)  # oversampling_factor не используется
        # Выводим параметры сигнала в текстовый редактор
        with main_window.redirect_stdout_to_textedit():
            print(f"Длина сигнала = {len(s)}")
            print(f"Длительность сигнала = {(t[-1]-t[0])*1000:.2f} мс")
            print(f"Частота дискретизации = {1/(t[1]-t[0])/1e6:.2f} МГц")
        # Вычисляем спектр сигнала с помощью БПФ
        spectrum_y, _, _, _, spectrum_x = fft_signal(np.array(s), np.array(t))  # nsamp, fs, df не используются
        # Повторно выводим частоту дискретизации
        with main_window.redirect_stdout_to_textedit():
            print(f"Частота дискретизации = {(1/(t[1]-t[0]))/1e6:.2f} МГц")
        # Определяем минимальную длину массивов спектра
        min_len = min(len(spectrum_x), len(spectrum_y))
        # Находим индекс первого значения spectrum_x >= 0 (только положительные частоты)
        idx0 = np.argmax(spectrum_x >= 0)
        # Обрезаем массивы спектра до положительных частот
        spectrum_x = spectrum_x[idx0:min_len]
        spectrum_y = spectrum_y[idx0:min_len]
    else:
        # Если у линии нет атрибута has_spectrum или спектр уже построен — выводим сообщение
        if not hasattr(line, 'has_spectrum'):
            main_window.show_message("У выбранной линии не установлен флаг has_spectrum — невозможно построить спектр.")
        elif line.has_spectrum:
            main_window.show_message("Для выбранной линии спектр уже построен.")
        main_window.show_message("Для выбранной линии спектр уже построен или не установлен флаг has_spectrum")
        return None

    # Возвращаем массивы частот и амплитуд спектра
    return spectrum_x, spectrum_y

def set_spectrum_db_mode(main_window, db_mode: bool):
    '''
    Устанавливает режим отображения спектра: в децибелах (дБ) или в вольтах (В).
    Если выбран режим дБ (db_mode=True), амплитуда спектра преобразуется в децибелы и отображается соответствующим образом.
    Если выбран режим В (db_mode=False), амплитуда спектра отображается в вольтах.
    После смены режима функция перерисовывает активный спектр с учетом выбранного режима и обновляет параметры осей графика.
    Параметры:
        db_mode (bool): 
            True — отображать спектр в децибелах (дБ).
            False — отображать спектр в вольтах (В).
    Примечания:
        - Если нет активной линии спектра или её параметров, функция ничего не делает.
        - Для предотвращения ошибок при логарифмировании к амплитуде добавляется малое значение (1e-12).
    '''
    main_window._spectrum_db_mode = db_mode  # Сохраняем выбранный режим

    # Получаем активную линию спектра и её параметры
    line = main_window.spectrum_data.get_active_line()
    params = main_window.spectrum_data.get_active_line_params()
    if line is None or params is None:
        # Если нет активной линии или параметров — ничего не делаем
        return

    # Получаем данные спектра (частоты и амплитуды)
    freq = line.get_xdata()
    spectrum = line.get_ydata()

    # Очищаем холст перед перерисовкой
    main_window.spectrum_data.clear_canvas()

    if main_window._spectrum_db_mode:
        # Переводим амплитуду в дБ
        spectrum_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
        # Строим спектр в дБ
        main_window.spectrum_data.plot_line(
            freq, spectrum_db,
            add_mode=True,
            color=params['color'],
            linestyle=params['linestyle'],
            label=params['label'] + " (дБ)"
        )
        # Устанавливаем параметры осей для режима дБ
        main_window.spectrum_data.set_axes_params(
            xlim=(0, 4),
            title="Спектр сигнала (дБ)",
            ylabel='Амплитуда, дБ',
            xlabel='Частота, МГц'
        )
    else:
        # Переводим амплитуду из дБ обратно в Вольты (если исходный спектр был в дБ)
        spectrum_v = np.power(10, spectrum / 20)
        # Строим спектр в Вольтах
        main_window.spectrum_data.plot_line(
            freq, spectrum_v,
            add_mode=True,
            color=params['color'],
            linestyle=params['linestyle'],
            label=params['label']
        )
        # Устанавливаем параметры осей для режима В
        main_window.spectrum_data.set_axes_params(
            xlim=(0, 4),
            title="Спектр сигнала",
            ylabel='Амплитуда, В',
            xlabel='Частота, МГц'
        )

def add_spectrume(main_window, line, params):
    '''
    Создает и отображает спектр выбранной линии на основном графике.
    Если линия не указана, используется активная линия. Спектр строится на отдельной вкладке
    и отображается в выбранном режиме (амплитуда в дБ или в В). После построения спектра
    блокируется возможность перемещения линий на графике спектра, а также происходит
    автоматическое переключение на вкладку со спектром и выводится сообщение об успешном построении.
    Аргументы:
        line: Объект линии, для которой строится спектр. Если None, используется активная линия.
        params (dict): Словарь параметров отображения спектра (цвет, стиль линии, подпись и др.).
    Возвращает:
        None
    '''
    def get_amplitude_and_ylabel(main_window, spectrum):
        # Определяем режим отображения спектра: дБ или В
        if hasattr(main_window, '_spectrum_db_mode') and main_window._spectrum_db_mode:
            # Если выбран режим дБ, переводим амплитуду в децибелы
            spectrum_db = 20 * np.log10(np.abs(spectrum) + 1e-12)
            return spectrum_db, 'Амплитуда, дБ'
        else:
            # В противном случае отображаем амплитуду в вольтах
            return abs(spectrum), 'Амплитуда, В'
                
    # Строим спектр по активной линии
    freq, spectrum = create_spectrume(main_window, line)
    
    if freq is None or spectrum is None:
        # Если не удалось построить спектр — выходим
        return

    # Получаем амплитуду и подпись оси Y в зависимости от режима отображения
    spectrum, ylabel = get_amplitude_and_ylabel(main_window, spectrum)

    # Строим спектр на отдельном холсте (в МГц)
    main_window.spectrum_data.plot_line(
        freq/1e6, spectrum,
        add_mode=True,
        color=params['color'],
        linestyle=params['linestyle'],
        label=params['label']
    )

    # Устанавливаем параметры осей для спектра
    main_window.spectrum_data.set_axes_params(
        xlim=(0, 4),
        title="Спектр сигнала",
        ylabel=ylabel,
        xlabel='Частота, МГц'
    )

    # Блокируем изменение положения линий после построения (для спектра)
    layout = main_window.spectrum_widget.layout()
    if layout is not None:
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            widget._osc_viewer_move_locked = True

    # Переключаемся на вкладку со спектром
    main_window.tabs.setCurrentWidget(main_window.spectrum_widget)

    # Показываем сообщение об успешном построении графика
    main_window.show_message("График построен")
    
