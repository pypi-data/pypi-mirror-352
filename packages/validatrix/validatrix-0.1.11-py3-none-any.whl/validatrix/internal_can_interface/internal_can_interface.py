import can
import cantools
import os
from pathlib import Path
from threading import Thread, Event
import threading
import json
from datetime import datetime
from time import sleep
import time
from ..data_collection import *

class Internal_CANInterface:
    def __init__(self,name=None,hw_channal=None,baudrate=None, dbc_file_path=None,
                 trace_file_name=None,data_interface:DataCollectionInterface=None,
                 register_for_log=False,global_update_interval=0.1):
        self._bus = None
        self._db = None
        self._running = Event()
        self._lock = threading.Lock()
        self._thread = None
        self.trace_file_name=trace_file_name
        self.data_dict = {}
        self.data_interface = data_interface
        self.register_for_log=register_for_log
        self.global_data_update_interval=global_update_interval
        self.global_update_thread=None
        self.trace_file_path=None
        self.save_trace_file=False
        self.trace_csv_file=None
        self.trace_buffer=None
        self._periodic_msgs = {}  # Store periodic message threads
        self._periodic_events = {}  # Store events for stopping periodic messages
        

        if name:
            self.name=name
        else:
            self.name=self.hw_channal

        self.hw_channal=hw_channal
        self.baudrate=baudrate

        try:
            self.load_dbc(dbc_file_path)
        except:
            pass
        ### if data collection interface is available, register dictionary for monitoring
        if(self.data_interface):
            self.data_interface.register_for_data_collection(self.data_dict,self.register_for_log,logger_name=str(self.name))
            self.data_interface.update_data(self.data_dict,logger_name=str(self.name))
        try:
            self.connect()
            self.start()
        except:
            pass
        

    def load_dbc(self, dbc_file_path):
        """Load DBC file for message decoding"""
        if dbc_file_path and os.path.exists(dbc_file_path):
            self._db = cantools.database.load_file(dbc_file_path)
        # Initialize messages dictionary with all signals from DBC
        if self._db:
            self.data_dict = {}
            for message in self._db.messages:
                for signal in message.signals:
                    self.data_dict[str(message.frame_id)+"_"+str(signal.name)] = -1
        else:
            self.data_dict = {}

  
    def connect(self):
        """Connect to CAN bus"""
        try:
            os.system("sudo ip link set "+str(self.hw_channal)+" down")
            os.system("sudo ip link set "+str(self.hw_channal)+" type can bitrate "+str(self.baudrate)+"000")
            os.system("sudo ip link set "+str(self.hw_channal)+" up")
            sleep(1)
            self._bus = can.interface.Bus(
                channel=self.hw_channal,
                bustype='socketcan',
                bitrate=self.baudrate,
                receive_own_messages = True                
            )
            return True
        except Exception as e:
            # print(f"Error connecting to CAN bus: {e}")
            return False

    def start(self):
        """Start reading messages from CAN bus"""
        if not self._bus:
            return False
        
        self._running.set()
        self._thread = Thread(target=self._read_messages)
        self._thread.daemon = True
        self._thread.start()
        
        if(self.data_interface):
            self.global_update_thread = Thread(target=self.update_data_in_data_interface)
            self.global_update_thread.daemon = True
            self.global_update_thread.start()


        return True

    def stop(self):
        """Stop reading messages and all periodic sends"""
        # Stop all periodic messages
        for msg_key in list(self._periodic_events.keys()):
            msg_id, interval = map(int, msg_key.split('_'))
            self.stop_periodic_msg(msg_id, interval)
        
        # Stop main message reading
        self._running.clear()
        if self._thread:
            self._thread.join()
        if self._bus:
            self._bus.shutdown()

    def add_to_trace_buffer(self, msg):
        """Add message to trace buffer"""
        if self.trace_buffer is None:
            self.trace_buffer = {}
            
        ### add new message data to trace buffer
        if msg.arbitration_id not in self.trace_buffer.keys():            
            ctime = datetime.now()
            dt_str = ctime.strftime("%Y-%m-%d_%H:%M:%S.%f")            
            msg_dict = {
                "msg_id": hex(msg.arbitration_id),
                "msg_data": [hex(byte) for byte in msg.data],
                "timestamp": dt_str,
                "delay": 0,
            }
            self.trace_buffer[msg.arbitration_id] = msg_dict
        ### update older data dictionary with new data
        else:
            old_dt_str = self.trace_buffer[msg.arbitration_id]["timestamp"]
            ctime = datetime.now()
            dt_str = ctime.strftime("%Y-%m-%d_%H:%M:%S.%f")
            time_difference = (ctime - datetime.strptime(old_dt_str, "%Y-%m-%d_%H:%M:%S.%f")).total_seconds() * 1000.0

            msg_dict = {
                "msg_id": hex(msg.arbitration_id),
                "msg_data": [hex(byte) for byte in msg.data],
                "timestamp": dt_str,
                "delay": time_difference,
            }
            self.trace_buffer[msg.arbitration_id] = msg_dict

    def _read_messages(self):
        """Read and decode CAN messages"""
        while self._running.is_set():
            try:
                msg = self._bus.recv(timeout=1)
                self.add_to_trace_buffer(msg)
                if(self.save_trace_file == True):
                    self.send_to_trace(id=msg.arbitration_id,data_list=list(msg.data))
                decoded_dict = self._db.decode_message(msg.arbitration_id, msg.data)
                # print(decoded_dict)
                with self._lock:
                    for k in decoded_dict.keys():
                        self.data_dict[str(msg.arbitration_id)+"_"+str(k)]=decoded_dict[k]                    
            except Exception as e:
                print(f"Error reading CAN message: {e}")

    ### function to update local data dictionary in global data interface
    def update_data_in_data_interface(self):
        while(1):
            try:
                with self._lock:
                    self.data_interface.update_data(self.data_dict)
            except:
                pass
            sleep(self.global_data_update_interval)

    def get_messages(self):
        """Get all stored messages"""
        with self._lock:
            return self.data_dict.copy()

    def clear_messages(self):
        """Clear stored messages"""
        for k in self.data_dict.keys():
            self.data_dict[k] = -1
    
    def start_trace_file_save(self):
        if self.trace_file_name:
            dateString = str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_"))                
            self.trace_file_path = os.path.join(self.data_interface.data_folder_path,dateString+"_"+str(self.trace_file_name)+".csv")
        else:
            dateString = str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S_"))                
            self.trace_file_path = os.path.join(self.data_interface.data_folder_path,dateString+"_"+str(self.hw_channal)+"_trace.csv")
        
        self.trace_csv_file=open(self.trace_file_path, "a")   
        date = "Date"
        time = "Time"
        ms="Microseconds"
        msg_id="Message_ID"
        msg_data0="D_Byte0"
        msg_data1="D_Byte1"
        msg_data2="D_Byte2"
        msg_data3="D_Byte3"
        msg_data4="D_Byte4"
        msg_data5="D_Byte5"
        msg_data6="D_Byte6"
        msg_data7="D_Byte7"

        self.trace_csv_file.write(
            "{},{},{},{},{},{},{},{},{},{},{},{}\n".format(date, time,ms, msg_id,
                                                           msg_data0,msg_data1,msg_data2,msg_data3,
                                                           msg_data4,msg_data5,msg_data6,msg_data7)
        )
        self.trace_csv_file.close()
        self.save_trace_file=True
    
    ### takes input as integer msg id and data list and save as hex formats
    def send_to_trace(self,id,data_list):
        id_hex= hex(id)
        hex_byte0=hex(data_list[0])
        hex_byte1=hex(data_list[1])
        hex_byte2=hex(data_list[2])
        hex_byte3=hex(data_list[3])
        hex_byte4=hex(data_list[4])
        hex_byte5=hex(data_list[5])
        hex_byte6=hex(data_list[6])
        hex_byte7=hex(data_list[7])

        self.trace_csv_file=open(self.trace_file_path, "a")                            
        ctime = datetime.now()
        date = ctime.strftime("%Y-%m-%d")
        time = ctime.strftime("%H:%M:%S")
        ms=ctime.strftime("%H:%M:%S.%f")[-6:]  
        self.trace_csv_file.write(
            "{},{},{},{},{},{},{},{},{},{},{},{}\n".format(date, time, ms, id_hex,
                                                          hex_byte0, hex_byte1, hex_byte2, hex_byte3,
                                                          hex_byte4, hex_byte5, hex_byte6, hex_byte7)
        )

        self.trace_csv_file.close()

    def stop_trace_file_save(self):
        self.save_trace_file =False

    def send_msg(self, msg_id, data,extended_id=False):
        """Send CAN message"""
        if self._bus:
            try:
                msg = can.Message(arbitration_id=msg_id, data=data, is_extended_id=extended_id)
                self._bus.send(msg)
                return True
            except Exception as e:
                print(f"Error sending CAN message: {e}")
                return False
        return False

    def send_msg_periodic(self, msg_id, data, extended_id=False, interval_ms=-1, duration_ms=-1):
        """Send CAN message periodically
        Args:
            msg_id: Message ID
            data: Message data bytes
            extended_id: Whether to use extended ID format
            interval_ms: Interval between messages in milliseconds. -1 for one-shot
            duration_ms: Duration to send messages for in milliseconds. -1 for infinite
        """
        if interval_ms <= 0:  # One-shot message
            return self.send_msg(msg_id, data, extended_id)

        # Create stop event
        msg_key = f"{msg_id}_{interval_ms}"
        if msg_key in self._periodic_msgs:
            self.stop_periodic_msg(msg_id, interval_ms)  # Stop existing periodic send
            
        stop_event = Event()
        self._periodic_events[msg_key] = stop_event

        def send_periodic():
            start_time = time.time()
            while not stop_event.is_set():
                if duration_ms > 0 and (time.time() - start_time) * 1000 >= duration_ms:
                    break
                self.send_msg(msg_id, data, extended_id)
                time.sleep(interval_ms / 1000.0)

        # Start periodic sending thread
        thread = Thread(target=send_periodic)
        thread.daemon = True
        thread.start()
        self._periodic_msgs[msg_key] = thread
        return True

    def stop_periodic_msg(self, msg_id, interval_ms):
        """Stop periodic message sending for given ID and interval"""
        msg_key = f"{msg_id}_{interval_ms}"
        if msg_key in self._periodic_events:
            self._periodic_events[msg_key].set()  # Signal thread to stop
            if msg_key in self._periodic_msgs:
                self._periodic_msgs[msg_key].join(timeout=1.0)  # Wait for thread to finish
                del self._periodic_msgs[msg_key]
            del self._periodic_events[msg_key]
            return True
        return False

