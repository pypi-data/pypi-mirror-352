# PyFilterLab

A simple Python toolkit for designing, visualizing, and applying digital FIR/IIR filters.

## Features

- FIR/IIR filter design
- Signal filtering
- Frequency response visualization
- Time-domain signal plotting

## Install

```bash
pip install pyfilterlab
```

## Usage


```bash
from pyfilterlab import design_fir, apply_filter, plot_response, plot_signal
```

## 📘 Use Reference

| Function | Description | Parameters | Returns |
|----------|-------------|------------|---------|
| `design_fir(num_taps, cutoff, fs, window='hamming')` | Designs a FIR low-pass filter using the window method. | - `num_taps` (int): Number of filter coefficients  
- `cutoff` (float): Cutoff frequency in Hz  
- `fs` (float): Sampling frequency in Hz  
- `window` (str): Type of window (e.g., 'hamming', 'hann', 'blackman') | `numpy.ndarray`: FIR filter coefficients |
| `design_iir(order, cutoff, fs, ftype='butter')` | Designs an IIR low-pass filter. | - `order` (int): Filter order  
- `cutoff` (float): Cutoff frequency in Hz  
- `fs` (float): Sampling frequency in Hz  
- `ftype` (str): Type of IIR filter ('butter', 'cheby1', 'cheby2', 'ellip') | Tuple (`b`, `a`): Numerator and denominator coefficients |
| `apply_filter(b, a, signal)` | Applies a filter to a signal using the filter coefficients. | - `b` (array): Numerator coefficients  
- `a` (array or 1): Denominator coefficients  
- `signal` (array): Input signal | `numpy.ndarray`: Filtered signal |
| `plot_response(b, a=1, fs=1.0, title='Frequency Response')` | Plots the frequency response (gain vs frequency) of the filter. | - `b`, `a`: Filter coefficients  
- `fs`: Sampling frequency  
- `title`: Plot title | Displays a Matplotlib plot |
| `plot_signal(signal, fs=1.0, title='Signal')` | Plots a time-domain signal. | - `signal`: Signal data  
- `fs`: Sampling frequency  
- `title`: Plot title | Displays a Matplotlib plot |
