import struct
import numpy as np
import matplotlib.pyplot as plt

class ParametersMode:
    def __init__(self):
        self.sig1 = 0
        self.sig2 = 0
        self.version = 0
        self.rec_type = 0
        self.size_file = 0
        self.Code_ZI = 0
        self.Mode = 0
        self.Mode1 = 0
        self.TimeZ = 0
        self.NumPrd = 0
        self.TimeR = 0
        self.TimeI = 0
        self.CRC = 0
        self.Prm0 = 0
        self.Prm1 = 0
        self.Ver = 0
        self.Type = 0
        self.Name_RU = ""
        self.Name_EN = ""
        self.StartFreq = 0.0
        self.EndFreq = 0.0
        self.TimeZI = 0.0
        self.Fs = 0.0
        self.SampleType = 0
        self.Rzv2 = 0
        self.NumCC = 0
        self.Rzv3 = 0
        self.s = []
        self.t = []
        self.CC = []

def reader_dds(file_name, fclk):
    Tclk = 1 / fclk
    mode = ParametersMode()
    with open(file_name, "rb") as f:
        mode.sig1, = struct.unpack("<I", f.read(4))
        mode.sig2, = struct.unpack("<I", f.read(4))
        mode.version, = struct.unpack("<H", f.read(2))
        mode.rec_type, = struct.unpack("<H", f.read(2))
        mode.size_file, = struct.unpack("<I", f.read(4))
        mode.Code_ZI, = struct.unpack("<H", f.read(2))
        mode.Mode, = struct.unpack("<B", f.read(1))
        mode.Mode1, = struct.unpack("<B", f.read(1))
        mode.TimeZ, = struct.unpack("<H", f.read(2))
        mode.NumPrd, = struct.unpack("<I", f.read(4))
        mode.TimeR, = struct.unpack("<H", f.read(2))
        mode.TimeI, = struct.unpack("<H", f.read(2))
        mode.CRC, = struct.unpack("<H", f.read(2))
        mode.Prm0, = struct.unpack("<I", f.read(4))
        mode.Prm1, = struct.unpack("<I", f.read(4))
        mode.Ver, = struct.unpack("<B", f.read(1))
        mode.Type, = struct.unpack("<B", f.read(1))
        mode.Name_RU = f.read(40).decode("utf-16le", errors="ignore").rstrip('\x00')
        mode.Name_EN = f.read(40).decode("utf-16le", errors="ignore").rstrip('\x00')
        mode.StartFreq, = struct.unpack("<d", f.read(8))
        mode.EndFreq, = struct.unpack("<d", f.read(8))
        mode.TimeZI, = struct.unpack("<d", f.read(8))
        mode.Fs, = struct.unpack("<d", f.read(8))
        mode.SampleType, = struct.unpack("<B", f.read(1))
        mode.Rzv2, = struct.unpack("<B", f.read(1))
        mode.NumCC, = struct.unpack("<H", f.read(2))
        mode.Rzv3, = struct.unpack("<H", f.read(2))
        mode.CC = list(struct.unpack("<" + "H" * mode.NumCC, f.read(2 * mode.NumCC)))
        mode.s = cc2s_mode5(mode.CC)
        mode.t = np.arange(0, len(mode.s)) * Tclk
    return mode

def print_info(pm):
    print(f"sig1: 0x{pm.sig1:x}")
    print(f"sig2: 0x{pm.sig2:x}")
    print(f"version: 0x{pm.version:x}")
    print(f"rec_type: 0x{pm.rec_type:x}")
    print(f"size_file: {pm.size_file}")
    print(f"Code_ZI: {pm.Code_ZI}")
    print(f"Mode: {pm.Mode}")
    print(f"Mode1: {pm.Mode1}")
    print(f"TimeZ: {pm.TimeZ}")
    print(f"NumPrd: {pm.NumPrd}")
    print(f"TimeR: {pm.TimeR}")
    print(f"TimeI: {pm.TimeI}")
    print(f"CRC: {pm.CRC}")
    print(f"Prm0: {pm.Prm0}")
    print(f"Prm1: {pm.Prm1}")
    print(f"Ver: {pm.Ver}")
    print(f"Type: {pm.Type}")
    print(f"Name_RU: {pm.Name_RU}")
    print(f"Name_EN: {pm.Name_EN}")
    print(f"StartFreq: {pm.StartFreq}")
    print(f"EndFreq: {pm.EndFreq}")
    print(f"TimeZI: {pm.TimeZI}")
    print(f"Fs: {pm.Fs}")
    print(f"SampleType: {pm.SampleType}")
    print(f"Rzv2: {pm.Rzv2}")
    print(f"NumCC: {pm.NumCC}")
    print(f"Rzv3: {pm.Rzv3}")

def plot_signal(mode):
    plt.plot(1e6 * mode.t, mode.s)
    plt.xlabel("Время, мкс")
    plt.ylabel("Амплитуда")
    plt.title("Сигнал из DDS")
    plt.grid(True)
    plt.show()

def cc2s_mode5(CC):
    signal = []
    k = 0
    while k < len(CC):
        if CC[k] == 511:
            break
        bits = [int(b) for b in f"{CC[k]:016b}"]
        s = 0.0 if k % 2 == 0 else (1.0 if bits[7] == 0 else -1.0)
        if k % 2 != 0:
            bits[7] = 0
        bin_str = ''.join(str(b) for b in bits)
        T_val = int(bin_str, 2) + 2
        signal.extend([s] * T_val)
        k += 1
    signal.extend([0.0] * 1000)
    return np.array(signal)