

from threading import Thread, Event
import threading
from time import sleep
import struct
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.client import ModbusSerialClient as msc
from pymodbus.payload import BinaryPayloadDecoder as pp
from pymodbus.transaction import ModbusRtuFramer
from ..data_collection import *
from .Internal_RS485_slave_server import Internal_RS485_slave_server_class
from .Internal_RS485_device_data import *

#####make sure that pymodbus version in sudo pip3 is 3.1.3

class Internal_RS485_slave_class:
    def __init__(self,name=None,device_name=None,slave_address=None,
                 data_interface:DataCollectionInterface=None,
                 server_obj:Internal_RS485_slave_server_class=None,
                 register_for_log=False,global_update_interval=0.1):
       

        self.name=name        
        self.device_name=device_name
        self._lock = threading.Lock()
        self.global_update_thread=None
        self.register_update_thread=None
        self.set_data_dict = {}
        self.base_data_dict = {}
        self.load_data_dict()

        self.data_interface = data_interface
        self.register_for_log=register_for_log
        self.global_data_update_interval=global_update_interval
        self.server_obj=server_obj
        self.slave_address=slave_address

        ### if data collection interface is available, register dictionary for monitoring
        if(self.data_interface):
            self.data_interface.register_for_data_collection(self.set_data_dict,self.register_for_log,logger_name=str(self.name))
            self.data_interface.update_data(self.set_data_dict,logger_name=str(self.name))

        # # Define the Modbus registers
        self.coils = ModbusSequentialDataBlock(1, [0] * 100)
        self.discrete_inputs = ModbusSequentialDataBlock(1, [0] * 100)
        self.holding_registers = ModbusSequentialDataBlock(1, [0] * 100)
        self.input_registers = ModbusSequentialDataBlock(1, [0] * 100)

        # Define the Modbus slave context
        self.slave_context = ModbusSlaveContext(
            di=self.discrete_inputs,
            co=self.coils,
            hr=self.holding_registers,
            ir=self.input_registers
        )
        try:
            self.add_to_server()
        except:
            pass
    
    def add_to_server(self):
        """Add this slave to the server object"""
        if self.server_obj:
            self.server_obj.add_slave(slave_id=self.slave_address, slave_context=self.slave_context)
            self.global_update_thread = Thread(target=self.update_data_in_data_interface, daemon=True)
            self.global_update_thread.start()
            self.register_update_thread = Thread(target=self.update_set_data_to_registers, daemon=True)
            self.register_update_thread.start()

        else:
            print("No server object provided to add slave.")
    
    def start(self):
        """Start the RS485 slave server"""
        if self.server_obj:
            self.server_obj.set_slave_state(slave_id=self.slave_address, state=True)
        else:
            print("No server object provided to start the server.")

    def stop(self):
        """Stop the RS485 slave server"""
        if self.server_obj:
            self.server_obj.set_slave_state(slave_id=self.slave_address, state=False)
        else:
            print("No server object provided to stop the server.")

    
    def convert_bin_list_to_int(ls):
        # print("binary_signals: "+str(ls))
        bin_str=""
        for l in ls:
            bin_str=str(l)+bin_str
        return int(bin_str,2)
    
    
    def float_to_bytes(value):
        # Pack float into 32-bit binary, then unpack as hex
        hex_val= hex(struct.unpack('<I', struct.pack('<f', value))[0])    
        while(len(hex_val)<10):
            hex_val=hex_val[:2]+"0"+hex_val[2:]
        
        # print(hex_val)
        byte2= int(hex_val[2:6], 16)
        byte1 = int(hex_val[6:10], 16)

        return byte1,byte2

    def load_data_dict(self):
        if(self.device_name == "WF_chiller"):
            self.set_data_dict = WF_chiller_data.copy()
            self.base_data_dict = WF_chiller_data_base.copy()
        elif(self.device_name == "WF_heater"):
            self.set_data_dict = WF_heater_data.copy()
            self.base_data_dict = WF_heater_base_data.copy()
        elif(self.device_name == "LT_AC_EM"):
            self.set_data_dict = LT_AC_EM_data_dict.copy()
            self.base_data_dict = LT_AC_EM_data_dict_base.copy()

    ### function to update local data dictionary in global data interface
    def update_data_in_data_interface(self):
        while(1):
            try:
                with self._lock:
                    self.data_interface.update_data(self.set_data_dict,logger_name=str(self.name))
            except:
                pass
            sleep(self.global_data_update_interval)

    def update_set_data_to_registers(self):
        """Update the Modbus registers with the set data dictionary."""
        while(1):
            try:
                if(self.device_name == "WF_chiller"):
                    reg4_data=int(self.set_data_dict["chiller_liquid_temp"]*10)
                    reg5_data=int(self.set_data_dict["chiller_aft_temp"]*10)           

                    reg10_data=self.convert_bin_list_to_int([self.set_data_dict["chiller_room_temp_probe_fail"],
                                                        self.set_data_dict["chiller_aft_probe_fail"],
                                                        self.set_data_dict["chiller_room_temp_probe_ht_fault"],
                                                        self.set_data_dict["chiller_room_temp_probe_lt_fault"]])
                    
                    reg11_data=self.convert_bin_list_to_int([self.set_data_dict["chiller_pump_overload_fault"],
                                                        self.set_data_dict["chiller_spp_fault"],
                                                        self.set_data_dict["chiller_compressor_overload_fault"],
                                                        self.set_data_dict["chiller_hp_fault"],
                                                        self.set_data_dict["chiller_lp_fault"]])
                    
                    reg12_data=self.convert_bin_list_to_int([self.set_data_dict["chiller_low_liquid_level_fault"],
                                                        self.set_data_dict["chiller_liquid_line_high_temp_fault"],
                                                        self.set_data_dict["chiller_high_temp_fault"],
                                                        self.set_data_dict["chiller_aft_fault"]])
                    
                    reg13_data=self.convert_bin_list_to_int([self.set_data_dict["chiller_compressor_on"],
                                                        self.set_data_dict["chiller_pump_on"],
                                                        self.set_data_dict["chiller_sv_on"],
                                                        self.set_data_dict["chiller_alarm_on"]])
                    
                    reg28_data=int(self.set_data_dict["chiller_set_high_set"]*10) 
                    reg29_data=int(self.set_data_dict["chiller_set_low_set"]*10) 
                    reg30_data=int(self.set_data_dict["chiller_set_set_point"]*10) 
                    reg34_data=int(self.set_data_dict["chiller_set_differential"]*10) 
                    reg35_data=int(self.set_data_dict["chiller_set_high_temp_alarm"]*10) 
                    reg36_data=int(self.set_data_dict["chiller_set_low_temp_alarm"]*10) 
                    reg38_data=int(self.set_data_dict["chiller_set_aft_set_temp"]*10) 
                    reg39_data=int(self.set_data_dict["chiller_set_aft_differential"]*10) 
                    reg51_data=int(self.set_data_dict["chiller_remote_start"]) 

                    self.holding_registers.setValues(4, reg4_data)
                    self.holding_registers.setValues(5, reg5_data)            
                    self.holding_registers.setValues(10, reg10_data)
                    self.holding_registers.setValues(11, reg11_data)
                    self.holding_registers.setValues(12, reg12_data)
                    self.holding_registers.setValues(13, reg13_data)
                    self.holding_registers.setValues(28, reg28_data)
                    self.holding_registers.setValues(28, reg28_data)
                    self.holding_registers.setValues(29, reg29_data)
                    self.holding_registers.setValues(30, reg30_data)
                    self.holding_registers.setValues(34, reg34_data)
                    self.holding_registers.setValues(35, reg35_data)
                    self.holding_registers.setValues(36, reg36_data)
                    self.holding_registers.setValues(38, reg38_data)
                    self.holding_registers.setValues(39, reg39_data)
                    self.holding_registers.setValues(51, reg51_data)
                
                elif(self.device_name == "WF_heater"):

                    relay_encoded_list=["heater_relay_sts_alarm","heater_relay_sts_compressor"]
                    fault_encoded_list=["heater_fault_sts_probe_fail_low","heater_fault_sts_probe_fail_high",
                                            "heater_fault_sts_ht","heater_fault_sts_lt","heater_fault_water_level_low",
                                            "heater_fault"]
                    
                    reg11_data=self.convert_bin_list_to_int([self.set_data_dict["heater_relay_sts_alarm"],
                                                        self.set_data_dict["heater_relay_sts_compressor"]])
                                                
            
                    reg12_data=self.convert_bin_list_to_int([self.set_data_dict["heater_fault_sts_probe_fail_low"],
                                                        self.set_data_dict["heater_fault_sts_probe_fail_high"],
                                                        self.set_data_dict["heater_fault_sts_ht"],
                                                        self.set_data_dict["heater_fault_sts_lt"],
                                                        self.set_data_dict["heater_fault_water_level_low"],
                                                        self.set_data_dict["heater_fault"]])
                    
                    self.holding_registers.setValues(self.set_data_dict['relay_status'], reg11_data)
                    self.holding_registers.setValues(self.set_data_dict['fault_status'], reg12_data)

                    for k in self.set_data_dict.keys():
                        if(k not in relay_encoded_list and k not in fault_encoded_list):
                            reg_data=int(self.set_data_dict[k]*10)
                            self.holding_registers.setValues(self.set_data_dict[k], reg_data)

                elif(self.device_name == "LT_AC_EM"):

                    for k in self.set_data_dict.keys():  
                        if(k=="em_k_watt_hour"):
                            in_data=self.set_data_dict[k]*1000
                        else:
                            in_data=self.set_data_dict[k]

                        b1,b2=self.float_to_bytes(in_data)
                        reg_name_1=str(k)+"_b1"
                        reg_name_2=str(k)+"_b2"
                        
                        self.holding_registers.setValues(LT_AC_EM_registers_dict[reg_name_1], b1)
                        self.holding_registers.setValues(LT_AC_EM_registers_dict[reg_name_2], b2)

            except Exception as e:
                print(f"Error updating registers: {e}")

            sleep(0.1)

    def set_data(self, key, value):
        """Set a value in the data dictionary."""
        with self._lock:
            if key in self.set_data_dict:
                self.set_data_dict[key] = value
            else:
                print(f"Key {key} not found in set_data_dict.")
       
    def get_data_dict(self):
        """Get the current data dictionary."""
        with self._lock:
            return self.set_data_dict.copy()
        
    def reset_to_base_values(self):
        """Reset the data dictionary to base values."""
        with self._lock:
            self.set_data_dict = self.base_data_dict.copy()
            
