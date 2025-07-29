from ..data_collection import *
from time import sleep
from threading import Thread, Event
import threading
try:
    import RPi.GPIO as GPIO
except:
    pass

class Internal_DigitalReadInterface:
    def __init__(self,name=None,type=None,GPIO_pin=None,inverted_logic=True,
                 data_interface:DataCollectionInterface=None,register_for_log=False):

        self.name=name       
        self.data_interface = data_interface
        self.type=type
        self.inverted_logic_flag=inverted_logic
        self.state=-1       
        self.data_dict={"Feedback":self.state}     
        self.register_for_log=register_for_log
        self.GPIO_pin=GPIO_pin
        self._lock = threading.Lock()
        self._Updatethread = None
        self._running = Event()
        
         ### if data collection interface is available, register dictionary for monitoring
        if(self.data_interface):
            self.data_interface.register_for_data_collection(self.data_dict,self.register_for_log,logger_name=str(self.name))
            self.data_interface.update_data(self.data_dict,logger_name=str(self.name))
        
        try:
            self.initialize()
        except:
            pass
        
        
        
    def initialize(self):
        """
        Initialize the DigitalReadInterface.        
        """
        try:
            if(self.type =="GPIO_continuity_check"):
                # Use BCM pin numbering
                GPIO.setmode(GPIO.BCM)  
                # Set up the pin as an input
                GPIO.setup(self.GPIO_pin, GPIO.IN,pull_up_down=GPIO.PUD_UP) # Set pull-up resistor

            self._running.set()

            self._Updatethread = Thread(target=self.update_state_function)
            self._Updatethread.daemon = True
            self._Updatethread.start()
        except:
            pass
    
    def update_state_function(self):
        """
        Update the state of the digital input pin.
        """
        while(1):
            if(self._running.is_set() == False):
                break
            try:
                if(self.type =="GPIO_continuity_check"):
                    # Read the state of the pin
                    if GPIO.input(self.GPIO_pin) == GPIO.LOW:
                        self.state=1 if self.inverted_logic_flag else 0
                    else:
                        self.state=0 if self.inverted_logic_flag else 1
                
                # Update the data dictionary with the new state
                self.data_dict["Feedback"]=self.state
                
                # Update the data collection interface if available
                if(self.data_interface):
                    self.data_interface.update_data(self.data_dict,logger_name=str(self.name))
            except:
                pass
            sleep(0.05)

    def get_state(self):
        """
        Get the current state of the digital input pin.
        """
        with self._lock:
            return self.state
    
    def stop(self):
        """
        Stop the DigitalReadInterface and clean up GPIO settings.
        """
        try:
            GPIO.cleanup()
            self._running.clear()
            sleep(0.1)
            if self._Updatethread is not None:
                self._Updatethread.join()
        except:
            pass    
        
        
        

        
        
        
