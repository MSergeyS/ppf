import numpy as np
import pandas as pd

class MetaInfo:
    def __init__(self, info):
        self.info = info
        
def load_data(file_name, format_ver):
    # Вместо print используем возврат строки для отображения в TextBox
    status_message = f"\nЗагрузка файла: {file_name}  Формат: {format_ver}"
    # Для передачи цвета можно вернуть кортеж (строка, цвет)
    # Например: return status_message, "green"
    # Или если TextBox поддерживает HTML/Markdown:
    # status_message = f"<span style='color:green'>{status_message}</span>"
    print(status_message)

    meta = {}
    t = []
    s = []
    k_t = 1.0

    with open(file_name, "r", encoding="utf-8") as io:
        cnt_str = 0
        names = []
        cnt = 0
        for line in io:
            fields = line.strip().split(',')
            if format_ver == 0:
                if len(fields) >= 5 and (fields[0] != "" or fields[1] != "" or fields[2] != ""):
                    meta[fields[0]] = fields[1]
                elif len(fields) >= 5 and fields[0] == "" and fields[1] == "" and fields[2] == "":
                    t.append(float(fields[3]))
                    s.append(float(fields[4]))
            elif format_ver == 1:
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

    if len(t) > 1:
        meta['fs'] = 1/(t[1]-t[0])
    else:
        meta['fs'] = 0.0  # or handle as appropriate

    meta_info = MetaInfo(meta)
    meta_df = pd.DataFrame({'Key': list(meta_info.info.keys()), 'Value': list(meta_info.info.values())})
    print()
    print(meta_df)

    start_t = meta_df.loc[meta_df['Key'] == 'Start', 'Value'].values
    if len(start_t) > 0:
        start_t = float(start_t[0])
    else:
        start_t = 0.0
    t = np.array(t) + start_t
    t = t.tolist()

    print(f'Сигнал загружен. Количество точек: {len(s)}\n')
    
    return t, s, meta_df

def prepare_data(t, s, downsampling_factor=10):
    print(f"\nПодготовка данных с даунсемплингом: {downsampling_factor}")
    print(f"Исходная частота дискретизации = {1/(t[1] - t[0])/1e6:.2f} МГц")

    if downsampling_factor > 1:
        t = t[::downsampling_factor]
        s = s[::downsampling_factor]

    # Убираем среднее значение из сигнала (постоянную составляющую)
    s = np.array(s) - np.mean(s)
    s = s.tolist()

    N = len(s)
    oversampling_factor = 2**16 / N
    N_new = int(np.floor(oversampling_factor * N))

    # увеличиваем количество точек для разрешения по частоте до 2^16 точек (если нужно)
    s = s + [0.0] * (N_new - N)
    t = t.tolist() + [0.0] * (N_new - N)

    print(f"Новая частота дискретизации = {1/(t[1] - t[0])/1e6:.2f} МГц")
    print(f"Подготовка проведена. Длина сигнала после подготовки = {len(s)}\n")

    return t, s, oversampling_factor

