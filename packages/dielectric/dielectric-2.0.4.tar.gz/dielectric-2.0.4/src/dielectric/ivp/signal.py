# https://medium.com/@t.gamsjaeger/elementary-signal-generation-with-python-4bd4642ad5f8

import numpy as np
from scipy import signal as sg
import scipy.fft as fft
import matplotlib.pyplot as plt
import matplotlib


matplotlib.use("QtAgg")

amp = 1.0
freq = 1.0e3
t = np.linspace(0, 0.01, 1000, endpoint=False)
signal1 = amp*np.sin(2*np.pi*freq*t)
signal2 = amp*sg.square(2*np.pi*freq*t, duty=0.3)
signal3 = amp*sg.sawtooth(2*np.pi*freq*t, width=0.5)

plt.subplots(figsize=(10, 4))
plt.plot(t, signal1, label='sin')
plt.plot(t, signal2, label='square')
plt.plot(t, signal3, label='sawtooth')
plt.xlabel('time (s)')
plt.ylabel('voltage (mV)')
plt.title('sin and square wave')
plt.grid()
plt.legend()
plt.show()

# Generate a time-domain signal
t = np.linspace(0, 1, 1000)
x = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 20 * t)

# Calculate the Fourier Transform
X = fft.fft(x)
freqs = fft.fftfreq(x.size, d=t[1]-t[0])  # Calculate the frequencies

# Plot the frequency-domain representation of the signal
plt.subplots(figsize=(10, 4))
plt.plot(freqs, np.abs(X))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.xlim([0, 50])  # Display frequencies from 0 to 50 Hz for clarity
plt.show()


# Generate a time-domain signal
t = np.linspace(0, 1, 1000)
x = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 20 * t)

# Estimate the PSD using the Welch Method
freqs, Pxx = sg.welch(x, fs=1000)

# Plot the estimated PSD
plt.plot(freqs, Pxx)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power')
plt.xlim([0, 50])  # Display frequencies from 0 to 50 Hz for clarity
plt.show()