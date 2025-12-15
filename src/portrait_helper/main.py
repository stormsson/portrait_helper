"""Application entry point for Portrait Helper."""

import sys
import logging
from PySide6.QtWidgets import QApplication

from portrait_helper.gui.main_window import MainWindow

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Portrait Helper")
    app.setOrganizationName("Portrait Helper")

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("Portrait Helper application started")

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

