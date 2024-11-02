import logging

# Enable or disable debug logging
DEBUG_LOGGING = False

if DEBUG_LOGGING:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)


def main():
    """
    Main entry point for the PyQt6 application.

    This function initializes the application, sets a notification,
    and schedules the start of the main UI component using a QTimer.
    """
    from PyQt6.QtWidgets import QApplication
    import sys
    from .lingu import Lingu
    from lingu import notify, wait_notify

    # Initialize the application
    app = QApplication(sys.argv)

    # Display a startup notification
    notify("Start", "Loading modules", -1, "custom", "🚀")

    def on_notification_visible():
        # Start linguflex after notification became visible
        lingu = Lingu(app)
        lingu.start()

    # Wait for notification
    # (If we start lingu before waiting for display of the notification
    #  the notification will not be displayed because UI is blocked)
    wait_notify(on_notification_visible)

    # Execute the application and exit
    sys.exit(app.exec())


if __name__ == '__main__':
    from lingu import log
    log.inf("Logging initialized.")
    main()
    log.inf("Exit")
