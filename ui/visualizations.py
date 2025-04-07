"""
Audio visualization components.
Provides spectrograms and frequency spectrum visualization tools.
"""

import numpy as np
import traceback
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy


class SpectrogramCanvas(FigureCanvas):
    """
    Matplotlib canvas for displaying a spectrogram.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.axes.text(0.5, 0.5, 'No audio file loaded', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=self.axes.transAxes, fontsize=14)
        self.draw()
        
    def plot_spectrogram(self, samples, sample_rate):
        """
        Generate and display a spectrogram for audio data.
        
        Parameters:
        -----------
        samples : numpy.ndarray
            Audio samples
        sample_rate : int
            Sample rate of the signal
        """
        if samples is None or len(samples) == 0:
            print("No data for spectrogram")
            self.axes.clear()
            self.axes.text(0.5, 0.5, 'No audio data', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.axes.transAxes, fontsize=14)
            self.draw()
            return
            
        print(f"Generating spectrogram for {len(samples)} samples at {sample_rate}Hz")
        
        self.axes.clear()
        
        try:
            self.axes.specgram(samples, NFFT=2048, Fs=sample_rate, 
                          noverlap=1024, cmap='viridis', 
                          mode='magnitude', scale='dB')
            self.axes.set_ylabel('Frequency [Hz]')
            self.axes.set_xlabel('Time [sec]')
            self.axes.set_title('Spectrogram')
            
            self.fig.tight_layout()
            
            self.draw()
            print("Spectrogram generated successfully")
        except Exception as e:
            print(f"Error generating spectrogram: {e}")
            traceback.print_exc()
            
            self.axes.clear()
            self.axes.text(0.5, 0.5, f'Error: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.axes.transAxes, fontsize=10, color='red')
            self.draw()


class FrequencySpectrumCanvas(FigureCanvas):
    """
    Matplotlib canvas for displaying a frequency spectrum.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.axes.text(0.5, 0.5, 'No audio file loaded', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=self.axes.transAxes, fontsize=14)
        self.draw()
        
    def plot_frequency_spectrum(self, samples, sample_rate):
        """
        Generate and display a frequency spectrum for audio data.
        
        Parameters:
        -----------
        samples : numpy.ndarray
            Audio samples
        sample_rate : int
            Sample rate of the signal
        """
        if samples is None or len(samples) == 0:
            print("No data for frequency spectrum")
            self.axes.clear()
            self.axes.text(0.5, 0.5, 'No audio data', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.axes.transAxes, fontsize=14)
            self.draw()
            return
            
        print(f"Generating frequency spectrum for {len(samples)} samples at {sample_rate}Hz")
        
        self.axes.clear()
        
        try:
            # Calculate FFT
            # Use a Hamming window to reduce artifacts
            windowed_samples = samples * np.hamming(len(samples))
            
            # Take only a portion of samples for faster and clearer FFT
            # (maximum 100,000 samples or all if fewer)
            max_samples = min(len(windowed_samples), 100000)
            segment = windowed_samples[:max_samples]
            
            # Apply FFT
            fft_result = np.fft.rfft(segment)
            # Use rfft to get only the positive part of the spectrum (more efficient)
            freqs = np.fft.rfftfreq(len(segment), d=1/sample_rate)
            
            # Calculate magnitude in dB for better visualization
            magnitude = np.abs(fft_result)
            magnitude_db = 20 * np.log10(magnitude + 1e-10)  # Add a small value to avoid log(0)
            
            # Display frequency spectrum
            self.axes.plot(freqs, magnitude_db)
            self.axes.set_xlabel('Frequency [Hz]')
            self.axes.set_ylabel('Magnitude [dB]')
            self.axes.set_title('Frequency Spectrum')
            
            # Set axis limits for better visualization
            self.axes.set_xlim([0, min(20000, sample_rate/2)])  # Limit to 20kHz or Nyquist
            
            # Add a grid for easier reading
            self.axes.grid(True, alpha=0.3)
            
            # Improve appearance
            self.fig.tight_layout()
            
            # Update canvas
            self.draw()
            print("Frequency spectrum generated successfully")
        except Exception as e:
            print(f"Error generating frequency spectrum: {e}")
            traceback.print_exc()
            
            # Display error message on graph
            self.axes.clear()
            self.axes.text(0.5, 0.5, f'Error: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.axes.transAxes, fontsize=10, color='red')
            self.draw()


class WaveformCanvas(FigureCanvas):
    """
    Matplotlib canvas for displaying a waveform.
    """
    def __init__(self, parent=None, width=5, height=2, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.axes.text(0.5, 0.5, 'No audio file loaded', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=self.axes.transAxes, fontsize=14)
        self.draw()
    
    def plot_waveform(self, samples, sample_rate):
        """
        Generate and display a waveform for audio data.
        
        Parameters:
        -----------
        samples : numpy.ndarray
            Audio samples
        sample_rate : int
            Sample rate of the signal
        """
        if samples is None or len(samples) == 0:
            print("No data for waveform")
            self.axes.clear()
            self.axes.text(0.5, 0.5, 'No audio data', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.axes.transAxes, fontsize=14)
            self.draw()
            return
        
        print(f"Generating waveform for {len(samples)} samples at {sample_rate}Hz")
        
        self.axes.clear()
        
        try:
            # Calculate time array
            time = np.arange(len(samples)) / sample_rate
            
            # For large arrays, downsample for better performance
            if len(samples) > 1000000:
                downsample_factor = len(samples) // 1000000 + 1
                samples = samples[::downsample_factor]
                time = time[::downsample_factor]
                print(f"Downsampled to {len(samples)} points for display")
            
            # Plot waveform
            self.axes.plot(time, samples, linewidth=0.5)
            self.axes.set_ylabel('Amplitude')
            self.axes.set_xlabel('Time [sec]')
            self.axes.set_title('Waveform')
            
            # Add grid for easier reading
            self.axes.grid(True, alpha=0.3)
            
            # Set y-axis limits to show full range of int16
            self.axes.set_ylim([-32768, 32767])
            
            # Improve appearance
            self.fig.tight_layout()
            
            # Update canvas
            self.draw()
            print("Waveform generated successfully")
        except Exception as e:
            print(f"Error generating waveform: {e}")
            traceback.print_exc()
            
            # Display error message on graph
            self.axes.clear()
            self.axes.text(0.5, 0.5, f'Error: {str(e)}', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=self.axes.transAxes, fontsize=10, color='red')
            self.draw()