"""
Filters module for audio signal processing.
Provides FIR (Finite Impulse Response) filters for audio processing.
"""

import numpy as np
from scipy import signal
from ..core.audio_processor import normalize_audio


def fir_low_pass(audio_data, sample_rate, cutoff_freq=1000, N=101, output_type=np.int16):
    """
    Apply a FIR low-pass filter to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    cutoff_freq : float
        Cutoff frequency in Hz
    N : int
        Order of the filter (number of coefficients)
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
        
    Returns:
    --------
    numpy.ndarray
        Filtered audio data
    """
    # Normalize cutoff frequency
    cutoff_freq = cutoff_freq / sample_rate

    # Calculate sinc filter
    h = np.sinc(2 * cutoff_freq * (np.arange(N) - (N - 1) / 2.))
    # Apply Hamming window
    h *= np.hamming(N)
    # Normalize to get unity gain
    h /= np.sum(h)
    
    # Apply filter by convolution
    audio_filtered = np.convolve(audio_data, h)
    
    # Normalize to prevent clipping
    audio_filtered = normalize_audio(audio_filtered)
    
    return np.clip(audio_filtered, -32768, 32767).astype(output_type)


def fir_high_pass(audio_data, sample_rate, cutoff_freq=1000, N=101, output_type=np.int16):
    """
    Apply a FIR high-pass filter to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    cutoff_freq : float
        Cutoff frequency in Hz
    N : int
        Order of the filter (number of coefficients)
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
        
    Returns:
    --------
    numpy.ndarray
        Filtered audio data
    """
    # Normalize cutoff frequency
    cutoff_freq = cutoff_freq / sample_rate

    # Calculate sinc filter (same as low-pass)
    h = np.sinc(2 * cutoff_freq * (np.arange(N) - (N - 1) / 2.))
    # Apply Hamming window
    h *= np.hamming(N)
    # Normalize to get unity gain
    h /= np.sum(h)
    
    # Convert to high-pass by spectral inversion
    h = -h
    h[int((N - 1) / 2)] += 1  # Add impulse at center
    
    # Apply filter by convolution
    audio_filtered = np.convolve(audio_data, h)
    
    # Normalize to prevent clipping
    audio_filtered = normalize_audio(audio_filtered)
    
    return np.clip(audio_filtered, -32768, 32767).astype(output_type)


def fir_band_pass(audio_data, sample_rate, low_cutoff=500, high_cutoff=2000, N_low=101, N_high=101, output_type=np.int16):
    """
    Apply a FIR band-pass filter to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    low_cutoff : float
        Lower cutoff frequency in Hz
    high_cutoff : float
        Higher cutoff frequency in Hz
    N_low : int
        Order of the low-pass filter
    N_high : int
        Order of the high-pass filter
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
        
    Returns:
    --------
    numpy.ndarray
        Filtered audio data
    """
    # Normalize cutoff frequencies
    low_cutoff = low_cutoff / sample_rate
    high_cutoff = high_cutoff / sample_rate

    # Calculate low-pass filter with cutoff frequency high_cutoff
    hlpf = np.sinc(2 * high_cutoff * (np.arange(N_high) - (N_high - 1) / 2.))
    hlpf *= np.blackman(N_high)
    hlpf /= np.sum(hlpf)
    
    # Calculate high-pass filter with cutoff frequency low_cutoff
    hhpf = np.sinc(2 * low_cutoff * (np.arange(N_low) - (N_low - 1) / 2.))
    hhpf *= np.blackman(N_low)
    hhpf /= np.sum(hhpf)
    hhpf = -hhpf
    hhpf[int((N_low - 1) / 2)] += 1
    
    # Convolve low-pass and high-pass filters to get band-pass filter
    h = np.convolve(hlpf, hhpf)
    
    # Apply filter by convolution
    audio_filtered = np.convolve(audio_data, h)
    
    # Normalize to prevent clipping
    audio_filtered = normalize_audio(audio_filtered)
    
    return np.clip(audio_filtered, -32768, 32767).astype(output_type)


def fir_band_reject(audio_data, sample_rate, low_cutoff=500, high_cutoff=2000, N_low=101, N_high=101, output_type=np.int16):
    """
    Apply a FIR band-reject filter to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    low_cutoff : float
        Lower cutoff frequency in Hz
    high_cutoff : float
        Higher cutoff frequency in Hz
    N_low : int
        Order of the low-pass filter
    N_high : int
        Order of the high-pass filter
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
        
    Returns:
    --------
    numpy.ndarray
        Filtered audio data
    """
    # Normalize cutoff frequencies
    low_cutoff = low_cutoff / sample_rate
    high_cutoff = high_cutoff / sample_rate

    # Calculate low-pass filter with cutoff frequency low_cutoff
    hlpf = np.sinc(2 * low_cutoff * (np.arange(N_low) - (N_low - 1) / 2.))
    hlpf *= np.blackman(N_low)
    hlpf /= np.sum(hlpf)
    
    # Calculate high-pass filter with cutoff frequency high_cutoff
    hhpf = np.sinc(2 * high_cutoff * (np.arange(N_high) - (N_high - 1) / 2.))
    hhpf *= np.blackman(N_high)
    hhpf /= np.sum(hhpf)
    hhpf = -hhpf
    hhpf[int((N_high - 1) / 2)] += 1
    
    # Add both filters
    if N_high >= N_low:
        h = hhpf
        h[int((N_high - N_low) / 2) : int((N_high - N_low) / 2 + N_low)] += hlpf
    else:
        h = hlpf
        h[int((N_low - N_high) / 2) : int((N_low - N_high) / 2 + N_high)] += hhpf
    
    # Apply filter by convolution
    audio_filtered = np.convolve(audio_data, h)
    
    # Normalize to prevent clipping
    audio_filtered = normalize_audio(audio_filtered)
    
    return np.clip(audio_filtered, -32768, 32767).astype(output_type)


def butter_low_pass(audio_data, sample_rate, cutoff_freq=1000, order=4, output_type=np.int16):
    """
    Apply a Butterworth low-pass filter to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    cutoff_freq : float
        Cutoff frequency in Hz
    order : int
        Order of the filter
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
        
    Returns:
    --------
    numpy.ndarray
        Filtered audio data
    """
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Design Butterworth filter
    nyq = 0.5 * sample_rate
    normal_cutoff = cutoff_freq / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low')
    
    # Apply filter
    audio_filtered = signal.lfilter(b, a, audio_float)
    
    # Normalize to prevent clipping
    audio_filtered = normalize_audio(audio_filtered)
    
    return np.clip(audio_filtered, -32768, 32767).astype(output_type)


def butter_high_pass(audio_data, sample_rate, cutoff_freq=1000, order=4, output_type=np.int16):
    """
    Apply a Butterworth high-pass filter to audio data.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Input audio data
    sample_rate : int
        Sample rate of the audio signal
    cutoff_freq : float
        Cutoff frequency in Hz
    order : int
        Order of the filter
    output_type : numpy.dtype, optional
        Output data type (default: np.int16)
        
    Returns:
    --------
    numpy.ndarray
        Filtered audio data
    """
    # Convert to float for processing
    audio_float = audio_data.astype(np.float32)
    
    # Design Butterworth filter
    nyq = 0.5 * sample_rate
    normal_cutoff = cutoff_freq / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high')
    
    # Apply filter
    audio_filtered = signal.lfilter(b, a, audio_float)
    
    # Normalize to prevent clipping
    audio_filtered = normalize_audio(audio_filtered)
    
    return np.clip(audio_filtered, -32768, 32767).astype(output_type)