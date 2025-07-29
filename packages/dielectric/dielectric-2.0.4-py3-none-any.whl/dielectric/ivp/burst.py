# https://stridecodes.readthedocs.io/en/latest/_modules/stride/utils/wavelets.html

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import get_window, gausspulse
from typing import Optional, Tuple, Union, List
import math
import matplotlib
from stride import tone_burst

matplotlib.use("QtAgg")


import logging
from math import floor

import numpy as np
import scipy
from numpy.fft import ifftshift, fft, ifft


if __name__ == "__main__":
    s = tone_burst(centre_freq=1.0e6, n_cycles=15.0,
                   n_samples=2500, dt=1.0e-8, envelope='rectangular', offset=100)
    fig, ax = plt.subplots()
    ax.plot(s)
    ax.set_xlabel('Sample #')
    ax.set_ylabel('Amplitude')
    ax.set_title('Tone burst wavelet')
    fig.tight_layout()
    plt.show()

    t = np.linspace(-1, 1, 2 * 100, endpoint=False)
    i, q, e = gausspulse(t, fc=5, retquad=True, retenv=True)
    fig, ax = plt.subplots()
    ax.plot(t, i, t, q, t, e, '--')
    plt.show()


