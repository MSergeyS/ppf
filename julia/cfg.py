c = get_config()

import os
c.TemplateExporter.template_path = ['.', os.path.expanduser('~/.jupyter/templates/')]


# Полезный блок, который дает возможность не выводить ячейки с тегом Skip

# если некоторые блоки выполняют только служебную функцию

c.TagRemovePreprocessor.enabled=True

c.TagRemovePreprocessor.remove_cell_tags=("Skip",)

# Указывает основной файл шаблона

# c.Exporter.template_file = 'style_notebook.tplx'