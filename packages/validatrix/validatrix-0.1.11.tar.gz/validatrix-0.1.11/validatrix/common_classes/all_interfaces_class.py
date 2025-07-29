
from ..data_collection import DataCollectionInterface
from ..internal_can_interface import Internal_CANInterface    
from ..internal_thermistor_emulation import Internal_ThermistorEmulationInterface
from ..Internal_DAC_interface import Internal_DACInterface
from ..automated_test_interface import AutomatedTestInterface
from ..Internal_digital_read_interface import Internal_DigitalReadInterface
from ..Internal_RS485_slave_interface import *


class all_interfacesClass:
    def __init__(self):
        
        self.data_interface: DataCollectionInterface=None  
        self.auto_test_interface: AutomatedTestInterface=None
        self.internal_can_interface_list: list[Internal_CANInterface]=[] 
        self.internal_thermistor_emulation_list: list[Internal_ThermistorEmulationInterface]=[]
        self.internal_relay_read_interface_list: list[Internal_DigitalReadInterface] =[]
        self.internal_RS485_slave_list: list[Internal_RS485_slave_class]=[]

    def add_interface(self,interface_name,interface_object):
        if interface_name == 'data_interface':
            if not isinstance(interface_object, DataCollectionInterface):
                raise TypeError("Expected a DataCollectionInterface object")
            self.data_interface =interface_object
        elif interface_name == 'auto_test_interface':
            if not isinstance(interface_object, AutomatedTestInterface):
                raise TypeError("Expected an AutomatedTestInterface object")
            self.auto_test_interface = interface_object
        elif 'int_can' in interface_name:
            if not isinstance(interface_object, Internal_CANInterface):
                raise TypeError("Expected a Internal_CANInterface object")
            self.internal_can_interface_list.append(interface_object)
        elif 'int_thermistor' in interface_name:
            if not isinstance(interface_object, Internal_ThermistorEmulationInterface):
                raise TypeError("Expected a Internal_ThermistorEmulationInterface object")
            self.internal_thermistor_emulation_list.append(interface_object)
        elif 'int_relay_read' in interface_name:
            if not isinstance(interface_object, Internal_DigitalReadInterface):
                raise TypeError("Expected a Internal_DigitalReadInterface object")
            self.internal_relay_read_interface_list.append(interface_object)
        elif 'int_RS485_slave' in interface_name:
            if not isinstance(interface_object, Internal_RS485_slave_class):
                raise TypeError("Expected a Internal_RS485_slave_class object")
            self.internal_RS485_slave_list.append(interface_object)
        else:
            raise ValueError(f"Unknown interface name: {interface_name}")
    
   