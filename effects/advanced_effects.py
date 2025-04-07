"""
Advanced audio effects module.
Provides complex audio effects like equalizer, noise cancellation, and combined effects.
"""

import numpy as np
from scipy import signal
import scipy.fftpack as fft
from ..core.audio_processor import normalize_audio


def apply_pitch_shift(audio_data, sample_rate, n_steps=4, output_type=np.int16):
    """
    Apply pitch shifting to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    n_steps : int
        Number of semitones to shift (positive = up, negative = down)
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with shifted pitch
    """
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Calculate pitch factor from semitones (1 semitone = 2^(1/12) ratio)
    pitch_factor = 2 ** (n_steps / 12)
    
    # First apply speed change to modify the pitch
    from .basic_effects import apply_speed_up
    speed_changed = apply_speed_up(
        audio_float, 
        sample_rate, 
        speed_factor=pitch_factor, 
        preserve_pitch=False
    )
    
    # Then apply speed change again in the opposite direction to keep duration
    # but preserve the pitch change
    restored_duration = apply_speed_up(
        speed_changed, 
        sample_rate, 
        speed_factor=1/pitch_factor, 
        preserve_pitch=True
    )
    
    # Normalize to prevent clipping
    restored_duration = normalize_audio(restored_duration)
    
    return np.clip(restored_duration, -32768, 32767).astype(output_type)


def apply_equalizer(audio_data, sample_rate, gains=None, output_type=np.int16):
    """
    Apply a multi-band equalizer to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    gains : list
        List of gain values for each frequency band.
        Values >1 amplify, values <1 attenuate. Values between 0.1 and 3.0 are recommended.
        If None, default values [1.0, 1.0, 1.0, 1.0, 1.0] are used
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with equalizer applied
    """
    # Define default gain values (neutral)
    if gains is None:
        gains = [1.0, 1.0, 1.0, 1.0, 1.0]
    
    # Ensure we have exactly 5 gain values
    if len(gains) != 5:
        raise ValueError("You must specify exactly 5 gain values")
    
    # Define frequency bands (Hz)
    bands = [
        (20, 250),      # Bass - low frequencies
        (250, 500),     # Low-mids
        (500, 2000),    # Mids
        (2000, 5000),   # Upper-mids
        (5000, 20000)   # Highs - high frequencies
    ]
    
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Apply equalizer using band-pass filters
    equalized_audio = np.zeros_like(audio_float, dtype=np.float32)
    
    # For each band, apply a filter and amplify/attenuate
    for i, ((low_freq, high_freq), gain) in enumerate(zip(bands, gains)):
        # Normalize frequencies
        nyq = 0.5 * sample_rate
        low_norm = low_freq / nyq
        high_norm = high_freq / nyq
        
        # For bass band, use a low-pass filter
        if i == 0:
            b, a = signal.butter(2, high_norm, btype='lowpass')
        # For high band, use a high-pass filter
        elif i == len(bands) - 1:
            b, a = signal.butter(2, low_norm, btype='highpass')
        # For mid bands, use band-pass filters
        else:
            b, a = signal.butter(2, [low_norm, high_norm], btype='bandpass')
        
        # Apply filter
        filtered_band = signal.lfilter(b, a, audio_float)
        
        # Apply gain and add to final result
        equalized_audio += filtered_band * gain
    
    # Normalize to prevent clipping
    equalized_audio = normalize_audio(equalized_audio)
    
    return np.clip(equalized_audio, -32768, 32767).astype(output_type)

def apply_compressor(audio_data, sample_rate, threshold=-20, ratio=4, attack=0.005, release=0.05, output_type=np.int16):
    """
    Apply dynamic range compression to audio data.
    Reduces the volume of loud sounds and amplifies quiet sounds.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    threshold : float
        Threshold in dB below which compression starts
    ratio : float
        Compression ratio (higher values = more compression)
    attack : float
        Attack time in seconds
    release : float
        Release time in seconds
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with compression applied
    """
    # Convert to float
    audio_float = audio_data.astype(np.float32) / 32767.0
    
    # Calculate attack and release parameters
    attack_coef = np.exp(-1.0 / (sample_rate * attack))
    release_coef = np.exp(-1.0 / (sample_rate * release))
    
    # Convert threshold to linear
    threshold_linear = 10.0 ** (threshold / 20.0)
    
    # Initialize gain and envelope
    gain = 1.0
    envelope = 0.0
    compressed = np.zeros_like(audio_float)
    
    # Apply compression sample by sample
    for i in range(len(audio_float)):
        # Calculate envelope (absolute value with attack/release)
        sample = abs(audio_float[i])
        if envelope < sample:
            envelope = sample + attack_coef * (envelope - sample)
        else:
            envelope = sample + release_coef * (envelope - sample)
        
        # Apply compression if above threshold
        if envelope > threshold_linear:
            gain = threshold_linear * (envelope / threshold_linear) ** (1.0 / ratio) / envelope
        else:
            gain = 1.0
        
        # Apply gain
        compressed[i] = audio_float[i] * gain
    
    # Normalize to prevent clipping
    compressed = normalize_audio(compressed * 32767.0)
    
    return np.clip(compressed, -32768, 32767).astype(output_type)


def apply_echo_speed_combo(audio_data, sample_rate, echo_params=None, speed_params=None, output_type=np.int16):
    """
    Combine Echo and Speed-Up effects for a complex audio effect.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    echo_params : dict, optional
        Parameters for echo effect
    speed_params : dict, optional
        Parameters for speed-up effect
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with combined effects applied
    """
    # Initialize default parameters if None
    if echo_params is None:
        echo_params = {
            'delays_ms': [200, 400],
            'decays': [0.5, 0.25]
        }
    
    if speed_params is None:
        speed_params = {
            'speed_factor': 1.2,
            'preserve_pitch': True
        }
    
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Apply echo effect
    from .basic_effects import apply_echo
    echo_audio = apply_echo(
        audio_float, 
        sample_rate,
        delays_ms=echo_params.get('delays_ms', [200, 400]),
        decays=echo_params.get('decays', [0.5, 0.25])
    )
    
    # Apply speed-up effect to the echo result
    from .basic_effects import apply_speed_up
    processed_audio = apply_speed_up(
        echo_audio,
        sample_rate,
        speed_factor=speed_params.get('speed_factor', 1.2),
        preserve_pitch=speed_params.get('preserve_pitch', True)
    )
    
    # Normalize to prevent clipping
    processed_audio = normalize_audio(processed_audio)
    
    return np.clip(processed_audio, -32768, 32767).astype(output_type)