class VisaIOError(Exception):
    """
    Exception raised for errors related to VISA communication.
    """
    def __init__(self, message, msg=None):
        super().__init__(message)
        self.msg = msg

class InstrumentError(Exception):
    """
    Exception raised for instrument-related logic errors.
    """
    def __init__(self, message, command=None):
        super().__init__(message)
        self.command = command
