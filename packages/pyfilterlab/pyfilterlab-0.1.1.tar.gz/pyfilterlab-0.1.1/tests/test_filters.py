import numpy as np
from pyfilterlab import design_fir, apply_filter

def test_fir_lowpass():
    signal = np.ones(100)
    fir = design_fir(21, cutoff=0.2, fs=1.0)
    filtered = apply_filter(fir, 1, signal)
    assert len(filtered) == 100
