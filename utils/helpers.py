"""
Helper functions for the audio player application.
"""

import os
import time
import datetime


def format_time(milliseconds):
    """
    Format time in milliseconds to a human-readable string.
    
    Parameters:
    -----------
    milliseconds : int
        Time in milliseconds
        
    Returns:
    --------
    str
        Formatted time string (MM:SS)
    """
    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds %= 60
    return f"{minutes}:{seconds:02d}"


def format_file_size(size_bytes):
    """
    Format file size in bytes to a human-readable string.
    
    Parameters:
    -----------
    size_bytes : int
        File size in bytes
        
    Returns:
    --------
    str
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def ensure_directory_exists(path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Parameters:
    -----------
    path : str
        Directory path
    """
    if not os.path.exists(path):
        os.makedirs(path)


def generate_timestamp():
    """
    Generate a timestamp string for use in filenames.
    
    Returns:
    --------
    str
        Timestamp string
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def is_audio_file(file_path):
    """
    Check if a file is an audio file based on its extension.
    
    Parameters:
    -----------
    file_path : str
        Path to the file
        
    Returns:
    --------
    bool
        True if the file is an audio file, False otherwise
    """
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a']