"""
File handling module for audio file operations.
Provides functionality for reading, analyzing, and extracting information from audio files.
"""

import os
import wave
import numpy as np
import traceback
import scipy.io.wavfile as wav
import librosa
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_audio_info(file_path):
    """
    Extract and display technical details of an audio file.
    Supports both WAV and MP3 files.
    
    Parameters:
    -----------
    file_path : str
        Path to the audio file
        
    Returns:
    --------
    dict
        A dictionary with the audio file information
    """
    info = {}
    
    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # Get file size
        info['file_size'] = os.path.getsize(file_path)
        info['file_size_mb'] = round(info['file_size'] / (1024 * 1024), 2)
        
        if ext == '.wav':
            try:
                with wave.open(file_path, 'rb') as wav_file:
                    info['format'] = 'WAV'
                    info['channels'] = wav_file.getnchannels()
                    info['sample_width'] = wav_file.getsampwidth() * 8  # convert to bits
                    info['sample_rate'] = wav_file.getframerate()
                    info['frames'] = wav_file.getnframes()
                    info['duration'] = info['frames'] / info['sample_rate']
                    info['bitrate'] = int(info['sample_rate'] * info['sample_width'] * info['channels'])
                
                # Load metadata using mutagen
                try:
                    wave_data = WAVE(file_path)
                    if hasattr(wave_data, 'tags'):
                        info['metadata'] = wave_data.tags
                    else:
                        info['metadata'] = "No metadata"
                except Exception as e:
                    info['metadata_error'] = str(e)
                    
            except Exception as e:
                info['error'] = f"Error reading WAV file: {str(e)}"
                
        elif ext == '.mp3':
            try:
                # Use mutagen for MP3
                mp3_data = MP3(file_path)
                
                info['format'] = 'MP3'
                info['channels'] = mp3_data.info.channels
                info['sample_rate'] = mp3_data.info.sample_rate
                info['duration'] = mp3_data.info.length
                info['bitrate'] = mp3_data.info.bitrate
                
                # Extract metadata (ID3 tags)
                if mp3_data.tags:
                    metadata = {}
                    for key, value in mp3_data.tags.items():
                        metadata[key] = str(value)
                    info['metadata'] = metadata
                else:
                    info['metadata'] = "No metadata"
                    
            except Exception as e:
                info['error'] = f"Error reading MP3 file: {str(e)}"
        else:
            info['error'] = f"Unsupported file format: {ext}"
    except Exception as e:
        logging.error(f"General error: {str(e)}")
        info['error'] = f"General error: {str(e)}"
    
    return info


