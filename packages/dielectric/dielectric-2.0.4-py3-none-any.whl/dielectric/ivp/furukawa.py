# https://github.com/ryo-furukawa-1122/Tone-Burst-Generator/blob/main/python/generate_wav.py

import numpy as np
from scipy.io.wavfile import write


# Function to generate a sine wave and save as a .wav file
def generate_tone(frequency, duration, sample_rate, file_name):
    """
    Generate a pure tone wave and save it as a .wav file.

    Args:
        frequency (int): The frequency of the tone in Hz.
        duration (float): The duration of the tone in seconds.
        sample_rate (int): The sample rate in Hz.
        file_name (str): The name of the output .wav file.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t) * 0.5  # Scale amplitude to avoid clipping
    tone = (tone * 32767).astype(np.int16)  # Convert to 16-bit PCM format
    write(file_name, sample_rate, tone)
    print(f"Generated {file_name}")

# Parameters
sample_rate = 44100  # 44.1 kHz
duration = 60  # 2 seconds
frequencies = [2000, 4000, 8000, 16000]  # Desired frequencies in Hz
file_names = [f"{freq}Hz.wav" for freq in frequencies]

# Generate tones
for freq, file_name in zip(frequencies, file_names):
    generate_tone(freq, duration, sample_rate, file_name)