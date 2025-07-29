from ..Internal_DAC_interface import *
from ..data_collection import *
import math

class Internal_ThermistorEmulationInterface:
    def __init__(self,name=None,ref_resistance=10000.0,ref_temperature=25.0,beta=3950.0,series_resistance=10000.0,
                 ref_voltage=3.3,dac_interface:Internal_DACInterface=None,data_interface:DataCollectionInterface=None,register_for_log=False):

        self.name=name
        self.ref_resistance=ref_resistance
        self.ref_temperature=ref_temperature
        self.beta=beta
        self.series_resistance=series_resistance
        self.ref_voltage=ref_voltage
        self.dac_interface=dac_interface
        self.data_interface = data_interface
        self.current_temperature=ref_temperature
        self.current_resistance=ref_resistance
        self.current_voltage=self.ref_voltage/2.0   
        self.data_dict={"set_temperature":self.current_temperature}     
        self.register_for_log=register_for_log
        try:
            self.initialize_thermistor()
        except Exception as e:
            pass
         ### if data collection interface is available, register dictionary for monitoring
        if(self.data_interface):
            self.data_interface.register_for_data_collection(self.data_dict,self.register_for_log,logger_name=str(self.name))
            self.data_interface.update_data(self.data_dict,logger_name=str(self.name))
        
    def initialize_thermistor(self):
        """Initialize the thermistor to referance temperature"""
        if self.dac_interface:
            self.dac_interface.set_voltage(self.ref_voltage/2.0)
    
    #### function to set temperature in degree celsius
    def set_temperature(self,temperature):
        """Set the temperature of the thermistor"""
        self.current_temperature=temperature
        temp_kelvin=temperature+273.15
        ref_temp_kelvin=self.ref_temperature+273.15 
        self.current_resistance=self.ref_resistance*math.exp(self.beta*((1.0/temp_kelvin)-(1.0/ref_temp_kelvin)))
        self.current_voltage=self.ref_voltage*self.current_resistance/(self.current_resistance+self.series_resistance)
        self.dac_interface.set_voltage(self.current_voltage)
        self.data_dict["set_temperature"]=temperature
        if(self.data_interface):
            self.data_interface.update_data(self.data_dict,logger_name=str(self.name))
        
    def get_temperature(self):
        """Get the temperature of the thermistor"""
        return self.current_temperature
    
    def get_resistance(self):
        """Get the resistance of the thermistor"""
        return self.current_resistance
    
    def get_voltage(self):
        """Get the voltage of the thermistor"""
        return self.current_voltage
        
        
        
        

        
        
        
