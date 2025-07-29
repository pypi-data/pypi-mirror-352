import matplotlib.pyplot as plt
from scipy.signal import freqz
import numpy as np

def plot_response(b, a=1, fs=1.0, title='Frequency Response'):
    w, h = freqz(b, a, fs=fs)
    plt.figure()
    plt.plot(w, 20 * np.log10(abs(h)), 'b')
    plt.title(title)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain (dB)')
    plt.grid()
    plt.show()

def plot_signal(signal, fs=1.0, title='Signal'):
    t = np.arange(len(signal)) / fs
    plt.figure()
    plt.plot(t, signal)
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.show()
