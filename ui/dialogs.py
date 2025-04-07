"""
Dialog boxes module.
Provides various dialog windows for the audio player application.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QDoubleSpinBox, QSpinBox, QComboBox,
    QDialogButtonBox, QGroupBox, QSlider
)
from PyQt5.QtCore import Qt


class AudioInfoDialog(QDialog):
    """
    Dialog for displaying detailed information about an audio file.
    """
    def __init__(self, audio_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio File Information")
        self.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.populate_table(audio_info)
        
        layout.addWidget(self.table)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def populate_table(self, info):
        """
        Populate the table with audio information.
        
        Parameters:
        -----------
        info : dict
            Dictionary with information about the audio file
        """
        rows = []
        for key, value in info.items():
            if key != 'metadata':  # Process metadata separately
                rows.append((key, str(value)))
        
        if 'metadata' in info and info['metadata'] and info['metadata'] != "No metadata":
            if isinstance(info['metadata'], dict):
                for meta_key, meta_value in info['metadata'].items():
                    rows.append((f"Metadata: {meta_key}", str(meta_value)))
            else:
                rows.append(("Metadata", str(info['metadata'])))
                
        self.table.setRowCount(len(rows))
        for i, (key, value) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(key))
            self.table.setItem(i, 1, QTableWidgetItem(value))


class GenerateSignalDialog(QDialog):
    """
    Dialog for generating test signals.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Test Signal")
        self.setMinimumWidth(300)
        
        self.main_layout = QVBoxLayout()
        
        # Signal type selection
        self.signal_type_group = QGroupBox("Signal Type")
        signal_type_layout = QVBoxLayout()
        
        self.signal_type_combo = QComboBox()
        self.signal_type_combo.addItems(["Sine Wave", "Square Wave", "Sawtooth Wave", "White Noise", "Pink Noise"])
        self.signal_type_combo.currentIndexChanged.connect(self.update_parameter_visibility)
        signal_type_layout.addWidget(self.signal_type_combo)
        
        self.signal_type_group.setLayout(signal_type_layout)
        self.main_layout.addWidget(self.signal_type_group)
        
        # Parameters section
        self.params_group = QGroupBox("Signal Parameters")
        self.params_layout = QFormLayout()
        
        # Frequency
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(20, 20000)  # Between 20Hz and 20kHz
        self.freq_spin.setValue(440)         # Initial value: note A
        self.params_layout.addRow("Frequency (Hz):", self.freq_spin)
        
        # Duration
        self.dur_spin = QDoubleSpinBox()
        self.dur_spin.setRange(0.1, 30.0)    # Between 0.1 and 30 seconds
        self.dur_spin.setValue(2.0)          # Initial value: 2 seconds
        self.dur_spin.setSingleStep(0.1)
        self.params_layout.addRow("Duration (sec):", self.dur_spin)
        
        # Amplitude
        self.amp_spin = QDoubleSpinBox()
        self.amp_spin.setRange(0.0, 1.0)     # Between 0.0 and 1.0
        self.amp_spin.setValue(0.8)          # Initial value: 0.8
        self.amp_spin.setSingleStep(0.1)
        self.params_layout.addRow("Amplitude (0-1):", self.amp_spin)
        
        self.params_group.setLayout(self.params_layout)
        self.main_layout.addWidget(self.params_group)
        
        # Button section
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.accept)
        self.generate_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.generate_button)
        
        self.main_layout.addLayout(button_layout)
        
        self.setLayout(self.main_layout)
        
        # Initial update of parameter visibility
        self.update_parameter_visibility()
    
    def update_parameter_visibility(self):
        """Update parameter visibility based on signal type"""
        signal_type = self.signal_type_combo.currentText()
        
        # Show/hide frequency control for noise types
        is_noise = "Noise" in signal_type
        self.freq_spin.setEnabled(not is_noise)
        
    def get_parameters(self):
        """
        Get parameter values from dialog.
        
        Returns:
        --------
        dict
            Dictionary with parameter values
        """
        return {
            'signal_type': self.signal_type_combo.currentText(),
            'frequency': self.freq_spin.value(),
            'duration': self.dur_spin.value(),
            'amplitude': self.amp_spin.value()
        }


