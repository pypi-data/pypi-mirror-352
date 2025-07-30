import pyvisa
from comm.adapter import Adapter

class VISAAdapter(Adapter):
    """
    VISA Adapter for communication with instruments via VISA protocol.
    Providing low-level read/write/query operations, including binary transfer.
    """

    def __init__(self, resource_name, rm=None, visa_library="", **kwargs):
        """
        Initialize a VISAAdapter instance.
        Args:
            resource_name (str): VISA resource address.
            rm: Optional pyvisa ResourceManager (used for simulation).
            visa_library (str): VISA backend library string.
            **kwargs: Additional options passed to open_resource.
        """
        super().__init__()
        if rm is not None:
            self.rm = rm
        else:
            self.rm = pyvisa.ResourceManager(visa_library)
        self.connection = self.rm.open_resource(resource_name, **kwargs)
        self.resource_name = resource_name

    def write(self, command, **kwargs):
        """Send a command string to the instrument."""
        self.connection.write(command, **kwargs)

    def write_bytes(self, content, **kwargs):
        """Send raw bytes to the instrument."""
        self.connection.write_raw(content, **kwargs)

    def read(self, **kwargs):
        """Read a string response from the instrument."""
        return self.connection.read(**kwargs)

    def read_bytes(self, count=-1, **kwargs):
        """Read bytes from the instrument."""
        if count >= 0:
            return self.connection.read_bytes(count, **kwargs)
        return self.connection.read_raw(None, **kwargs)

    def query(self, command, **kwargs):
        """Send a command and return its string response."""
        return self.connection.query(command, **kwargs)

    def query_binary_values(self, command, datatype='B', container=bytes, **kwargs):
        """
        Send a command and return binary values as specified.
        """
        return self.connection.query_binary_values(command, datatype=datatype, container=container, **kwargs)

    def close(self):
        """Close the VISA connection and resource manager."""
        try:
            self.connection.close()
        except Exception:
            pass
        try:
            self.rm.close()
        except Exception:
            pass
