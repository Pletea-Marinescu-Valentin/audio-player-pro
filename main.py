"""
Main entry point for the Audio Player Pro application.
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """
    Main function to start the application.
    """
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("Audio Player Pro")
    app.setOrganizationName("AudioTeam")
    app.setOrganizationDomain("example.com")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()