def extract_audio_data(file_path, keep_stereo=False):
    """
    Extract audio data from a file for visualization and processing.
    Supports both WAV and MP3.
    
    Parameters:
    -----------
    file_path : str
        Path to the audio file
    keep_stereo : bool
        If True, keeps stereo channels (if they exist)
        
    Returns:
    --------
    tuple
        A tuple (samples, sample_rate), where samples is a numpy.ndarray and
        sample_rate is the sample rate in Hz
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File does not exist: {file_path}")
            return None, None
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.wav':
            try:
                # Read WAV file directly
                sample_rate, samples = wav.read(file_path)
                
                # Debug info - display information about data shape
                print(f"WAV: Initial data shape: {samples.shape}, type: {samples.dtype}")
                
                # If we have stereo and don't want to keep stereo channels, convert to mono for visualization
                if len(samples.shape) > 1 and not keep_stereo:
                    print(f"Converting stereo audio to mono (channels: {samples.shape[1]})")
                    samples = np.mean(samples, axis=1).astype(np.int16)
                    print(f"WAV: Shape after conversion to mono: {samples.shape}")
                
                return samples, sample_rate
            except Exception as e:
                print(f"Error reading WAV file: {e}")
                traceback.print_exc()
                return None, None
                
        elif ext == '.mp3':
            try:
                # Use librosa to extract audio data from MP3
                if keep_stereo:
                    # For MP3, if we want stereo
                    samples, sample_rate = librosa.load(file_path, sr=None, mono=False)
                    print(f"MP3: Initial stereo data shape: {samples.shape}, type: {samples.dtype}")
                    
                    # librosa returns an array of shape (channels, samples) but we need (samples, channels)
                    if len(samples.shape) > 1:
                        samples = samples.T
                        print(f"MP3: Shape after transposition: {samples.shape}")
                else:
                    # For visualization, we usually use mono
                    samples, sample_rate = librosa.load(file_path, sr=None, mono=True)
                    print(f"MP3: Initial mono data shape: {samples.shape}, type: {samples.dtype}")
                
                # Convert to int16 for compatibility
                samples = (samples * 32767).astype(np.int16)
                print(f"MP3: Final shape after conversion to int16: {samples.shape}")
                
                return samples, sample_rate
            except Exception as e:
                print(f"Error reading MP3 file: {str(e)}")
                traceback.print_exc()
                return None, None
                
        else:
            print(f"Unsupported format: {ext}")
            return None, None
            
    except Exception as e:
        logging.error(f"General error processing file: {str(e)}")
        traceback.print_exc()
        return None, None


def save_audio_file(samples, sample_rate, file_path):
    """
    Save audio data to a WAV file.
    
    Parameters:
    -----------
    samples : numpy.ndarray
        Audio samples
    sample_rate : int
        Sample rate in Hz
    file_path : str
        Output file path
        
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Write WAV file
        wav.write(file_path, sample_rate, samples)
        return True
    except Exception as e:
        logging.error(f"Error saving audio file: {e}")
        traceback.print_exc()
        return False


def compare_stereo_channels(file_path):
    """
    Compare stereo channels of an audio file.
    Returns information about differences between channels.
    
    Parameters:
    -----------
    file_path : str
        Path to the audio file
        
    Returns:
    --------
    dict
        Dictionary with comparison results or error information
    """
    result = {}
    
    try:
        print(f"Analyzing file for channel comparison: {file_path}")
        # Use keep_stereo=True to preserve stereo channels
        samples, sample_rate = extract_audio_data(file_path, keep_stereo=True)
        
        if samples is None:
            result['error'] = "Could not extract audio data"
            return result
            
        print(f"Extracted data shape: {samples.shape}, type: {samples.dtype}")
        
        # Check array shape to determine if it's stereo
        if len(samples.shape) > 1 and samples.shape[1] > 1:
            print(f"File has {samples.shape[1]} channels")
            channel_left = samples[:, 0]  # Left channel
            channel_right = samples[:, 1]  # Right channel
            
            # Calculate differences
            difference = np.abs(channel_left - channel_right)
            
            # Populate results
            result['max_difference'] = int(np.max(difference))
            result['mean_difference'] = float(np.mean(difference))
            result['min_difference'] = int(np.min(difference))
            result['correlation'] = float(np.corrcoef(channel_left, channel_right)[0,1])
            
            # Add descriptive analysis
            mean_diff = np.mean(difference)
            if mean_diff < 10:
                result['analysis'] = "Channels are almost identical. Probably a mono file converted to stereo."
            elif mean_diff < 1000:
                result['analysis'] = "Channels have moderate differences. This is a typical stereo file."
            else:
                result['analysis'] = "Channels have significant differences. This is a stereo file with distinct channels."
                
            result['is_stereo'] = True
        else:
            result['is_stereo'] = False
            result['analysis'] = "Audio file is not stereo (has only one channel)."
            
            # Get additional file information
            ext = os.path.splitext(file_path)[1].lower()
            result['format'] = ext
            
            try:
                if ext == '.wav':
                    with wave.open(file_path, 'rb') as wav_file:
                        result['channels'] = wav_file.getnchannels()
                elif ext == '.mp3':
                    mp3_data = MP3(file_path)
                    result['channels'] = mp3_data.info.channels
            except Exception as e:
                result['info_error'] = str(e)
    
    except Exception as e:
        logging.error(f"Error comparing stereo channels: {str(e)}")
        traceback.print_exc()
        result['error'] = str(e)
    
    return result