'''
test_load_and_prepare_data.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль содержит набор unit-тестов для функций модуля load_and_prepare_data, реализующих загрузку и предварительную обработку данных из CSV-файлов. 
Тесты проверяют корректность чтения данных различных форматов, обработку метаданных, а также работу функций downsampling и форматирования вывода.
'''

import os
import sys
import tempfile
import numpy as np
import pandas as pd
import pytest

# Получаем абсолютный путь к директории osc_viewer (на уровень выше текущего файла).
osc_viewer_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if osc_viewer_dir not in sys.path:
    sys.path.insert(0, osc_viewer_dir)

from load_and_prepare_data import load_data, prepare_data, print_c

# Фикстура для создания временного CSV-файла формата 0
@pytest.fixture
def csv_file_format0():
    # Содержимое файла: две строки метаданных и три строки данных
    content = (
        "Key1,Value1,,,,\n"
        "Key2,Value2,,,,\n"
        ",,,0.0,1.0\n"
        ",,,1.0,2.0\n"
        ",,,2.0,3.0\n"
    )
    # Создание временного файла
    with tempfile.NamedTemporaryFile(
        "w+", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        f.flush()
        yield f.name  # Возвращаем путь к файлу для теста
    os.remove(f.name)  # Удаляем файл после теста

# Фикстура для создания временного CSV-файла формата 1
@pytest.fixture
def csv_file_format1():
    # Содержимое файла: две строки метаданных и три строки данных
    content = "Increment,Start,Other\n" "0.5,1.0,abc\n" "0,10\n" "1,20\n" "2,30\n"
    with tempfile.NamedTemporaryFile(
        "w+", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        f.flush()
        yield f.name  # Возвращаем путь к файлу для теста
    os.remove(f.name)  # Удаляем файл после теста

# Тест загрузки данных формата 0
def test_load_data_format0(csv_file_format0):
    t, s, meta_df = load_data(csv_file_format0, 0)
    # Проверяем типы возвращаемых данных
    assert isinstance(t, list)
    assert isinstance(s, list)
    assert isinstance(meta_df, pd.DataFrame)
    # Проверяем корректность метаданных
    assert meta_df[meta_df["Key"] == "Key1"]["Value"].values[0] == "Value1"
    # Проверяем корректность данных
    assert np.allclose(t, [0.0, 1.0, 2.0])
    assert np.allclose(s, [1.0, 2.0, 3.0])

# Тест загрузки данных формата 1
def test_load_data_format1(csv_file_format1):
    t, s, meta_df = load_data(csv_file_format1, 1)
    # t должен быть [0*0.5+1.0, 1*0.5+1.0, 2*0.5+1.0] = [1.0, 1.5, 2.0]
    assert isinstance(t, list)
    assert isinstance(s, list)
    assert isinstance(meta_df, pd.DataFrame)
    assert np.allclose(t, [1.0, 1.5, 2.0])
    assert np.allclose(s, [10.0, 20.0, 30.0])
    # Проверяем метаданные
    assert float(meta_df[meta_df["Key"] == "Increment"]["Value"].values[0]) == 0.5
    assert float(meta_df[meta_df["Key"] == "Start"]["Value"].values[0]) == 1.0

# Тест downsampling в prepare_data
def test_prepare_data_downsampling():
    t = np.linspace(0, 1, 100)  # Временная ось
    s = np.sin(2 * np.pi * t)   # Сигнал
    t2, s2, oversampling_factor = prepare_data(t, s, downsampling_factor=10)
    # Проверяем длины массивов после downsampling
    assert len(t2) == len(s2)
    assert len(t2) >= len(t) // 10
    # Проверяем, что среднее значение сигнала близко к 0 (для синуса)
    assert np.isclose(np.mean(s2[: len(s2) - (len(t2) - len(s) // 10)]), 0, atol=1e-10)

# Тест prepare_data без downsampling
def test_prepare_data_no_downsampling():
    t = np.linspace(0, 1, 100)
    s = np.ones(100)
    t2, s2, oversampling_factor = prepare_data(t, s, downsampling_factor=1)
    # Проверяем длины массивов
    assert len(t2) == len(s2)
    # Проверяем, что среднее значение сигнала равно 0 (после обработки)
    assert np.allclose(np.mean(s2[:100]), 0)

# Тест функции цветного вывода print_c
def test_print_c(capsys):
    print_c("test", color="red")
    captured = capsys.readouterr()
    # Проверяем, что вывод содержит HTML-строку с нужным цветом
    assert '<span style="color: red;">test</span>' in captured.out
