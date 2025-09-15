import numpy as np
import pandas as pd

class MetaInfo:
    def __init__(self, info):
        self.info = info

def load_and_prepare_data(file_name, format_ver, inx_start, inx_stop, downsampling_factor):
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
                    # Проверяем, что поля не пустые
                    if (len(fields) < 2):
                        break
                    if fields[0].strip() != '' and fields[1].strip() != '':
                        t.append(float(fields[0]) * k_t)
                        s.append(float(fields[1]))
                    # # Проверяем, что поля не пустые
                    # if fields[0].strip() != '':
                    #     t.append(cnt * k_t)
                    #     s.append(float(fields[0]))
                    #     cnt += 1


    print(f"Считано {len(t)} отсчётов")
    print(f"Частота дискретизации = {round((1/k_t)/1e6)}  МГц")

    if downsampling_factor != 1:
        s = s[inx_start:inx_stop:downsampling_factor]
        t = np.array(t)[inx_start:inx_stop:downsampling_factor] - t[inx_start]
        t = t.tolist()
    else:
        t = t[inx_start:inx_stop]
        s = s[inx_start:inx_stop]
        t = np.array(t) - t[0]
        t = t.tolist()

    s = np.array(s) - np.mean(s)
    s = s.tolist()

    meta_info = MetaInfo(meta)
    meta_df = pd.DataFrame({'Key': list(meta_info.info.keys()), 'Value': list(meta_info.info.values())})
    print(meta_df)

    N = len(s)
    oversampling_factor = 2**16 / N
    N = len(t)
    N_new = int(np.floor(oversampling_factor * N))

    s = s + [0.0] * (N_new - N)
    dt = t[1] - t[0]
    # Пример получения значения из meta_df по ключу, например "Start"
    start_t = meta_df.loc[meta_df['Key'] == 'Start', 'Value'].values
    if len(start_t) > 0:
        start_t = float(start_t[0])
    else:
        start_t = 0.0
    t = [val + start_t for val in t + [t[-1] + dt * i for i in range(1, N_new - N + 1)]]
    
    print(f"Для анализа берём {len(t)} отсчётов")
    dt = t[1] - t[0]
    print(f"\nЧастота дискретизации (новая) = {round((1/dt)/1e6)}  МГц\n")

    return t, s, meta_info, meta_df, dt, oversampling_factor, N
