from abc import ABC, abstractmethod

class Adapter(ABC):
    """
    Abstract base class for communication adapters.
    Defines the main interface for low-level communication with instruments.
    """

    def __init__(self):
        self.connection = None

    @abstractmethod
    def write(self, command, **kwargs):
        """Send a command to the instrument."""
        pass

    @abstractmethod
    def write_bytes(self, content, **kwargs):
        """Send raw bytes to the instrument."""
        pass

    @abstractmethod
    def read(self, **kwargs):
        """Read response as string from the instrument."""
        pass

    @abstractmethod
    def read_bytes(self, count=-1, **kwargs):
        """Read bytes from the instrument."""
        pass

    @abstractmethod
    def query(self, command, **kwargs):
        """Send command and return response as string."""
        pass

    @abstractmethod
    def query_binary_values(self, command, **kwargs):
        """Send command and return binary values."""
        pass

    def close(self):
        """Close the underlying connection."""
        if self.connection is not None:
            self.connection.close()
