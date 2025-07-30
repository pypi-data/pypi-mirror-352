import numpy as np
import logging
from api.SCPIMixin import SCPIMixin
from api.oscilloscope import Oscilloscope
from utils.exceptions import InstrumentError
from utils.logger import InstrumentLogger
from typing import Dict, Union

class RohdeSchwarzRTM3002(Oscilloscope, SCPIMixin):
    """
    Enhanced driver for the Rohde & Schwarz RTM3002 oscilloscope.

    Provides high-level methods to control channels, timebase, trigger, 
    acquisition, waveform transfer and measurement operations via SCPI commands.
    """

    CHANNELS = [1, 2]
    WAVEFORM_FORMATS = ["BYTE", "ASCII"]
    TRIGGER_MODES = ["AUTO", "NORMal", "SINGle"]
    MEASUREMENT_PARAMS = {
        "VPP": "VPP",
        "VRMS": "VRMS",
        "FREQ": "FREQuency",
        "PERIOD": "PERiod",
        "AVG": "AVG",
        "MAX": "MAXimum",
        "MIN": "MINimum"
    }

    def __init__(self, adapter, name="Rohde & Schwarz RTM3002", log_level=logging.INFO, **kwargs):
        """
        Initialize the RTM3002 oscilloscope driver.

        Args:
            adapter: Communication adapter instance.
            name: Device name for logging.
            log_level: Logger level.
            **kwargs: Additional arguments for the parent class.
        """
        super().__init__(adapter, name=name, **kwargs)
        self.log = InstrumentLogger("drivers.oscilloscope.rtm3002", level=log_level)
        self._validate_connection()
        self.log.info(f"Successfully connected to {self.id}")

    def _validate_connection(self):
        """
        Check device identification string to ensure correct model is connected.
        """
        try:
            idn = self.id
            if "RTM3002" not in idn:
                raise InstrumentError(f"Connected device is not RTM3002: {idn}")
        except Exception as e:
            raise InstrumentError(f"Connection validation failed: {str(e)}")

    @property
    def id(self) -> str:
        """
        Get device identification string (*IDN?).
        Returns:
            str: Identification string.
        """
        return self.query("*IDN?").strip()

    def _valid_channel(self, channel: int):
        """
        Validate channel number.
        Args:
            channel: Channel number.
        Raises:
            InstrumentError: If channel number is invalid.
        """
        if channel not in self.CHANNELS:
            raise InstrumentError(f"Invalid channel {channel}. Available: {self.CHANNELS}")

    def start_acquisition(self):
        """
        Start continuous acquisition.
        """
        self.write(":RUN")
        self.log.debug("Acquisition started")

    def stop_acquisition(self):
        """
        Stop acquisition.
        """
        self.write(":STOP")
        self.log.debug("Acquisition stopped")

    def single_shot(self):
        """
        Perform a single acquisition (single trigger).
        """
        self.write(":SINGle")
        self.log.debug("Single shot acquisition triggered")

    def get_waveform(self, channel: int, format_mode: str = "ASCII") -> np.ndarray:
        """
        Acquire waveform data from the specified channel.

        Args:
            channel: Channel number.
            format_mode: Data format, "ASCII" (default) or "BYTE".

        Returns:
            np.ndarray: Array of waveform points.

        Raises:
            InstrumentError: If format is unknown or acquisition fails.
        """
        self.log.info(f"Reading waveform from channel {channel}")
        self.query("SING;*OPC?")
        points = self.query("ACQ:POIN?")
        print(f'Number of sample points: {points}')
        if format_mode == "ASCII":
            self.write("FORMat:DATA ASC")
            self.query("*OPC?")
            data = self.query(f"CHAN{channel}:DATA?")
            print(data)
            waveform = np.array([float(val) for val in data.strip().split(',') if val], dtype=np.float32)
            self.log.debug(f"Read {len(waveform)} points (ASCII) from CH{channel}")
            return waveform
        else:
            raise InstrumentError(f"Unknown waveform data format: {format_mode}")

    def set_channel_scale(self, channel: int, scale: float):
        """
        Set vertical scale for the given channel (in V/div).

        Args:
            channel: Channel number.
            scale: Vertical scale in volts per division.
        """
        self._valid_channel(channel)
        self.write(f":CHANnel{channel}:SCALe {scale}")
        self.log.debug(f"Channel {channel} scale set to {scale} V/div")

    def get_channel_scale(self, channel: int) -> float:
        """
        Get vertical scale for the given channel.

        Args:
            channel: Channel number.
        Returns:
            float: Vertical scale in V/div.
        """
        self._valid_channel(channel)
        return float(self.query(f":CHANnel{channel}:SCALe?"))

    def set_channel_offset(self, channel: int, offset: float):
        """
        Set vertical offset for the given channel (in volts).

        Args:
            channel: Channel number.
            offset: Vertical offset in volts.
        """
        self._valid_channel(channel)
        self.write(f":CHANnel{channel}:OFFSet {offset}")
        self.log.debug(f"Channel {channel} offset set to {offset} V")

    def get_channel_offset(self, channel: int) -> float:
        """
        Get vertical offset for the given channel.

        Args:
            channel: Channel number.
        Returns:
            float: Vertical offset in volts.
        """
        self._valid_channel(channel)
        return float(self.query(f":CHANnel{channel}:OFFSet?"))

    def measure(self, parameter: str, channel: int) -> float:
        """
        Perform measurement on the specified channel.

        Args:
            parameter: Measurement type, e.g. "VPP", "VRMS", "FREQ", etc.
            channel: Channel number.

        Returns:
            float: Measured value.

        Raises:
            InstrumentError: If parameter is invalid or measurement fails.
        """
        self._valid_channel(channel)
        scpi_param = self.MEASUREMENT_PARAMS.get(parameter.upper())
        if not scpi_param:
            raise InstrumentError(f"Unknown measurement: {parameter}")

        try:
            # Note: For some SCPI commands, format may vary; update as needed.
            return float(self.query(f":MEASure:RESult:{scpi_param}? CH{channel}"))
        except Exception as e:
            raise InstrumentError(f"Measurement failed: {str(e)}")

    def get_timebase_settings(self) -> Dict[str, float]:
        """
        Get current timebase settings.

        Returns:
            Dict[str, float]: Timebase settings (scale and position).
        """
        return {
            "scale": float(self.query(":TIMebase:SCALe?")),
            "position": float(self.query(":TIMebase:POSition?"))
        }

    def set_timebase(self, scale: float = None, position: float = None):
        """
        Configure timebase settings.

        Args:
            scale: Timebase scale (seconds/division).
            position: Timebase position (seconds).
        """
        if scale is not None:
            self.write(f":TIMebase:SCALe {scale}")
        if position is not None:
            self.write(f":TIMebase:POSition {position}")

    def get_trigger_settings(self) -> Dict[str, Union[str, float]]:
        """
        Get current trigger settings.

        Returns:
            Dict[str, Union[str, float]]: Trigger settings (mode and level).
        """
        return {
            "mode": self.query(":TRIGger:MODE?").strip(),
            "level": float(self.query(":TRIGger:LEVel?"))
        }

    def set_trigger(self, mode: str = None, level: float = None):
        """
        Configure trigger settings.

        Args:
            mode: Trigger mode ("AUTO", "NORMal", "SINGle").
            level: Trigger level (volts).
        Raises:
            InstrumentError: If trigger mode is invalid.
        """
        if mode is not None:
            if mode not in self.TRIGGER_MODES:
                raise InstrumentError(f"Invalid trigger mode: {mode}")
            self.write(f":TRIGger:MODE {mode}")
        if level is not None:
            self.write(f":TRIGger:LEVel {level}")

    def save_screenshot(self, filename: str, format: str = "PNG"):
        """
        Save oscilloscope screenshot to file.

        Args:
            filename: File name to save screenshot.
            format: Screenshot format (e.g., "PNG").
        """
        self.write(f":HARDcopy:INKSaver OFF")
        self.write(f":HARDcopy:FORMat {format}")
        raw_data = self.query_binary_values(":HARDcopy:START?", datatype='B', container=bytes)
        with open(filename, 'wb') as f:
            f.write(raw_data)
        self.log.info(f"Screenshot saved to {filename}")

    def close(self):
        """
        Close connection to the instrument.
        """
        try:
            self.adapter.close()
            self.log.info("Connection closed")
        except Exception as e:
            self.log.error(f"Error closing connection: {str(e)}")
            raise
