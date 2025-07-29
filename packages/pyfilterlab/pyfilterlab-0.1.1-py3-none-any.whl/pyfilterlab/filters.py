from scipy.signal import firwin, iirfilter, lfilter

def design_fir(num_taps, cutoff, fs, window='hamming'):
    return firwin(num_taps, cutoff, fs=fs, window=window)

def design_iir(order, cutoff, fs, ftype='butter'):
    b, a = iirfilter(order, cutoff, fs=fs, btype='low', ftype=ftype)
    return b, a

def apply_filter(b, a, signal):
    return lfilter(b, a, signal)
