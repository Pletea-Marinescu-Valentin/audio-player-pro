"""
Player controls module.
Provides UI components for controlling the audio player.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QSlider, QLabel, QFileDialog, QListWidget, 
    QComboBox, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
import os


class PlayerControls(QWidget):
    """
    Widget for controlling media playback.
    """
    # Define signals
    file_opened = pyqtSignal(str)
    visualization_update_requested = pyqtSignal()
    effect_applied = pyqtSignal()
    
    def __init__(self, media_player, playlist, parent=None):
        super().__init__(parent)
        self.media_player = media_player
        self.playlist = playlist
        self.current_audio_file = None
        self.shuffle = False
        self.repeat = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout()
        
        # Playlist section
        playlist_group = QGroupBox("Playlist")
        playlist_layout = QVBoxLayout()
        
        # Playlist widget
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_song)
        playlist_layout.addWidget(self.playlist_widget)
        
        # Playlist controls
        playlist_controls = QHBoxLayout()
        
        # Load button
        load_button = QPushButton("📂 Load")
        load_button.clicked.connect(self.open_audio_file)
        playlist_controls.addWidget(load_button)
        
        # Remove button
        remove_button = QPushButton("🗑️ Remove")
        remove_button.clicked.connect(self.remove_selected_song)
        playlist_controls.addWidget(remove_button)
        
        # Info button
        info_button = QPushButton("ℹ️ Info")
        info_button.clicked.connect(self.show_audio_info)
        playlist_controls.addWidget(info_button)
        
        # Compare channels button
        compare_button = QPushButton("🔊 Compare Channels")
        compare_button.clicked.connect(self.compare_stereo_channels)
        playlist_controls.addWidget(compare_button)
        
        playlist_layout.addLayout(playlist_controls)
        playlist_group.setLayout(playlist_layout)
        main_layout.addWidget(playlist_group)
        
        # Player controls section
        controls_group = QGroupBox("Player Controls")
        controls_layout = QVBoxLayout()
        
        # Playback controls
        playback_layout = QHBoxLayout()
        
        # Play/pause button
        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.toggle_play)
        playback_layout.addWidget(self.play_button)
        
        # Stop button
        stop_button = QPushButton("■ Stop")
        stop_button.clicked.connect(self.stop_audio)
        playback_layout.addWidget(stop_button)
        
        # Shuffle button
        self.shuffle_button = QPushButton("🔀 Shuffle: Off")
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        playback_layout.addWidget(self.shuffle_button)
        
        # Repeat button
        self.repeat_button = QPushButton("🔁 Repeat: Off")
        self.repeat_button.clicked.connect(self.toggle_repeat)
        playback_layout.addWidget(self.repeat_button)
        
        controls_layout.addLayout(playback_layout)
        
        # Progress slider
        progress_layout = QHBoxLayout()
        
        self.time_label = QLabel("0:00 / 0:00")
        progress_layout.addWidget(self.time_label)
        
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.set_position)
        progress_layout.addWidget(self.progress_slider)
        
        controls_layout.addLayout(progress_layout)
        
        # Volume and speed controls
        adjustment_layout = QHBoxLayout()
        
        # Volume slider
        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("🔊 Volume:"))
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # Default: 50%
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(self.volume_slider)
        
        adjustment_layout.addLayout(volume_layout)
        
        # Speed slider
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(QLabel("⏩ Playback Speed:"))
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)  # Default: 100% = normal speed
        self.speed_slider.valueChanged.connect(self.change_speed)
        speed_layout.addWidget(self.speed_slider)
        
        adjustment_layout.addLayout(speed_layout)
        
        controls_layout.addLayout(adjustment_layout)
        
        # Status label
        self.status_label = QLabel("Ready")
        controls_layout.addWidget(self.status_label)
        
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)
        
        # Effects section
        effects_group = QGroupBox("Audio Effects")
        effects_layout = QVBoxLayout()
        
        # Effects dropdown
        effects_layout.addWidget(QLabel("🎚️ Select Effect:"))
        
        self.effects_combo = QComboBox()
        self.effects_combo.addItems([
            "None",
            "FIR Low Pass",
            "FIR High Pass",
            "FIR Band Pass",
            "FIR Band Reject",
            "Bass Boost",
            "Reverb",
            "Echo",
            "Speed Up",
            "Tremolo",
            "Equalizer",
            "Echo + Speed Up"
        ])
        effects_layout.addWidget(self.effects_combo)
        
        # Apply effect button
        apply_effect_button = QPushButton("💾 Apply Effect")
        apply_effect_button.clicked.connect(self.apply_effect)
        effects_layout.addWidget(apply_effect_button)
        
        effects_group.setLayout(effects_layout)
        main_layout.addWidget(effects_group)
        
        # Update signal connections
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.stateChanged.connect(self.update_player_state)
        
        self.setLayout(main_layout)
        
        # Set tooltips for better usability
        load_button.setToolTip("Load an audio file into the playlist")
        remove_button.setToolTip("Remove the selected audio file from the playlist")
        info_button.setToolTip("View detailed information about the selected audio file")
        compare_button.setToolTip("Compare the stereo channels of the selected audio file")
        self.play_button.setToolTip("Play or pause the current audio file")
        stop_button.setToolTip("Stop playback and reset to the beginning")
        self.shuffle_button.setToolTip("Toggle shuffle mode for the playlist")
        self.repeat_button.setToolTip("Toggle repeat mode for the playlist")
        self.volume_slider.setToolTip("Adjust the playback volume")
        self.speed_slider.setToolTip("Adjust the playback speed")
        self.effects_combo.setToolTip("Select an audio effect to apply")
        apply_effect_button.setToolTip("Apply the selected audio effect to the current file")

    def open_audio_file(self):
        """
        Open a dialog to select an audio file and add it to the playlist.
        Updates both the internal playlist and the visual interface.
        Updates the current_audio_file variable to allow applying effects.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "", "Audio Files (*.mp3 *.wav)"
        )
        if file_path:
            self.current_audio_file = file_path
            
            # Check file format
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.mp3':
                print(f"MP3 file loaded: {file_path}")
            else:
                print(f"WAV file loaded: {file_path}")
                
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"ERROR: File {file_path} does not exist!")
                return
                
            media_content = QMediaContent(QUrl.fromLocalFile(file_path))
            self.playlist.addMedia(media_content)
            self.playlist_widget.addItem(os.path.basename(file_path))
            
            # Check if media_content is valid
            print(f"Media content valid: {not media_content.isNull()}")
            
            # Update visualizations when a new file is loaded
            self.file_opened.emit(file_path)
    
    def remove_selected_song(self):
        """
        Remove the selected song from the playlist and visual interface.
        """
        selected_item = self.playlist_widget.currentItem()
        if selected_item:
            row = self.playlist_widget.row(selected_item)
            self.playlist.removeMedia(row)
            self.playlist_widget.takeItem(row)
    
    def play_selected_song(self):
        """
        Play the selected song from the playlist.
        Activated when the user double-clicks an item in the list.
        Updates the current_audio_file variable to allow applying effects.
        """
        selected = self.playlist_widget.currentRow()
        if selected != -1:
            # Get the selected file name from playlist widget
            selected_file_name = self.playlist_widget.item(selected).text()
            
            # For regular files, we need to get the media URL
            url = self.playlist.media(selected).canonicalUrl()
            if url.isValid():
                self.current_audio_file = url.toLocalFile()
            
            # Check if file exists
            if not os.path.exists(self.current_audio_file):
                print(f"ERROR: File {self.current_audio_file} does not exist!")
                return
                
            print(f"Playing file: {self.current_audio_file}")
            
            # Check file format
            ext = os.path.splitext(self.current_audio_file)[1].lower()
            if ext == '.mp3':
                print("Playing MP3...")
            else:
                print("Playing WAV...")
                
            # Set index and start playback
            self.playlist.setCurrentIndex(selected)
            self.media_player.play()
            
            # Display player state
            print(f"Player state after play: {self.media_player.state()}")
            if self.media_player.state() != QMediaPlayer.PlayingState:
                # If the player is not in playing state, display the error
                error = self.media_player.error()
                print(f"Media player error: {error}")
                
            # Update visualizations for current file
            self.file_opened.emit(self.current_audio_file)
    
    def show_audio_info(self):
        """
        Show a dialog with detailed information about the current audio file.
        """
        from .dialogs import AudioInfoDialog
        from ..core.file_handler import get_audio_info
        
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            # Get audio information
            audio_info = get_audio_info(self.current_audio_file)
            
            # Show info dialog
            dialog = AudioInfoDialog(audio_info, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "No File Selected", 
                               "No audio file is selected or the file does not exist.")
    
    def compare_stereo_channels(self):
        """
        Compare stereo channels of the current audio file.
        Display information about differences between channels.
        """
        from .dialogs import ChannelComparisonDialog
        from ..core.file_handler import compare_stereo_channels
        
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            # Compare stereo channels
            comparison_results = compare_stereo_channels(self.current_audio_file)
            
            # Show comparison dialog
            dialog = ChannelComparisonDialog(comparison_results, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "No File Selected", 
                               "No audio file is selected or the file does not exist.")
    
    def toggle_play(self):
        """
        Toggle between play and pause states.
        If the player is running, pause it; if paused, resume playback.
        """
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def stop_audio(self):
        """Stop audio playback completely and reset position to beginning."""
        self.media_player.stop()
    
    def toggle_shuffle(self):
        """
        Toggle between sequential and random playback modes.
        Update the global variable and playlist setting.
        """
        self.shuffle = not self.shuffle
        
        # Set the appropriate mode considering both shuffle and repeat
        if self.shuffle:
            self.shuffle_button.setText("🔀 Shuffle: On")
            mode = QMediaPlaylist.Random
        else:
            self.shuffle_button.setText("🔀 Shuffle: Off")
            mode = QMediaPlaylist.Sequential
            
        if self.repeat:
            mode = QMediaPlaylist.Loop if not self.shuffle else QMediaPlaylist.Random
            
        self.playlist.setPlaybackMode(mode)
    
    def toggle_repeat(self):
        """
        Toggle between single and repeat playback modes.
        Update the global variable and playlist setting.
        """
        self.repeat = not self.repeat
        
        # Set the appropriate mode considering both shuffle and repeat
        if self.repeat:
            self.repeat_button.setText("🔁 Repeat: On")
            mode = QMediaPlaylist.Loop
        else:
            self.repeat_button.setText("🔁 Repeat: Off")
            mode = QMediaPlaylist.Sequential
            
        if self.shuffle:
            mode = QMediaPlaylist.Random
            
        self.playlist.setPlaybackMode(mode)
    
    def change_volume(self, value):
        """
        Change playback volume based on slider value.
        Convert value from 0-100 range to 0.0-1.0 range.
        
        Parameters:
        -----------
        value : int
            Volume value (0-100)
        """
        self.media_player.setVolume(value)
    
    def change_speed(self, value):
        """
        Change playback speed based on slider value.
        Value 100 represents normal speed.
        
        Parameters:
        -----------
        value : int
            Speed value (50-200, where 100 is 1x)
        """
        speed = value / 100.0
        self.media_player.setPlaybackRate(speed)
    
    def update_position(self, position):
        """
        Update progress slider position based on current playback position.
        
        Parameters:
        -----------
        position : int
            Current position in milliseconds
        """
        # Prevent slider update loop by ignoring if slider is being dragged
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
            
        # Update time label
        duration = self.media_player.duration()
        if duration > 0:
            self.update_time_label(position, duration)
    
    def update_duration(self, duration):
        """
        Update progress slider range based on media duration.
        
        Parameters:
        -----------
        duration : int
            Media duration in milliseconds
        """
        self.progress_slider.setRange(0, duration)
        
        # Update time label
        position = self.media_player.position()
        self.update_time_label(position, duration)
    
    def update_time_label(self, position, duration):
        """
        Update the time label with formatted time information.
        
        Parameters:
        -----------
        position : int
            Current position in milliseconds
        duration : int
            Media duration in milliseconds
        """
        position_sec = position // 1000
        position_min = position_sec // 60
        position_sec %= 60
        
        duration_sec = duration // 1000
        duration_min = duration_sec // 60
        duration_sec %= 60
        
        self.time_label.setText(f"{position_min}:{position_sec:02d} / {duration_min}:{duration_sec:02d}")
    
    def set_position(self, position):
        """
        Set playback position when user manually moves the progress slider.
        
        Parameters:
        -----------
        position : int
            Desired position in milliseconds
        """
        self.media_player.setPosition(position)
    
    def update_player_state(self, state):
        """
        Update UI based on player state.
        
        Parameters:
        -----------
        state : QMediaPlayer.State
            Current state of the media player
        """
        if state == QMediaPlayer.PlayingState:
            self.play_button.setText("⏸ Pause")
            self.status_label.setText("Playing")
        elif state == QMediaPlayer.PausedState:
            self.play_button.setText("▶ Play")
            self.status_label.setText("Paused")
        elif state == QMediaPlayer.StoppedState:
            self.play_button.setText("▶ Play")
            self.status_label.setText("Stopped")
    
    def apply_effect(self):
        """
        Apply the selected effect to the current audio file and save the result.
        """
        from .dialogs import EffectParametersDialog
        
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            QMessageBox.warning(self, "No File Selected", 
                               "No audio file is selected or the file does not exist.")
            return
            
        # Determine file extension
        ext = os.path.splitext(self.current_audio_file)[1].lower()
        
        # If the file is MP3, show a message and interrupt the process
        if ext == '.mp3':
            QMessageBox.warning(
                self, 
                "Unsupported Operation", 
                "Applying effects to MP3 files is not supported.\n\n"
                "To apply effects, first convert the file to WAV format.", 
                QMessageBox.Ok
            )
            return
            
        # Get selected effect
        effect = self.effects_combo.currentText()
        if effect == "None":
            QMessageBox.information(self, "No Effect Selected", 
                                  "Please select an effect to apply.")
            return
            
        # Show effect parameters dialog
        dialog = EffectParametersDialog(effect, None, self)
        if dialog.exec_() != EffectParametersDialog.Accepted:
            return
            
        # Get parameters from dialog
        effect_params = dialog.get_parameters()
        
        # Propose output file name with prefix "modified_"
        suggested_name = "modified_" + os.path.basename(self.current_audio_file)
        
        # Get output path
        output_file, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Modified Audio File", 
            suggested_name, 
            "Audio Files (*.wav)"  # Restrict to WAV
        )
        
        if not output_file:
            return
            
        # Process the file
        from ..core.audio_processor import process_audio_file
        from ..effects.filters import (
            fir_low_pass, fir_high_pass, fir_band_pass, fir_band_reject
        )
        from ..effects.basic_effects import (
            apply_bass_boost, apply_reverb, apply_echo, apply_speed_up, apply_tremolo
        )
        from ..effects.advanced_effects import (
            apply_equalizer, apply_echo_speed_combo
        )
        
        # Select the appropriate effect function
        effect_func = None
        if effect == "FIR Low Pass":
            effect_func = fir_low_pass
        elif effect == "FIR High Pass":
            effect_func = fir_high_pass
        elif effect == "FIR Band Pass":
            effect_func = fir_band_pass
        elif effect == "FIR Band Reject":
            effect_func = fir_band_reject
        elif effect == "Bass Boost":
            effect_func = apply_bass_boost
        elif effect == "Reverb":
            effect_func = apply_reverb
        elif effect == "Echo":
            effect_func = apply_echo
        elif effect == "Speed Up":
            effect_func = apply_speed_up
        elif effect == "Tremolo":
            effect_func = apply_tremolo
        elif effect == "Equalizer":
            effect_func = apply_equalizer
        elif effect == "Echo + Speed Up":
            effect_func = apply_echo_speed_combo
        
        if effect_func:
            # Apply the effect and save
            success = process_audio_file(self.current_audio_file, output_file, effect_func, effect_params)
            
            if success:
                QMessageBox.information(
                    self, 
                    "Processing Complete", 
                    f"Audio file has been processed and saved to:\n{output_file}"
                )
                
                # Add to playlist
                media_content = QMediaContent(QUrl.fromLocalFile(output_file))
                self.playlist.addMedia(media_content)
                self.playlist_widget.addItem(os.path.basename(output_file))
                
                # Notify that an effect was applied
                self.effect_applied.emit()
            else:
                QMessageBox.warning(
                    self, 
                    "Processing Failed", 
                    "An error occurred while processing the audio file."
                )