# -*- coding: utf-8 -*-
'''
load_and_prepare_data.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-25
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль для загрузки, предварительной обработки и подготовки данных сигналов из CSV-файлов для последующего анализа и визуализации. 
Содержит функции для чтения данных, извлечения и обработки метаинформации, а также для подготовки временных и сигнальных массивов с возможностью даунсемплинга и удаления постоянной составляющей.

Список функций:
---------------
- load_data(file_name: str, format_ver: int)
    Загружает данные и метаинформацию из CSV-файла в зависимости от версии формата.
- prepare_data(t, s, downsampling_factor=10)
    Выполняет даунсемплирование, удаление постоянной составляющей и дополнение массивов до нужной длины.
- open_csv_file(main_window)
    Открывает диалог выбора файла, загружает параметры отображения и данные, отображает сигнал на графике.
- print_c(text, color='white')
    Выводит текст в консоль с заданным цветом.
'''

import numpy as np
import pandas as pd

class MetaInfo:
    def __init__(self, info):
        self.info = info

def load_data(file_name, format_ver):
    '''
    Параметры:
        file_name (str): Путь к CSV-файлу с данными.
        format_ver (int): Версия формата файла. 
            0 — метаинформация и данные разделены пустыми строками.
            1 — первая строка содержит имена столбцов, вторая — значения метаинформации.
    Возвращает:
        t (list of float): Временной массив.
        s (list of float): Массив значений сигнала.
        meta_df (pandas.DataFrame): DataFrame с метаинформацией (ключ-значение).
    Особенности:
        - Автоматически вычисляет частоту дискретизации (fs), если возможно.
        - Корректирует временной массив с учетом смещения "Start" из метаинформации, если оно задано.
        - Выводит статус загрузки и информацию о сигнале в консоль.
    '''

    # Статус для отображения процесса загрузки
    print_c(f'Загрузка файла: {file_name}  Формат: {format_ver}', color='blue')

    meta = {}  # Словарь для хранения метаинформации
    t = []     # Список для времени
    s = []     # Список для значений сигнала
    k_t = 1.0  # Коэффициент масштабирования времени

    with open(file_name, "r", encoding="utf-8") as io:
        cnt_str = 0
        names = []
        cnt = 0
        for line in io:
            fields = line.strip().split(',')
            if format_ver == 0:
                # Формат 0: метаинформация и данные разделены пустыми строками
                if len(fields) >= 5 and (fields[0] != "" or fields[1] != "" or fields[2] != ""):
                    meta[fields[0]] = fields[1]
                elif len(fields) >= 5 and fields[0] == "" and fields[1] == "" and fields[2] == "":
                    t.append(float(fields[3]))
                    s.append(float(fields[4]))
            elif format_ver == 1:
                # Формат 1: первая строка — имена столбцов, вторая — значения метаинформации
                if cnt_str == 0:
                    names = fields
                    cnt_str += 1
                elif cnt_str == 1:
                    for i in range(len(names)-1):
                        meta[names[i]] = fields[i]
                        if names[i] == "Increment":
                            k_t = float(fields[i])
                    cnt_str += 1
                elif cnt_str > 1:
                    if (len(fields) < 2):
                        break
                    if fields[0].strip() != '' and fields[1].strip() != '':
                        t.append(float(fields[0]) * k_t)
                        s.append(float(fields[1]))

    # Вычисляем частоту дискретизации, если возможно
    if len(t) > 1:
        meta['fs'] = 1/(t[1]-t[0])
    else:
        meta['fs'] = 0.0  # Если данных недостаточно

    meta_info = MetaInfo(meta)
    # Преобразуем метаинформацию в DataFrame для удобства
    meta_df = pd.DataFrame({'Key': list(meta_info.info.keys()), 'Value': list(meta_info.info.values())})
    print_c(' ', color='white')
    print(meta_df)
    print_c('')

    # Корректируем временной массив, если задано смещение "Start"
    start_t = meta_df.loc[meta_df['Key'] == 'Start', 'Value'].values
    if len(start_t) > 0:
        start_t = float(start_t[0])
    else:
        start_t = 0.0
    t = np.array(t) + start_t
    t = t.tolist()

    print_c(f'Сигнал загружен. Количество точек: {len(s)}\n')
    
    return t, s, meta_df

def prepare_data(t, s, downsampling_factor=10):
    '''
    Подготавливает временные и сигнальные данные для дальнейшей обработки, включая даунсемплирование, удаление постоянной составляющей и дополнение до длины, кратной 2^16.
    Аргументы:
        t (list или np.ndarray): Массив временных отсчётов.
        s (list или np.ndarray): Массив значений сигнала.
        downsampling_factor (int, по умолчанию 10): Коэффициент даунсемплирования. Если больше 1, данные будут прорежены.
    Возвращает:
        tuple:
            t (list): Обновлённый массив времени, дополненный нулями до нужной длины.
            s (list): Обновлённый массив сигнала, с удалённой постоянной составляющей и дополненный нулями.
            oversampling_factor (float): Коэффициент увеличения длины сигнала для дополнения до 2^16 точек.
    Примечания:
        - Функция выводит в консоль информацию о частоте дискретизации до и после обработки, а также о длине сигнала.
        - После обработки длина массивов t и s становится равной ближайшему меньшему числу, кратному 2^16.
    '''

    print_c(f"\nПодготовка данных с даунсемплингом: {downsampling_factor}")
    print_c(f"Исходная частота дискретизации = {1/(t[1] - t[0])/1e6:.2f} МГц")

    # Даунсемплинг временного и сигнального массивов
    if downsampling_factor > 1:
        t = t[::downsampling_factor]
        s = s[::downsampling_factor]

    # Убираем среднее значение из сигнала (постоянную составляющую)
    s = np.array(s) - np.mean(s)
    s = s.tolist()

    N = len(s)
    oversampling_factor = 2**20 / N  # Коэффициент увеличения длины сигнала
    N_new = int(np.floor(oversampling_factor * N))

    # Дополняем сигнал и время нулями до 2^16 точек
    s = s + [0.0] * (N_new - N)
    t = t.tolist() + [0.0] * (N_new - N)

    print_c(f"Новая частота дискретизации = {1/(t[1] - t[0])/1e6:.2f} МГц")
    print_c(f"Подготовка проведена. Длина сигнала после подготовки = {len(s)}\n")

    return t, s, oversampling_factor

