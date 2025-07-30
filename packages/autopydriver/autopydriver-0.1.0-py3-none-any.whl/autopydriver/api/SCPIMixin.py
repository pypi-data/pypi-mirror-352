class SCPIMixin:
    """
    A mixin class that provides a standart methods of SCPI device.
    """
    def idn(self):
        """
        Get the identification (IDN) string of the device.
        """
        return self.query("*IDN?")
    
    def reset(self):
        """
        Reset the device to its default state.
        """
        self.write("*RST")
    
    def clear_status(self):
        """
        Clear the status of the device.
        """
        self.write("*CLS")
        
    def get_all_errors(self):
        """
        Get all errors from the device.
        """
        return self.query(":SYST:ERROR:ALL?")
    
    def get_error(self):    
        """
        Get the last error from the device.
        """
        return self.query(":SYST:ERROR?") 
    
