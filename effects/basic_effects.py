"""
Basic audio effects module.
Provides simple audio effects like bass boost, reverb, echo, and speed control.
"""

import numpy as np
from scipy import signal
from numba import jit
from ..core.audio_processor import normalize_audio


def apply_bass_boost(audio_data, sample_rate, boost_factor=2.5, cutoff_freq=150.0, output_type=np.int16):
    """
    Apply bass boost effect to audio data.
    Uses a low-pass filter to isolate and amplify only low frequencies.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    boost_factor : float
        Amplification factor for bass (1.0-5.0 recommended)
    cutoff_freq : float
        Cutoff frequency for bass (Hz)
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with amplified bass
    """
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Design Butterworth low-pass filter
    nyq = 0.5 * sample_rate
    cutoff_norm = cutoff_freq / nyq
    b, a = signal.butter(4, cutoff_norm, btype='low')
    
    # Apply filter to get only low frequencies
    bass_frequencies = signal.lfilter(b, a, audio_float)
    
    # Amplify low frequencies and add back to original signal
    boosted_audio = audio_float + (boost_factor - 1) * bass_frequencies
    
    # Normalize to prevent clipping
    boosted_audio = normalize_audio(boosted_audio)
    
    return np.clip(boosted_audio, -32768, 32767).astype(output_type)


def apply_reverb(audio_data, sample_rate, room_size=0.75, damping=0.5, wet_level=0.3, output_type=np.int16):
    """
    Apply reverb effect (spatial echo) to audio data.
    Simulates sound in a room with multiple reflections.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    room_size : float
        Virtual room size (0.0-1.0)
    damping : float
        Reflection attenuation (0.0-1.0)
    wet_level : float
        Effect level (0.0-1.0)
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with reverb effect
    """
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Define multiple reflections with different times and amplitudes
    num_reflections = 8  # Number of simulated reflections
    reverb_signal = np.zeros_like(audio_float)
    
    # Add original signal
    reverb_signal += audio_float * (1.0 - wet_level)
    
    # Generate multiple reflections with different delays and attenuations
    for i in range(num_reflections):
        # Calculate delay (longer for larger room_size)
        delay_ms = 50 + (room_size * 150 * (i + 1))
        delay_samples = int(sample_rate * delay_ms / 1000)
        
        # Calculate decay factor (larger for lower damping)
        decay = wet_level * (1.0 - damping) ** (i+1) / (i+1)
        
        # Apply delay and add to reverb signal
        if delay_samples < len(audio_float):
            # Create reflection
            reflection = np.zeros_like(audio_float)
            reflection[delay_samples:] = audio_float[:-delay_samples] * decay
            reverb_signal += reflection
    
    # Normalize to prevent clipping
    reverb_signal = normalize_audio(reverb_signal)
    
    return np.clip(reverb_signal, -32768, 32767).astype(output_type)


def apply_echo(audio_data, sample_rate, delays_ms=[200, 400], decays=[0.5, 0.25], output_type=np.int16):
    """
    Apply echo effect with multiple echoes.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    delays_ms : list
        List of delay times in milliseconds for each echo
    decays : list
        List of decay factors for each echo
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with echo effect
    """
    # Check that we have the same number of delays and decays
    if len(delays_ms) != len(decays):
        raise ValueError("delays_ms and decays lists must have the same length")
    
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    echo_signal = np.copy(audio_float)
    
    # Apply each echo
    for delay_ms, decay in zip(delays_ms, decays):
        delay_samples = int(sample_rate * delay_ms / 1000)
        
        # Check that delay is not too large
        if delay_samples >= len(audio_float):
            continue
        
        # Create echo and add to final signal
        echo = np.zeros_like(audio_float)
        echo[delay_samples:] = audio_float[:-delay_samples] * decay
        echo_signal += echo
    
    # Normalize to prevent clipping
    echo_signal = normalize_audio(echo_signal)
    
    return np.clip(echo_signal, -32768, 32767).astype(output_type)


def apply_speed_up(audio_data, sample_rate, speed_factor=1.2, preserve_pitch=True, output_type=np.int16):
    """
    Apply speed change to audio, with option to preserve original pitch.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    speed_factor : float
        Speed factor (1.0 = normal speed, 2.0 = double speed)
    preserve_pitch : bool
        Whether to preserve original pitch (True) or allow it to change (False)
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Processed audio data with modified speed
    """
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    if preserve_pitch:
        # Complex method: Short-time Fourier Transform (STFT)
        # This method allows changing speed without affecting pitch
        
        # Calculate new signal length
        new_length = int(len(audio_float) / speed_factor)
        
        # STFT parameters
        hop_length = 256  # Step size between consecutive windows
        n_fft = 2048      # FFT window size
        
        # Use signal library for STFT
        f, t, X = signal.stft(audio_float, fs=sample_rate, nperseg=n_fft, 
                            noverlap=n_fft-hop_length, boundary=None)
        
        # Modify time axis by interpolation
        time_steps = np.arange(X.shape[1])
        new_time_steps = np.linspace(0, X.shape[1] - 1, int(X.shape[1] / speed_factor))
        
        # Resize STFT using interpolation
        new_X = np.zeros((X.shape[0], len(new_time_steps)), dtype=X.dtype)
        
        # Interpolate real and imaginary parts separately to preserve complex properties
        for i in range(X.shape[0]):
            real_part = np.interp(new_time_steps, time_steps, np.real(X[i, :]))
            imag_part = np.interp(new_time_steps, time_steps, np.imag(X[i, :]))
            new_X[i, :] = real_part + 1j * imag_part
        
        # Apply inverse STFT to reconstruct signal
        _, modified_audio = signal.istft(new_X, fs=sample_rate, nperseg=n_fft,
                                       noverlap=n_fft-hop_length, boundary=None)
        
        # Ensure correct length
        if len(modified_audio) > new_length:
            modified_audio = modified_audio[:new_length]
        
    else:
        # Simple method: Resampling for speed change with pitch change
        # This will increase pitch when increasing speed
        new_length = int(len(audio_float) / speed_factor)
        modified_audio = signal.resample(audio_float, new_length)
    
    # Normalize to prevent clipping
    modified_audio = normalize_audio(modified_audio)
    
    # Convert back to int16
    return np.clip(modified_audio, -32768, 32767).astype(output_type)


@jit(nopython=True)
def apply_tremolo(audio_data, sample_rate, depth=0.5, rate=5.0, output_type=np.int16):
    """
    Apply tremolo effect to audio data.
    Tremolo creates a periodic oscillation of volume to achieve a vibrato effect.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    depth : float
        Modulation depth (0.0-1.0), where 0 = no effect and 1.0 = full modulation
    rate : float
        Oscillation frequency in Hz (cycles per second)
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
    
    Returns:
    --------
    numpy.ndarray
        Audio data with tremolo effect
    """
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Calculate total number of samples
    num_samples = len(audio_float)
    
    # Generate a modulation sinusoidal signal
    # Oscillation frequency is determined by the "rate" parameter
    time = np.arange(num_samples) / sample_rate
    modulation = 1.0 - depth * 0.5 * (1.0 + np.sin(2.0 * np.pi * rate * time))
    
    # Apply modulation to audio signal
    tremolo_signal = audio_float * modulation
    
    # Normalize to prevent clipping
    tremolo_signal = normalize_audio(tremolo_signal)
    
    # Convert back to int16
    return np.clip(tremolo_signal, -32768, 32767).astype(output_type)