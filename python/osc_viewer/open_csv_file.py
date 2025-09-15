from PyQt6.QtWidgets import QFileDialog
import os
import json  # Для работы с JSON файлами

from load_and_prepare_data import load_and_prepare_data  # загрузка и подготовка данных
from plot_to_qt import plot_signal_to_qt  # построение графика в PyQt


def open_csv_file(main_window):
    """
    Открывает диалог выбора CSV-файла, читает параметры из JSON,
    вызывает обработку данных и отображение графика.
    Если JSON-файл не найден, используются значения из main_window.
    Если график уже есть, новый строится поверх существующего.
    """
    ini_file = os.path.join(os.path.dirname(__file__), "osc_viewer.ini")

    # Читаем последнюю директорию из ini-файла (json-формат)
    last_dir = ""
    try:
        with open(ini_file, "r", encoding="utf-8") as f:
            ini_data = json.load(f)
            last_dir = ini_data.get("last_dir", "")
    except Exception:
        last_dir = ""

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
        main_window.format_ver = 1  # версия формата CSV файла
        main_window.inx_start = 0  # начальный индекс для отображения
        main_window.inx_stop = None  # конечный индекс для отображения
        main_window.downsampling_factor = 1  # коэффициент даунсемплинга
        main_window.show_message(f"Выбран файл: {file_name}")
        json_file_name = file_name[:-3] + "json"
        try:
            try:
                with open(json_file_name, "r", encoding="utf-8") as f:
                    data_dict = json.load(f)
                    main_window.format_ver = data_dict["format_ver"]
                    main_window.inx_start = data_dict["inx_start"]
                    main_window.inx_stop = data_dict["inx_stop"]
                    main_window.downsampling_factor = data_dict["downsampling_factor"]
                main_window.show_message(
                    f"Параметры: {main_window.format_ver}, {main_window.inx_start}, {main_window.inx_stop}, {main_window.downsampling_factor}"
                )
            except FileNotFoundError:
                main_window.show_message(
                    "JSON-файл не найден, используются параметры по умолчанию из окна."
                )
            t, s, meta_info, meta_df, dt, oversampling_factor, N = (
                load_and_prepare_data(
                    file_name,
                    main_window.format_ver,
                    main_window.inx_start,
                    main_window.inx_stop,
                    main_window.downsampling_factor,
                )
            )
            # Передаём флаг add_mode=True, чтобы не очищать область (реализуйте поддержку этого флага в plot_signal_to_qt)
            plot_signal_to_qt(main_window.plot_widget, t, s, add_mode=True)
        except Exception as e:
            main_window.show_message(f"Ошибка: {e}")
