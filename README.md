# Audio Player Pro

A modern, feature-rich audio player application with advanced processing capabilities, visualizations, and effects. Built with Python and PyQt5.

## Features

### Audio Playback
- Support for WAV and MP3 file formats
- Playlist management with drag-and-drop functionality
- Playback controls (play, pause, stop, shuffle, repeat)
- Volume and playback speed adjustment

### Audio Processing
- Real-time audio visualizations:
  - Waveform display
  - Spectrogram analysis
  - Frequency spectrum visualization
- Comprehensive audio information display

### Audio Effects
- **FIR Filters**:
  - Low-pass filter
  - High-pass filter
  - Band-pass filter
  - Band-reject filter
- **Basic Effects**:
  - Bass boost
  - Reverb
  - Echo
  - Speed adjustment with pitch preservation
  - Tremolo
- **Advanced Effects**:
  - Equalizer with 5-band control
  - Effect combinations

### Signal Generation
- Sine wave generator
- Square wave generator
- Sawtooth wave generator
- White and pink noise generators

### *(Coming soon)* Recording
- Audio recording with configurable parameters
- Recording visualization
- Format conversion

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/audio-player-pro.git
   cd audio-player-pro
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application
Launch the application with:
```bash
python main.py
```

### Basic Controls
- **Load Files**: Click "📂 Load" to add audio files to the playlist
- **Playback**: Use the play/pause, stop buttons to control playback
- **Playlist**: Double-click an item to play it
- **Volume**: Adjust using the volume slider
- **Playback Speed**: Control with the speed slider

### Applying Effects
1. Load an audio file
2. Select an effect from the dropdown menu
3. Click "💾 Apply Effect"
4. Configure effect parameters in the dialog
5. Save the processed file

### Generating Test Signals
1. Click "🎵 Generate Test Signal"
2. Select signal type (sine, square, sawtooth, noise)
3. Configure parameters (frequency, duration, amplitude)
4. Click "Generate"

## Project Structure

```
audio_player/
├── core/                # Core functionality
│   ├── audio_processor.py
│   ├── file_handler.py
│   └── signal_generator.py
├── effects/             # Audio effects
│   ├── basic_effects.py
│   ├── filters.py
│   └── advanced_effects.py
├── ui/                  # User interface
│   ├── dialogs.py
│   ├── main_window.py
│   ├── player_controls.py
│   └── visualizations.py
└── utils/               # Utilities
    └── helpers.py
```

## Development

### Setting up Development Environment
1. Fork the repository
2. Clone your fork
3. Set up the environment as described in the Installation section
4. Make your changes
5. Submit a pull request

### Branch Structure
- `main`: Stable releases
- `develop`: Development branch
- Feature branches: `feature/feature-name`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Acknowledgments

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) for the GUI framework
- [NumPy](https://numpy.org/) and [SciPy](https://scipy.org/) for signal processing
- [Matplotlib](https://matplotlib.org/) for visualizations
- [Librosa](https://librosa.org/) for audio analysis