#!/bin/bash

# Путь к директории с тестами
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

TEST_DIR="$SCRIPT_DIR/../tests"
cd $TEST_DIR
echo "Текущая директория: $(pwd)"

# Проверяем, что директория с тестами существует
if [ ! -d "$TEST_DIR" ]; then
    echo "Директория с тестами не найдена: $TEST_DIR"
    exit 1
fi

# Запускаем pytest для всех тестов в директории
for test_file in test_*.py; do
    pytest -v "$test_file"
    if [ $? -ne 0 ]; then
        echo "Ошибка в тесте: $test_file"
    fi
done
RESULT=$?

if [ $RESULT -eq 0 ]; then
    printf "\033[32m%s\033[0m\n" "Тесты прошли успешно."
else
    printf "\033[31m%s\033[0m\n" "Тесты завершились с ошибками."
fi

exit $RESULT
