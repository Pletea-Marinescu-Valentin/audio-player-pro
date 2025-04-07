"""
Main window module.
Provides the main application window and top-level UI components.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist
import os

from .player_controls import PlayerControls
from .visualizations import SpectrogramCanvas, FrequencySpectrumCanvas, WaveformCanvas
from ..core.file_handler import extract_audio_data
from ..core.signal_generator import generate_test_signal
from .dialogs import GenerateSignalDialog


class MainWindow(QMainWindow):
    """
    Main application window.
    Provides the top-level UI components and organization.
    """
    def __init__(self):
        super().__init__()
        
        # Initialize media components
        self.media_player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.media_player.setPlaylist(self.playlist)
        
        # Current file tracking
        self.current_audio_file = None
        
        # Set up the user interface
        self.init_ui()
        
        # Connect signals
        self.connect_signals()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("Audio Player Pro")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main tab widget
        self.tab_widget = QTabWidget()
        
        # Create the player tab
        self.player_tab = QWidget()
        self.create_player_tab()
        self.tab_widget.addTab(self.player_tab, "Player")
        
        # Create the visualizations tab
        self.visualizations_tab = QWidget()
        self.create_visualizations_tab()
        self.tab_widget.addTab(self.visualizations_tab, "Visualizations")
        
        # Set central widget
        self.setCentralWidget(self.tab_widget)
        
    def create_player_tab(self):
        """Create and populate the player tab."""
        layout = QVBoxLayout()
        
        # Add player controls
        self.player_controls = PlayerControls(self.media_player, self.playlist)
        layout.addWidget(self.player_controls)
        
        # Add a simple waveform view
        self.waveform_canvas = WaveformCanvas()
        layout.addWidget(self.waveform_canvas)
        
        # Add signal generation button
        generate_button = QPushButton("🎵 Generate Test Signal")
        generate_button.clicked.connect(self.show_generate_dialog)
        layout.addWidget(generate_button)
        
        self.player_tab.setLayout(layout)
        
    def create_visualizations_tab(self):
        """Create and populate the visualizations tab."""
        layout = QVBoxLayout()
        
        # Create a splitter for resizable visualizations
        splitter = QSplitter(Qt.Vertical)
        
        # Add spectrogram
        spectrogram_widget = QWidget()
        spectrogram_layout = QVBoxLayout()
        spectrogram_layout.addWidget(QLabel("Spectrogram:"))
        
        self.spectrogram_canvas = SpectrogramCanvas()
        spectrogram_layout.addWidget(self.spectrogram_canvas)
        
        # Add spectrogram explanation
        spectrogram_info = QLabel(
            "The spectrogram shows the distribution of frequencies over time. "
            "Brighter colors represent higher amplitudes. "
            "Low frequencies (bass) are at the bottom, high frequencies (treble) at the top."
        )
        spectrogram_info.setWordWrap(True)
        spectrogram_layout.addWidget(spectrogram_info)
        
        spectrogram_widget.setLayout(spectrogram_layout)
        splitter.addWidget(spectrogram_widget)
        
        # Add frequency spectrum
        spectrum_widget = QWidget()
        spectrum_layout = QVBoxLayout()
        spectrum_layout.addWidget(QLabel("Frequency Spectrum:"))
        
        self.frequency_spectrum_canvas = FrequencySpectrumCanvas()
        spectrum_layout.addWidget(self.frequency_spectrum_canvas)
        
        # Add spectrum explanation
        spectrum_info = QLabel(
            "The frequency spectrum shows the amplitude of the signal at different frequencies. "
            "Low frequencies (bass) are on the left, high frequencies (treble) on the right."
        )
        spectrum_info.setWordWrap(True)
        spectrum_layout.addWidget(spectrum_info)
        
        spectrum_widget.setLayout(spectrum_layout)
        splitter.addWidget(spectrum_widget)
        
        # Add update button
        update_button = QPushButton("🔄 Update Visualizations")
        update_button.clicked.connect(self.update_visualizations)
        
        # Add to main layout
        layout.addWidget(splitter)
        layout.addWidget(update_button)
        
        self.visualizations_tab.setLayout(layout)
        
    def connect_signals(self):
        """Connect signals to slots."""
        # Connect player controls signals
        self.player_controls.file_opened.connect(self.on_file_opened)
        self.player_controls.visualization_update_requested.connect(self.update_visualizations)
        self.player_controls.effect_applied.connect(self.update_visualizations)
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def on_file_opened(self, file_path):
        """
        Handle file opened signal.
        
        Parameters:
        -----------
        file_path : str
            Path to the opened audio file
        """
        self.current_audio_file = file_path
        self.update_visualizations()
        
    def on_tab_changed(self, index):
        """
        Handle tab changed signal.
        
        Parameters:
        -----------
        index : int
            Index of the selected tab
        """
        # Update visualizations when changing to visualizations tab
        if index == 1:  # Visualizations tab
            self.update_visualizations()
            
    def update_visualizations(self):
        """Update all visualizations with current audio file data."""
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            print(f"Updating visualizations for: {self.current_audio_file}")
            
            try:
                # Extract audio data for visualization (using mono for visualizations)
                samples, sample_rate = extract_audio_data(self.current_audio_file, keep_stereo=False)
                
                if samples is not None and sample_rate is not None:
                    print(f"Generating visualizations: {len(samples)} samples at {sample_rate}Hz")
                    
                    # Update all visualizations
                    self.waveform_canvas.plot_waveform(samples, sample_rate)
                    self.spectrogram_canvas.plot_spectrogram(samples, sample_rate)
                    self.frequency_spectrum_canvas.plot_frequency_spectrum(samples, sample_rate)
                else:
                    print("Could not get audio data for visualizations")
            except Exception as e:
                print(f"Error updating visualizations: {e}")
                import traceback
                traceback.print_exc()
        else:
            if not self.current_audio_file:
                print("No current audio file for visualization")
            elif not os.path.exists(self.current_audio_file):
                print(f"Current audio file does not exist: {self.current_audio_file}")
                
    def show_generate_dialog(self):
        """Show dialog for generating test signals."""
        dialog = GenerateSignalDialog(self)
        if dialog.exec_() == GenerateSignalDialog.Accepted:
            params = dialog.get_parameters()
            
            # Generate signal based on type
            signal_type = params['signal_type']
            
            if signal_type == "Sine Wave":
                filepath = generate_test_signal(
                    params['frequency'],
                    params['duration'],
                    params['amplitude']
                )
            elif signal_type == "Square Wave":
                from ..core.signal_generator import generate_square_wave
                samples = generate_square_wave(
                    params['frequency'],
                    params['duration'],
                    params['amplitude']
                )
                # Save the signal
                from ..core.file_handler import save_audio_file
                filepath = f"test_signals/square_{params['frequency']}Hz_{params['duration']}s.wav"
                save_audio_file(samples, 44100, filepath)
            elif signal_type == "Sawtooth Wave":
                from ..core.signal_generator import generate_sawtooth_wave
                samples = generate_sawtooth_wave(
                    params['frequency'],
                    params['duration'],
                    params['amplitude']
                )
                # Save the signal
                from ..core.file_handler import save_audio_file
                filepath = f"test_signals/sawtooth_{params['frequency']}Hz_{params['duration']}s.wav"
                save_audio_file(samples, 44100, filepath)
            elif "Noise" in signal_type:
                noise_type = signal_type.split()[0].lower()  # Extract "white" or "pink"
                from ..core.signal_generator import generate_noise
                samples = generate_noise(
                    params['duration'],
                    params['amplitude'],
                    44100,
                    noise_type
                )
                # Save the signal
                from ..core.file_handler import save_audio_file
                filepath = f"test_signals/{noise_type}_noise_{params['duration']}s.wav"
                save_audio_file(samples, 44100, filepath)
            
            # Add to playlist
            media_content = QMediaContent(QUrl.fromLocalFile(os.path.abspath(filepath)))
            self.playlist.addMedia(media_content)
            self.player_controls.playlist_widget.addItem(os.path.basename(filepath))
            
            # Update current file
            self.current_audio_file = filepath
            self.update_visualizations()