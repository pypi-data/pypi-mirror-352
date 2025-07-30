from utils.exceptions import InstrumentError

class Instrument:
    """
    Universal base class for all SCPI-compatible instruments.
    Providing basic communication and parsing logic.
    """

    def __init__(self, adapter, name="Instrument", **kwargs):
        """
        Initialize an Instrument instance.
        Args:
            adapter: Adapter object or resource address.
            name (str): Readable instrument name.
            **kwargs: Additional options for VISAAdapter if adapter is str.
        """
        if isinstance(adapter, str):
            from comm.visa_adapter import VISAAdapter
            adapter = VISAAdapter(adapter, **kwargs)
        self.adapter = adapter
        self.name = name

    def write(self, command, **kwargs):
        """Send a command string to the instrument."""
        self.adapter.write(command, **kwargs)

    def write_bytes(self, content, **kwargs):
        """Send raw bytes to the instrument."""
        self.adapter.write_bytes(content, **kwargs)

    def read(self, **kwargs):
        """Read a string response from the instrument."""
        return self.adapter.read(**kwargs)

    def read_bytes(self, count=-1, **kwargs):
        """Read bytes from the instrument."""
        return self.adapter.read_bytes(count, **kwargs)

    def query(self, command, get_process=str, **kwargs):
        """
        Send a command and return the processed response.
        """
        resp = self.adapter.query(command, **kwargs)
        try:
            result = get_process(resp)
        except Exception as exc:
            raise InstrumentError(f"Failed to parse: '{resp}'") from exc
        return result

    def query_binary_values(self, command, datatype='B', container=bytes, get_process=None, **kwargs):
        """
        Send command and return binary values.
        """
        data = self.adapter.query_binary_values(command, datatype=datatype, container=container, **kwargs)
        if get_process:
            data = get_process(data)
        return data

    def close(self):
        """Close the adapter connection."""
        self.adapter.close()