# --------------------------------------------------------------------------------------------


from PyQt6.QtWidgets import QFileDialog
import os
import json  # Для работы с JSON файлами

def open_csv_file(main_window):
    '''
    Открывает диалоговое окно для выбора CSV-файла, загружает параметры отображения из связанного JSON-файла (если он существует),
    сохраняет последнюю использованную директорию в ini-файл, загружает данные из выбранного CSV-файла и отображает их на графике.
    Основные действия функции:
    - Читает последнюю директорию из ini-файла (osc_viewer.ini) в формате JSON для использования в диалоге выбора файла.
    - Открывает диалоговое окно для выбора CSV-файла.
    - Сохраняет выбранную директорию обратно в ini-файл для последующего использования.
    - Устанавливает параметры отображения по умолчанию (версия формата, начальный и конечный индексы, коэффициент даунсемплинга).
    - Пытается загрузить параметры отображения из JSON-файла с тем же именем, что и выбранный CSV-файл.
    - Загружает данные из CSV-файла с помощью функции load_data.
    - Добавляет новую линию на график, используя данные из файла, и подписывает её именем файла.
    - Устанавливает параметры осей графика.
    - Обрабатывает возможные ошибки при загрузке файлов и построении графика, выводя сообщения пользователю.
    Аргументы:
        main_window: Главное окно приложения, содержащее методы для отображения сообщений, работы с графиком и хранения параметров отображения.
    Исключения:
        В случае ошибок при чтении файлов или построении графика, выводит сообщение об ошибке через main_window.show_message.
    '''

    ini_file = os.path.join(os.path.dirname(__file__), "osc_viewer.ini")

    # Читаем последнюю директорию из ini-файла (json-формат)
    last_dir = ""
    try:
        with open(ini_file, "r", encoding="utf-8") as f:
            ini_data = json.load(f)
            last_dir = ini_data.get("last_dir", "")
    except Exception:
        last_dir = ""

    # Открываем диалог выбора файла, используем последнюю директорию
    file_name, _ = QFileDialog.getOpenFileName(
        main_window, "Выберите CSV файл", last_dir, "CSV Files (*.csv);;All Files (*)"
    )

    # Сохраняем выбранную директорию в ini-файл
    if file_name:
        selected_dir = os.path.dirname(file_name)
        try:
            with open(ini_file, "w", encoding="utf-8") as f:
                json.dump({"last_dir": selected_dir}, f)
        except Exception:
            pass

    if file_name:
        # Устанавливаем параметры по умолчанию
        main_window.format_ver = 1  # версия формата CSV файла
        main_window.inx_start = 0  # начальный индекс для отображения
        main_window.inx_stop = None  # конечный индекс для отображения
        main_window.downsampling_factor = 1  # коэффициент даунсемплинга

        print_c(f'Выбран файл: {file_name}')

        # Формируем имя JSON-файла с параметрами
        json_file_name = file_name[:-3] + 'json'
        try:
            try:
                # Пробуем загрузить параметры из JSON-файла
                with open(json_file_name, 'r', encoding='utf-8') as f:
                    data_dict = json.load(f)
                    main_window.format_ver = data_dict['format_ver']
                    main_window.inx_start = data_dict['inx_start']
                    main_window.inx_stop = data_dict['inx_stop']
                    main_window.downsampling_factor = data_dict['downsampling_factor']
                print_c(
                    f'Параметры: {main_window.format_ver}, {main_window.inx_start}, {main_window.inx_stop}, {main_window.downsampling_factor}'
                )
            except FileNotFoundError:
                # Если JSON-файл не найден, используем параметры по умолчанию
                print_c('JSON-файл не найден, используются параметры по умолчанию из окна.')

            # Загружаем данные из CSV-файла
            t, s, meta_info = (
                load_data(
                    file_name,
                    main_window.format_ver
                )
            )

            # Получаем количество линий на графике
            num_lines = len(main_window.plot_data_signal.get_all_lines())
            # Инициализируем словарь для хранения имен файлов, если его нет
            if not hasattr(main_window.plot_data_signal, '_osc_viewer_file_names'):
                main_window.plot_data_signal._osc_viewer_file_names = {}
            # Сохраняем имя файла для текущей линии
            main_window.plot_data_signal._osc_viewer_file_names[num_lines] = file_name
            # Добавляем новую линию на график с подписью (именем файла)
            main_window.plot_data_signal.plot_line(
                t, s, x_zoom=1000, add_mode=True, label=file_name.split("/")[-1]
            )
            # Устанавливаем параметры осей графика
            main_window.plot_data_signal.set_axes_params(
                title="Осциллограмма сигнала",
                ylabel='Амплитуда, В',
                xlabel='Время, мс'
            )
            print_c('График построен', color='green')

        except Exception as e:
            # Обработка ошибок при загрузке и построении графика
            print_c(f"Ошибка: {e}", color='red')

def print_c(text, color='white'):
    print(f'<span style="color: {color};">{text}</span>')