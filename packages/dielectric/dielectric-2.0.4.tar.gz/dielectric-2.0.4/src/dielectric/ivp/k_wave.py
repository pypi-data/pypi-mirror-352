# https://github.com/waltsims/k-wave-python/blob/master/kwave/utils/signals.py

import logging
from math import floor
from math import pi
import math

import numpy as np
import scipy
from numpy.fft import ifftshift, fft, ifft
from typing import Optional, Tuple, Union, List


def rem(x, y, rtol=1e-05, atol=1e-08):
    """
    Returns the remainder after division of x by y, taking into account the floating point precision.
    x and y must be real and have compatible sizes.
    This function should be equivalent to the MATLAB rem function.

    Args:
        x (float, list, or ndarray): The dividend(s).
        y (float, list, or ndarray): The divisor(s).
        rtol (float): The relative tolerance parameter (see numpy.isclose).
        atol (float): The absolute tolerance parameter (see numpy.isclose).

    Returns:
        float or ndarray: The remainder after division.
    """
    if np.any(y == 0):
        return np.nan

    quotient = x / y
    closest_int = np.round(quotient)

    # check if quotient is close to an integer value
    if np.isclose(quotient, closest_int, rtol=rtol, atol=atol).all():
        return np.zeros_like(x)

    remainder = x - np.fix(quotient) * y

    return remainder


def gaussian(
    x: Union[int, float, np.ndarray],
    magnitude: Optional[Union[int, float]] = None,
    mean: Optional[float] = 0,
    variance: Optional[float] = 1,
) -> Union[int, float, np.ndarray]:
    """
    Returns a Gaussian distribution f(x) with the specified magnitude, mean, and variance. If these values are not specified,
    the magnitude is normalised and values of variance = 1 and mean = 0 are used. For example running:

        import matplotlib.pyplot as plt
        x = np.arange(-3, 0.05, 3)
        plt.plot(x, gaussian(x))

    will plot a normalised Gaussian distribution.

    Note, the full width at half maximum of the resulting distribution can be calculated by FWHM = 2 * sqrt(2 * log(2) * variance).

    Args:
        x: The input values.
        magnitude: Bell height. Defaults to normalised.
        mean: Mean or expected value. Defaults to 0.
        variance: Variance, or bell width. Defaults to 1.

    Returns:
        A Gaussian distribution.

    """

    if magnitude is None:
        magnitude = (2 * math.pi * variance) ** -0.5

    gauss_distr = magnitude * np.exp(-((x - mean) ** 2) / (2 * variance))

    return gauss_distr
    # return magnitude * norm.pdf(x, loc=mean, scale=variance)
    """ # Former impl. form Farid
        if magnitude is None:
        magnitude = np.sqrt(2 * np.pi * variance)
    return magnitude * np.exp(-(x - mean) ** 2 / (2 * variance))
    """


