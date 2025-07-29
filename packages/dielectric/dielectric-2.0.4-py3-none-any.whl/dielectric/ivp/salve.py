
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import get_window
import matplotlib

matplotlib.use("QtAgg")


def my_tone_burst(sample_freq, signal_freq, num_cycles,
                  signal_length=0, signal_offset=0):
    assert isinstance(signal_offset, int) or isinstance(signal_offset, np.ndarray), \
           "signal_offset must be integer or array of integers"
    assert isinstance(signal_length, int), \
           "signal_length must be integer"

    # calculate the temporal spacing
    dt = 1.0 / sample_freq  # in [s]

    # create the tone burst
    tone_length = num_cycles / signal_freq  # in [s]

import numpy as np
from matplotlib import pyplot as plt

SAMPLE_RATE = 44100  # Hertz
DURATION = 5  # Seconds


def generate_sine_wave(freq, sample_rate, duration):
    t = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    frequencies = x * freq
    # 2pi because np.sin takes radians
    y = np.sin((2 * np.pi) * frequencies)
    return x, y


def generate_sine(freq=100e3, fsample=10e6, duration=0.2e3):
    # fsin = 1.0; % sine freq
    # Fs = 100*fsin; % sampling freq
    dt = np.reciprocal(fsample)

    # duration = 0.2e-3; % signal duration in seconds
    samples = np.ceil(duration*fsample)
    t = dt * np.arange(0, samples-1, 1)
    offset = dt * (samples/2)    # to center the gaussian envelope

    a = 200 * fsample  # increase or decrease a to change number of periods
    signal = np.sin(2*np.pi*freq*t) *np.exp(-a * (t-offset)**2)
    return t, signal


def generate_burst(centre_freq, n_cycles, n_samples, dt, offset=0):




if __name__ == "__main__":
    tm, sig = generate_sine()
    plt.subplots()
    plt.plot(tm, sig)
    plt.grid(True)
    plt.show()

    # Generate a 2 hertz sine wave that lasts for 5 seconds
    x, y = generate_sine_wave(2, SAMPLE_RATE, DURATION)
    plt.plot(x, y)
    plt.show()
