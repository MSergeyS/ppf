'''
test_main.py

Автор:        Мосолов С.С. (mosolov.s.s@yandex.ru)
Дата:         2025-09-26
Версия:       1.0.0

Лицензия:     MIT License
Контакты:     https://github.com/MSergeyS/ppf.git

Краткое описание:
-----------------
Модуль содержит набор unit-тестов для классов QtOutput и MainWindow из основного приложения.
Тесты проверяют корректность вывода текста, работу перенаправления stdout, отображение сообщений и обработку событий закрытия окна.
'''

import os
import sys
import pytest
from PyQt6.QtWidgets import QApplication, QTextEdit, QMainWindow

# Получаем абсолютный путь к директории osc_viewer (на уровень выше текущего файла).
osc_viewer_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if osc_viewer_dir not in sys.path:
    sys.path.insert(0, osc_viewer_dir)

from main import QtOutput, MainWindow

# Импортируем классы для тестирования

@pytest.fixture(scope="module")
def qapp():
    '''
    Фикстура pytest для создания экземпляра QApplication.
    Необходима для тестирования PyQt-приложений.
    '''
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

def test_qtoutput_write_plain_text(qapp):
    '''
    Проверяет, что QtOutput корректно записывает обычный текст в QTextEdit.
    '''
    textedit = QTextEdit()
    output = QtOutput(textedit)
    output.write("Hello, world!\n")
    # Проверяем, что текст появился в QTextEdit
    assert "Hello, world!" in textedit.toPlainText()

def test_qtoutput_write_html(qapp):
    '''
    Проверяет, что QtOutput корректно записывает HTML-текст в QTextEdit.
    '''
    textedit = QTextEdit()
    output = QtOutput(textedit)
    output.write('<span style="color:red">RedText</span>')
    # Проверяем, что HTML-текст корректно отображается
    assert "RedText" in textedit.toHtml()

def test_qtoutput_flush(qapp):
    '''
    Проверяет, что метод flush у QtOutput не вызывает ошибок.
    '''
    textedit = QTextEdit()
    output = QtOutput(textedit)
    # flush не должен выбрасывать исключения
    output.flush()

def test_mainwindow_show_message(qapp):
    '''
    Проверяет, что метод show_message отображает сообщение в статусном поле.
    '''
    window = MainWindow()
    window.show_message("Test message")
    # Проверяем, что сообщение появилось в статусном QTextEdit
    assert "Test message" in window.status_text.toPlainText()

def test_mainwindow_redirect_stdout_to_textedit(qapp):
    '''
    Проверяет, что перенаправление stdout в QTextEdit работает корректно.
    '''
    window = MainWindow()
    # Используем контекстный менеджер для перенаправления stdout
    with window.redirect_stdout_to_textedit():
        print("Redirected output")
    # Проверяем, что вывод появился в статусном QTextEdit
    assert "Redirected output" in window.status_text.toPlainText()
    def test_mainwindow_close_event(qapp, monkeypatch):
        '''
        Проверяет, что при закрытии окна вызывается родительский closeEvent.
        '''
        window = MainWindow()
        called = {}  # Словарь для фиксации вызова fake_close_event

        # Определяем поддельную функцию closeEvent, чтобы отследить вызов
        def fake_close_event(self, event):
            # Сохраняем параметры вызова для последующей проверки
            called['called'] = (self, event)

        # Подменяем метод closeEvent у QMainWindow на нашу поддельную функцию
        monkeypatch.setattr(QMainWindow, "closeEvent", fake_close_event)

        dummy_event = object()  # Создаем фиктивный объект события
        window.closeEvent(dummy_event)  # Вызываем closeEvent у тестируемого окна

        # Проверяем, что fake_close_event был вызван с правильными аргументами
        assert called['called'][0] is window  # Первый аргумент — это окно
        assert called['called'][1] is dummy_event  # Второй аргумент — это событие
