
import os
try:
    import board
    import busio
    import adafruit_mcp4725
except:
    pass

from time import sleep

class Internal_DACInterface:
    def __init__(self,channal_addr=None,input_voltage=3.3):
        print("Initializing DAC interface...")
        print("DAC channel address:",channal_addr)
        self._addr = channal_addr
        self.dac_obj = None
        self._input_voltage=input_voltage
        self.current_voltage=input_voltage/2.0
        self.current_bit_value=2048
        try:
            self.initialize_dac()
        except:
            pass
        

    def initialize_dac(self):
        """Initialize DAC object"""
        if self._addr:
            # Initialize I2C bus.
            i2c = busio.I2C(board.SCL, board.SDA)
            # Initialize MCP4725.
            self.dac_obj = adafruit_mcp4725.MCP4725(i2c, address=self._addr)
       
        
    def set_voltage(self,voltage):
        """Set the voltage of the DAC"""
        self.current_voltage=voltage
        self.current_bit_value=int(voltage*4096/self._input_voltage)
        if self.current_bit_value>4095:
            self.current_bit_value=4095
        if self.current_bit_value<0:
            self.current_bit_value=0
        self.dac_obj.raw_value = self.current_bit_value   
    
    def set_voltage_by_bit_value(self,bit_value):
        """Set the voltage of the DAC by bit value"""
        self.current_bit_value=bit_value
        if self.current_bit_value>4095:
            self.current_bit_value=4095
        if self.current_bit_value<0:
            self.current_bit_value=0    
        self.current_voltage=bit_value*self._input_voltage/4096.0
        self.dac_obj.raw_value = self.current_bit_value   

    def get_voltage(self):
        """Get the voltage of the DAC"""
        return self.current_voltage
    
    

    def get_bit_value(self):
        """Get the bit value of the DAC"""
        return self.current_bit_value
    
    def get_input_voltage(self):
        """Get the input voltage of the DAC"""
        return self._input_voltage
    
    def get_addr(self):
        """Get the address of the DAC"""
        return self._addr
    
    
