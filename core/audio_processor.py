"""
Audio processing module for handling audio data and applying effects.
Provides core functionality for processing audio signals.
"""

import os
import wave
import numpy as np
import scipy.io.wavfile as wav
from scipy import signal
import traceback


def process_audio_file(input_file, output_file, effect_func, effect_params=None):
    """
    General function for applying any audio effect to a file.
    
    Parameters:
    -----------
    input_file : str
        Path to the input audio file
    output_file : str
        Path to the output audio file
    effect_func : callable
        Function that applies the effect
    effect_params : dict, optional
        Additional parameters for the effect
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    if effect_params is None:
        effect_params = {}
        
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: File {input_file} does not exist")
            return False
            
        # Verify input file is WAV
        ext = os.path.splitext(input_file)[1].lower()
        if ext != '.wav':
            print(f"Error: File {input_file} is not in WAV format")
            return False
        
        # Read audio file
        sample_rate, samples = wav.read(input_file)
        
        # Apply the effect
        processed_audio = effect_func(samples, sample_rate, **effect_params)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save processed audio
        wav.write(output_file, sample_rate, processed_audio)
        
        print(f"Audio processed successfully and saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error processing audio file: {e}")
        traceback.print_exc()
        return False


def running_mean(x, window_size):
    """
    Calculate running mean for an array.
    This function smooths the audio signal.
    
    Parameters:
    -----------
    x : numpy.ndarray
        Array for which to calculate the running mean
    window_size : int
        Size of the window for mean calculation
        
    Returns:
    --------
    numpy.ndarray
        Array with averaged values
    """
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size


def normalize_audio(audio_data, target_max=32767):
    """
    Normalize audio data to prevent clipping.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Audio data to normalize
    target_max : int, optional
        Target maximum value (default: 32767 for int16)
        
    Returns:
    --------
    numpy.ndarray
        Normalized audio data
    """
    # Find current max value
    max_val = np.max(np.abs(audio_data))
    
    # Avoid division by zero
    if max_val == 0:
        return audio_data
        
    # Scale the data
    if max_val > target_max:
        scaling_factor = target_max / max_val
        return audio_data * scaling_factor
    else:
        return audio_data


def combine_audio_effects(audio_data, sample_rate, effect_chain):
    """
    Apply multiple audio effects in sequence.
    
    Parameters:
    -----------
    audio_data : numpy.ndarray
        Audio data
    sample_rate : int
        Sample rate in Hz
    effect_chain : list
        List of (effect_func, params) tuples
        
    Returns:
    --------
    numpy.ndarray
        Processed audio data
    """
    processed_data = audio_data.copy()
    
    for effect_func, params in effect_chain:
        # Apply each effect in the chain
        processed_data = effect_func(processed_data, sample_rate, **params)
        
        # Ensure data stays within int16 range after each effect
        processed_data = np.clip(processed_data, -32768, 32767).astype(np.int16)
    
    return processed_data