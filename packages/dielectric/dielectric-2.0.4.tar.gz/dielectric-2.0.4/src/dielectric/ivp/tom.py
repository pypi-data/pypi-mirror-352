# https://medium.com/tomtalkspython/scipy-for-signal-processing-2fa2c8a290c4

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sg
from scipy.signal import spectrogram
from scipy.signal import find_peaks
import matplotlib
matplotlib.use("QtAgg")

# Parameters
fs = 1000                  # Sampling frequency
t = np.arange(0, 1, 1/fs)  # Time vector
frequency = 5              # Frequency of the sine wave

# Creating a sine wave
signal = np.sin(2 * np.pi * frequency * t)

# Plotting the signal
plt.plot(t, signal)
plt.title('Original Sine Wave Signal')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.grid()
plt.show()

# Adding noise
noise = np.random.normal(0, 0.5, signal.shape)
noisy_signal = signal + noise

# Plotting the noisy signal
plt.plot(t, noisy_signal)
plt.title('Noisy Sine Wave Signal')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.grid()
plt.show()

# Designing a low-pass Butterworth filter
cutoff_frequency = 10   # Cutoff frequency in Hz
b, a = sg.butter(4, cutoff_frequency / (0.5 * fs), btype='low')

# Applying the filter
filtered_signal = sg.filtfilt(b, a, noisy_signal)

# Plotting the filtered signal
plt.plot(t, filtered_signal, label='Filtered Signal', color='red')
plt.plot(t, noisy_signal, label='Noisy Signal', color='gray', alpha=0.5)
plt.title('Filtered Sine Wave Signal')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.legend()
plt.grid()
plt.show()

# Performing FFT
frequencies = np.fft.fftfreq(len(t), 1/fs)
fft_original = np.fft.fft(signal)
fft_filtered = np.fft.fft(filtered_signal)

# Plotting the frequency spectrum
plt.plot(frequencies[:len(frequencies)//2], np.abs(fft_original)[:len(frequencies)//2],
         label='Original Signal')
plt.plot(frequencies[:len(frequencies)//2], np.abs(fft_filtered)[:len(frequencies)//2],
         label='Filtered Signal', color='red')
plt.title('Frequency Spectrum')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude')
plt.xlim(0, 50)
plt.legend()
plt.grid()
plt.show()

# Generate a Sample Signal: Create a signal composed of multiple sinusoidal waves.
fs = 1000                                                # Sampling frequency
t = np.linspace(0, 1.0, fs, endpoint=False)  # Time array
signal = 0.5 * np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 120 * t)

# Compute the Spectrogram: Use the spectrogram function to compute the spectrogram of the signal.
f, t, Sxx = spectrogram(signal, fs)

# Plot the Spectrogram: Visualize the spectrogram using matplotlib.
plt.figure(figsize=(10, 6))
plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.title('Spectrogram')
plt.colorbar(label='Intensity [dB]')
plt.show()

# Generate a Noisy Signal: Create a synthetic signal with added noise.
x = np.linspace(0, 10, 1000)
y = np.sin(x) + np.random.normal(0, 0.5, 1000) # Sine wave + noise

# Detect Peaks: Use the find_peaks function to find peaks in the noisy signal.
peaks, _ = find_peaks(y, height=0) # Adjust height as needed

# Plot the Results: Visualize the noisy signal and mark the detected peaks.
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='Noisy Signal')
plt.plot(x[peaks], y[peaks], "x", label='Detected Peaks', color='red')
plt.title('Peak Detection in Noisy Signal')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.legend()
plt.show()