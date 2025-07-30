from abc import ABC, abstractmethod
from .base_instrument import BaseInstrument

class Oscilloscope(BaseInstrument, ABC):
    """
    Abstract base class for oscilloscopes.
    """

    @abstractmethod
    def start_acquisition(self):
        """Start data acquisition."""
        pass

    @abstractmethod
    def stop_acquisition(self):
        """Stop data acquisition."""
        pass

    @abstractmethod
    def get_waveform(self, channel, format_mode="ASCII"):
        """Acquire waveform from the given channel."""
        pass

    @abstractmethod
    def decode_waveform(self, raw_bytes, channel):
        """Decode raw waveform data."""
        pass

    @abstractmethod
    def set_channel_scale(self, channel, scale):
        """Set the vertical scale for the channel."""
        pass

    @abstractmethod
    def set_channel_offset(self, channel, offset):
        """Set the vertical offset for the channel."""
        pass

    @abstractmethod
    def get_channel_scale(self, channel):
        """Get the vertical scale for the channel."""
        pass

    @abstractmethod
    def get_channel_offset(self, channel):
        """Get the vertical offset for the channel."""
        pass

    @abstractmethod
    def measure(self, parameter, channel):
        """Perform measurement on the channel."""
        pass
