import numpy as np

def fft_signal(s: np.ndarray, t: np.ndarray):
    # спектр сигнала
    fft_s = np.fft.fft(s)

    # fftshift для симметричного спектра
    fft_s = np.fft.fftshift(fft_s)

    # длина сигнала
    nsamp = len(t)
    # вычисление амплитудного спектра
    amplitude_spectrum = np.abs(fft_s)
    # частота дискретизации
    fs = 1.0 / (t[1] - t[0])

    # частотный шаг
    df = fs / nsamp

    # нормировка амплитуды
    fft_s = fft_s / nsamp

    print(f"Частота дискретизации = {round(fs/1e6)}  МГц")
    print(f"Разрешение по частоте = {round(df)}  Гц")

    # вектор частот
    freq_vec = np.fft.fftshift(np.fft.fftfreq(nsamp, d=1/fs))

    return fft_s, nsamp, fs, df, freq_vec
