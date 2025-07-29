# https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.signal.hilbert.html

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, chirp
import matplotlib

matplotlib.use("QtAgg")


duration = 1.0
fs = 400.0
samples = int(fs*duration)
t = np.arange(samples) / fs

signal = chirp(t, 20.0, t[-1], 100.0)
signal *= (1.0 + 0.5 * np.sin(2.0*np.pi*3.0*t) )
analytic_signal = hilbert(signal)
amplitude_envelope = np.abs(analytic_signal)
instantaneous_phase = np.unwrap(np.angle(analytic_signal))
instantaneous_frequency = (np.diff(instantaneous_phase) /
                           (2.0*np.pi) * fs)

# https://stackoverflow.com/questions/60962094/find-peaks-and-envelope-question-in-python
upper_envelope = np.abs(hilbert(signal))

fig, (ax0, ax1) = plt.subplots(nrows=2)
ax0.plot(t, signal, label='signal')
ax0.plot(t, amplitude_envelope, label='envelope')
ax0.plot(t, upper_envelope, 'g--', label='upper envelope')
ax0.set_xlabel("time in seconds")
ax0.legend()
ax1.plot(t[1:], instantaneous_frequency)
ax1.set_xlabel("time in seconds")
ax1.set_ylim(0.0, 120.0)
fig.tight_layout()
plt.show()