class EffectParametersDialog(QDialog):
    """
    Dialog for configuring effect parameters.
    """
    def __init__(self, effect_name, effect_params=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{effect_name} Parameters")
        self.setMinimumWidth(350)
        
        self.effect_name = effect_name
        self.effect_params = effect_params if effect_params is not None else {}
        
        layout = QVBoxLayout()
        
        # Create parameter controls based on effect type
        self.param_controls = {}
        
        form_layout = QFormLayout()
        
        if effect_name == "FIR Low Pass" or effect_name == "FIR High Pass":
            # Cutoff frequency
            cutoff_spin = QSpinBox()
            cutoff_spin.setRange(20, 20000)
            cutoff_spin.setValue(self.effect_params.get('cutoff_freq', 1000))
            cutoff_spin.setSingleStep(100)
            form_layout.addRow("Cutoff Frequency (Hz):", cutoff_spin)
            self.param_controls['cutoff_freq'] = cutoff_spin
            
            # Filter order
            order_spin = QSpinBox()
            order_spin.setRange(3, 301)
            order_spin.setValue(self.effect_params.get('N', 101))
            order_spin.setSingleStep(2)  # Ensure odd values
            form_layout.addRow("Filter Order:", order_spin)
            self.param_controls['N'] = order_spin
            
        elif effect_name == "FIR Band Pass" or effect_name == "FIR Band Reject":
            # Low cutoff frequency
            low_cutoff_spin = QSpinBox()
            low_cutoff_spin.setRange(20, 20000)
            low_cutoff_spin.setValue(self.effect_params.get('low_cutoff', 500))
            low_cutoff_spin.setSingleStep(100)
            form_layout.addRow("Low Cutoff (Hz):", low_cutoff_spin)
            self.param_controls['low_cutoff'] = low_cutoff_spin
            
            # High cutoff frequency
            high_cutoff_spin = QSpinBox()
            high_cutoff_spin.setRange(20, 20000)
            high_cutoff_spin.setValue(self.effect_params.get('high_cutoff', 2000))
            high_cutoff_spin.setSingleStep(100)
            form_layout.addRow("High Cutoff (Hz):", high_cutoff_spin)
            self.param_controls['high_cutoff'] = high_cutoff_spin
            
            # Filter order
            order_low_spin = QSpinBox()
            order_low_spin.setRange(3, 301)
            order_low_spin.setValue(self.effect_params.get('N_low', 101))
            order_low_spin.setSingleStep(2)  # Ensure odd values
            form_layout.addRow("Low Filter Order:", order_low_spin)
            self.param_controls['N_low'] = order_low_spin
            
            order_high_spin = QSpinBox()
            order_high_spin.setRange(3, 301)
            order_high_spin.setValue(self.effect_params.get('N_high', 101))
            order_high_spin.setSingleStep(2)  # Ensure odd values
            form_layout.addRow("High Filter Order:", order_high_spin)
            self.param_controls['N_high'] = order_high_spin
            
        elif effect_name == "Bass Boost":
            # Boost factor
            boost_spin = QDoubleSpinBox()
            boost_spin.setRange(1.0, 5.0)
            boost_spin.setValue(self.effect_params.get('boost_factor', 2.5))
            boost_spin.setSingleStep(0.1)
            form_layout.addRow("Boost Factor:", boost_spin)
            self.param_controls['boost_factor'] = boost_spin
            
            # Cutoff frequency
            cutoff_spin = QSpinBox()
            cutoff_spin.setRange(20, 500)
            cutoff_spin.setValue(self.effect_params.get('cutoff_freq', 150))
            cutoff_spin.setSingleStep(10)
            form_layout.addRow("Cutoff Frequency (Hz):", cutoff_spin)
            self.param_controls['cutoff_freq'] = cutoff_spin
            
        elif effect_name == "Reverb":
            # Room size
            room_size_spin = QDoubleSpinBox()
            room_size_spin.setRange(0.1, 1.0)
            room_size_spin.setValue(self.effect_params.get('room_size', 0.75))
            room_size_spin.setSingleStep(0.05)
            form_layout.addRow("Room Size:", room_size_spin)
            self.param_controls['room_size'] = room_size_spin
            
            # Damping
            damping_spin = QDoubleSpinBox()
            damping_spin.setRange(0.0, 1.0)
            damping_spin.setValue(self.effect_params.get('damping', 0.5))
            damping_spin.setSingleStep(0.05)
            form_layout.addRow("Damping:", damping_spin)
            self.param_controls['damping'] = damping_spin
            
            # Wet level
            wet_level_spin = QDoubleSpinBox()
            wet_level_spin.setRange(0.0, 1.0)
            wet_level_spin.setValue(self.effect_params.get('wet_level', 0.3))
            wet_level_spin.setSingleStep(0.05)
            form_layout.addRow("Wet Level:", wet_level_spin)
            self.param_controls['wet_level'] = wet_level_spin
            
        elif effect_name == "Echo":
            # First delay
            delay1_spin = QSpinBox()
            delay1_spin.setRange(50, 1000)
            delays = self.effect_params.get('delays_ms', [200, 400])
            delay1_spin.setValue(delays[0] if len(delays) > 0 else 200)
            delay1_spin.setSingleStep(10)
            form_layout.addRow("Delay 1 (ms):", delay1_spin)
            self.param_controls['delay1'] = delay1_spin
            
            # First decay
            decay1_spin = QDoubleSpinBox()
            decay1_spin.setRange(0.0, 1.0)
            decays = self.effect_params.get('decays', [0.5, 0.25])
            decay1_spin.setValue(decays[0] if len(decays) > 0 else 0.5)
            decay1_spin.setSingleStep(0.05)
            form_layout.addRow("Decay 1:", decay1_spin)
            self.param_controls['decay1'] = decay1_spin
            
            # Second delay
            delay2_spin = QSpinBox()
            delay2_spin.setRange(50, 1000)
            delay2_spin.setValue(delays[1] if len(delays) > 1 else 400)
            delay2_spin.setSingleStep(10)
            form_layout.addRow("Delay 2 (ms):", delay2_spin)
            self.param_controls['delay2'] = delay2_spin
            
            # Second decay
            decay2_spin = QDoubleSpinBox()
            decay2_spin.setRange(0.0, 1.0)
            decay2_spin.setValue(decays[1] if len(decays) > 1 else 0.25)
            decay2_spin.setSingleStep(0.05)
            form_layout.addRow("Decay 2:", decay2_spin)
            self.param_controls['decay2'] = decay2_spin
            
        elif effect_name == "Speed Up":
            # Speed factor
            speed_spin = QDoubleSpinBox()
            speed_spin.setRange(0.5, 3.0)
            speed_spin.setValue(self.effect_params.get('speed_factor', 1.2))
            speed_spin.setSingleStep(0.1)
            form_layout.addRow("Speed Factor:", speed_spin)
            self.param_controls['speed_factor'] = speed_spin
            
            # Preserve pitch
            preserve_pitch_combo = QComboBox()
            preserve_pitch_combo.addItems(["Yes", "No"])
            preserve_pitch_index = 0 if self.effect_params.get('preserve_pitch', True) else 1
            preserve_pitch_combo.setCurrentIndex(preserve_pitch_index)
            form_layout.addRow("Preserve Pitch:", preserve_pitch_combo)
            self.param_controls['preserve_pitch'] = preserve_pitch_combo
            
        elif effect_name == "Tremolo":
            # Depth
            depth_spin = QDoubleSpinBox()
            depth_spin.setRange(0.0, 1.0)
            depth_spin.setValue(self.effect_params.get('depth', 0.5))
            depth_spin.setSingleStep(0.05)
            form_layout.addRow("Depth:", depth_spin)
            self.param_controls['depth'] = depth_spin
            
            # Rate
            rate_spin = QDoubleSpinBox()
            rate_spin.setRange(0.5, 20.0)
            rate_spin.setValue(self.effect_params.get('rate', 5.0))
            rate_spin.setSingleStep(0.5)
            form_layout.addRow("Rate (Hz):", rate_spin)
            self.param_controls['rate'] = rate_spin
                        
        elif effect_name == "Equalizer":
            # Create sliders for each frequency band
            bands = ["Bass (20-250Hz)", "Low-Mid (250-500Hz)", "Mid (500-2000Hz)", 
                    "High-Mid (2000-5000Hz)", "Treble (5000-20000Hz)"]
            
            gains = self.effect_params.get('gains', [1.0, 1.0, 1.0, 1.0, 1.0])
            
            # Use a separate layout for equalizer sliders
            eq_layout = QHBoxLayout()
            
            for i, band in enumerate(bands):
                # Create a vertical layout for each band
                band_layout = QVBoxLayout()
                
                # Add label
                band_label = QLabel(band)
                band_label.setAlignment(Qt.AlignCenter)
                band_layout.addWidget(band_label)
                
                # Create slider
                slider = QSlider(Qt.Vertical)
                slider.setRange(10, 300)  # 0.1x to 3.0x
                slider.setValue(int(gains[i] * 100) if i < len(gains) else 100)
                slider.setTickPosition(QSlider.TicksBothSides)
                slider.setTickInterval(50)
                band_layout.addWidget(slider)
                
                # Add value label
                value_label = QLabel(f"{slider.value() / 100:.1f}x")
                value_label.setAlignment(Qt.AlignCenter)
                band_layout.addWidget(value_label)
                
                # Connect slider to update label
                slider.valueChanged.connect(
                    lambda value, label=value_label: label.setText(f"{value / 100:.1f}x")
                )
                
                # Add to layout
                eq_layout.addLayout(band_layout)
                self.param_controls[f'gain_{i}'] = slider
            
            # Replace form layout with equalizer layout
            layout.addLayout(eq_layout)
            form_layout = None
        
        # Add form layout to main layout if it exists
        if form_layout:
            layout.addLayout(form_layout)
            
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_parameters(self):
        """
        Get parameter values from dialog.
        
        Returns:
        --------
        dict
            Dictionary with parameter values
        """
        params = {}
        
        if self.effect_name == "FIR Low Pass" or self.effect_name == "FIR High Pass":
            params['cutoff_freq'] = self.param_controls['cutoff_freq'].value()
            params['N'] = self.param_controls['N'].value()
            
        elif self.effect_name == "FIR Band Pass" or self.effect_name == "FIR Band Reject":
            params['low_cutoff'] = self.param_controls['low_cutoff'].value()
            params['high_cutoff'] = self.param_controls['high_cutoff'].value()
            params['N_low'] = self.param_controls['N_low'].value()
            params['N_high'] = self.param_controls['N_high'].value()
            
        elif self.effect_name == "Bass Boost":
            params['boost_factor'] = self.param_controls['boost_factor'].value()
            params['cutoff_freq'] = self.param_controls['cutoff_freq'].value()
            
        elif self.effect_name == "Reverb":
            params['room_size'] = self.param_controls['room_size'].value()
            params['damping'] = self.param_controls['damping'].value()
            params['wet_level'] = self.param_controls['wet_level'].value()
            
        elif self.effect_name == "Echo":
            params['delays_ms'] = [
                self.param_controls['delay1'].value(),
                self.param_controls['delay2'].value()
            ]
            params['decays'] = [
                self.param_controls['decay1'].value(),
                self.param_controls['decay2'].value()
            ]
            
        elif self.effect_name == "Speed Up":
            params['speed_factor'] = self.param_controls['speed_factor'].value()
            params['preserve_pitch'] = (self.param_controls['preserve_pitch'].currentText() == "Yes")
            
        elif self.effect_name == "Tremolo":
            params['depth'] = self.param_controls['depth'].value()
            params['rate'] = self.param_controls['rate'].value()
                        
        elif self.effect_name == "Equalizer":
            gains = []
            for i in range(5):
                gain_key = f'gain_{i}'
                if gain_key in self.param_controls:
                    gains.append(self.param_controls[gain_key].value() / 100.0)
            params['gains'] = gains
            
        return params


class ChannelComparisonDialog(QDialog):
    """
    Dialog for displaying the comparison between stereo channels.
    """
    def __init__(self, comparison_results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stereo Channel Comparison")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Add comparison results
        if 'error' in comparison_results:
            # Display error
            error_label = QLabel(f"Error: {comparison_results['error']}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)
        elif not comparison_results.get('is_stereo', False):
            # Inform that the file is not stereo
            info_label = QLabel(comparison_results.get('analysis', "The audio file is not stereo."))
            layout.addWidget(info_label)
        else:
            # Display numerical comparison
            info_group = QGroupBox("Channel Comparison")
            info_layout = QFormLayout()
            
            # Max difference
            max_diff = comparison_results.get('max_difference', 0)
            info_layout.addRow("Maximum Difference:", QLabel(str(max_diff)))
            
            # Mean difference
            mean_diff = comparison_results.get('mean_difference', 0)
            info_layout.addRow("Mean Difference:", QLabel(f"{mean_diff:.2f}"))
            
            # Correlation
            correlation = comparison_results.get('correlation', 0)
            info_layout.addRow("Correlation:", QLabel(f"{correlation:.4f}"))
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
            
            # Add analysis
            analysis_label = QLabel(comparison_results.get('analysis', ""))
            analysis_label.setWordWrap(True)
            layout.addWidget(analysis_label)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)