def tone_burst(sample_freq, signal_freq, num_cycles, envelope="Gaussian",
               plot_signal=False, signal_length=0, signal_offset=0):
    """
    Create an enveloped single frequency tone burst.

    Args:
        sample_freq: sampling frequency in Hz
        signal_freq: frequency of the tone burst signal in Hz
        num_cycles: number of sinusoidal oscillations
        envelope: Envelope used to taper the tone burst. Valid inputs are:
            - 'Gaussian' (the default)
            - 'Rectangular'
            - [num_ring_up_cycles, num_ring_down_cycles]
                The last option generates a continuous wave signal with a cosine taper of the specified length at the beginning and end.
        plot: Boolean controlling whether the created tone burst is plotted.
        signal_length: Signal length in number of samples. If longer than the tone burst length, the signal is appended with zeros.
        signal_offset: Signal offset before the tone burst starts in number of samples.
                        If an array is given, a matrix of tone bursts is created where each row corresponds to
                        a tone burst for each value of the 'SignalOffset'.

    Returns:
        created tone burst

    """
    assert isinstance(signal_offset, int) or isinstance(signal_offset, np.ndarray), "signal_offset must be integer or array of integers"
    assert isinstance(signal_length, int), "signal_length must be integer"

    # calculate the temporal spacing
    dt = 1 / sample_freq  # [s]

    # create the tone burst
    tone_length = num_cycles / signal_freq  # [s]
    # We want to include the endpoint but only if it's divisible by the step-size.
    # Modulo operator is not stable, so multiple conditions included.
    # if ( (tone_length % dt) < 1e-18 or (np.abs(tone_length % dt - dt) < 1e-18) ):
    if rem(tone_length, dt) < 1e-18:
        tone_t = np.linspace(0, tone_length, int(tone_length / dt) + 1)
    else:
        tone_t = np.arange(0, tone_length, dt)

    tone_burst = np.sin(2 * np.pi * signal_freq * tone_t)
    tone_index = np.round(signal_offset)

    # check for ring up and ring down input
    if isinstance(envelope, list) or isinstance(envelope, np.ndarray):
        num_ring_up_cycles, num_ring_down_cycles = envelope

        # check signal is long enough for ring up and down
        assert num_cycles >= (
            num_ring_up_cycles + num_ring_down_cycles
        ), "Input num_cycles must be longer than num_ring_up_cycles + num_ring_down_cycles."

        # get period
        period = 1 / signal_freq

        # create x-axis for ramp between 0 and pi
        up_ramp_length_points = round(num_ring_up_cycles * period / dt)
        down_ramp_length_points = round(num_ring_down_cycles * period / dt)
        up_ramp_axis = np.arange(0, np.pi + 1e-8, np.pi / (up_ramp_length_points - 1))
        down_ramp_axis = np.arange(0, np.pi + 1e-8, np.pi / (down_ramp_length_points - 1))

        # create ramp using a shifted cosine
        up_ramp = (-np.cos(up_ramp_axis) + 1) * 0.5
        down_ramp = (np.cos(down_ramp_axis) + 1) * 0.5

        # apply the ramps
        tone_burst[0:up_ramp_length_points] = tone_burst[0:up_ramp_length_points] * up_ramp
        tone_burst[-down_ramp_length_points:] = tone_burst[-down_ramp_length_points:] * down_ramp

    else:
        # create the envelope
        if envelope == "Gaussian":
            x_lim = 3
            window_x = np.arange(-x_lim, x_lim + 1e-8, 2 * x_lim / (len(tone_burst) - 1))
            window = gaussian(window_x, 1, 0, 1)
        elif envelope == "Rectangular":
            window = np.ones_like(tone_burst)
        elif envelope == "RingUpDown":
            raise NotImplementedError("RingUpDown not yet implemented")
        else:
            raise ValueError(f"Unknown envelope {envelope}.")

        # apply the envelope
        tone_burst = tone_burst * window

        # force the ends to be zero by applying a second window
        if envelope == "Gaussian":
            tone_burst = tone_burst * np.squeeze(get_win(len(tone_burst), type_="Tukey", param=0.05)[0])

    # Convert tone_index and signal_offset to numpy arrays
    signal_offset = np.array(signal_offset)

    # Determine the length of the signal array
    signal_length = max(signal_length, signal_offset.max() + len(tone_burst))

    # Create the signal array with the correct size
    signal = np.zeros((np.atleast_1d(signal_offset).size, signal_length))

    # Add the tone burst to the signal array
    tone_index = np.atleast_1d(tone_index)

    if tone_index.size == 1:
        tone_index = int(np.squeeze(tone_index))
        signal[:, tone_index : tone_index + len(tone_burst)] = tone_burst.T
    else:
        for i, idx in enumerate(tone_index):
            signal[i, int(idx) : int(idx) + len(tone_burst)] = tone_burst

    # plot the signal if required
    if plot_signal:
        raise NotImplementedError

    return signal
