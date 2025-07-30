import logging

class InstrumentLogger:
    """
    A common logger for instrument communication and debugging.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize the logger with a given name and log level.
        Args:
            name (str): Logger name.
            level (int): Logging level (e.g. logging.INFO).
        """
        self.logger = logging.getLogger(name)
        self.set_level(level)

    def set_level(self, level: int):
        """
        Set the log level for this logger.
        Args:
            level (int): Logging level.
        """
        self.logger.setLevel(level)

    def enable(self):
        """Enable logging at DEBUG level."""
        self.set_level(logging.DEBUG)

    def disable(self):
        """Disable logging (set to CRITICAL+1)."""
        self.set_level(logging.CRITICAL + 1)

    def info(self, msg, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)
