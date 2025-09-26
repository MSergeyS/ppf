#!/bin/bash

# Скрипт для обновления даты и версии в заголовке *.py файлов, если есть изменения для коммита

# Получаем текущую дату в формате YYYY-MM-DD
current_date=$(date +%Y-%m-%d)

# Переходим в корень проекта (директория выше scripts)
cd "$(dirname "$0")/.."
source_path=$(pwd)
# echo "Текущая директория: $(pwd)"

# Собираем информацию о датах и версиях всех *.py файлов
output_file="versions_source_files.txt"
# Заголовок таблицы
printf "%-54s %-19s %-10s\n" "Файл" "Дата" "Версия" > "$output_file"

find . -name "*.py" -not -path "*/__pycache__/*" | while read -r pyfile; do
	# Извлекаем дату
	file_date=$(grep -m1 -E "^ *Дата: *[0-9]{4}-[0-9]{2}-[0-9]{2}" "$pyfile" | sed -E 's/^ *Дата: *([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/')
	# Извлекаем версию
	file_version=$(grep -m1 -E "^ *Версия: *[0-9]+\.[0-9]+\.[0-9]+" "$pyfile" | sed -E 's/^ *Версия: *([0-9]+\.[0-9]+\.[0-9]+).*/\1/')
	# Если не найдено — ставим прочерк
	[ -z "$file_date" ] && file_date="-"
	[ -z "$file_version" ] && file_version="-"
	# Добавляем в таблицу (строки выравниваются по левому краю с заданной шириной)
	printf "%-50s %-15s %-10s\n" "$pyfile" "$file_date" "$file_version" >> "$output_file"
done

echo -e "\033[32mТаблица версий и дат сохранена в $output_file\033[0m"