import numpy as np
from scipy.signal import find_peaks

import matplotlib.pyplot as plt

def plot_peaks_periodogram(p_test, fvec,  freq_limit=100_000, height=-120, prominence=2, width=1):
    # Calculate spectrum in dB
    spectrum = 10 * np.log10(np.abs(p_test))
# Adjust 'd' as needed for your sampling rate

    # Limit frequencies
    inx_limit = np.where(fvec < freq_limit)[0]
    spectrum_limited = spectrum[inx_limit]
    fvec_limited = fvec[inx_limit]

    # Find peaks
    peaks, properties = find_peaks(spectrum_limited, height=height, prominence=prominence, width=width)

    print("Индексы пиков:", peaks)
    print("Частоты пиков:", fvec_limited[peaks] / 1e3, "кГц")
    print("Амплитуды пиков:", spectrum_limited[peaks], "дБ")

    max_y = np.max(spectrum_limited)

    plt.plot(fvec / 1e3, spectrum, label="Спектр сигнала (fft)")
    plt.scatter(fvec_limited[peaks] / 1e3, spectrum_limited[peaks], color='red', label="Пики")
    plt.xlabel("f, kHz")
    plt.ylabel("U, dB")
    plt.title("Спектр сигнала (fft)")
    plt.xlim(0, freq_limit / 1e3)
    plt.ylim(max_y - 60, max_y)
    plt.grid(True)
    plt.legend()
    plt.show()