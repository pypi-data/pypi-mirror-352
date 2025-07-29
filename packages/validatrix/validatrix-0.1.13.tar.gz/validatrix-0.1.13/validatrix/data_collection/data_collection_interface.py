import csv
import datetime
import os
from threading import Thread, Event
import threading
from time import sleep

class DataCollectionInterface:
    ### here csv file is all data log file which will print in it at a specific interval with watever data
    #### available at the time.
    #### txt file is test log to save the event timings and understand pass/fail with 
    #### print statements 
    def __init__(self,data_folder_path=None,data_csv_file_name=None,data_txt_file_name=None):
        self.all_data_dict={}
        self.csv_log_column_list=[]

        if(data_csv_file_name==None):
            self.data_csv_file_name = "data_log_csv"
        else:
            self.data_csv_file_name = data_csv_file_name

        if(data_txt_file_name==None):
            self.data_txt_file_name = "test_log_txt"
        else:
            self.data_txt_file_name = data_txt_file_name
        
        self.csv_path=None
        self.txt_path=None
        self.csv_file=None
        self.txt_file=None
        self.test_log=""

        self.data_folder_path=data_folder_path
        if not os.path.exists(data_folder_path):
            os.makedirs(data_folder_path)

        if self.data_folder_path and os.path.exists(self.data_folder_path): 
            dateString = str(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S_"))                
            self.txt_path = os.path.join(self.data_folder_path,dateString+"_"+str(self.data_txt_file_name)+".txt")
            
        
        self.csv_log_interval=0.1 ## sec
        self.txt_log_delay=0 ### sec
        self._csv_log_state = Event()
        self._csv_file_headers=Event()
        self.csv_thread=None
        self.data_lock = threading.Lock()

    #### funcion to register any dictinary for global data monitoring 
    #### csv_log_flag indicates if the dictionary is also to be
    #### added into csv log columns or not      
    def register_for_data_collection(self,data_dictionary,csv_log_flag=False,logger_name=""):
        for c in data_dictionary.keys():
            self.all_data_dict[str(logger_name)+"___"+str(c)] = -1
            if(csv_log_flag):
                self.csv_log_column_list.append(str(logger_name)+"___"+str(c))

    ### funcion to update global data dictionary from any logger module
    def update_data(self,input_data_dict,logger_name=""):
        with self.data_lock:
            for k in input_data_dict.keys():
                if((str(logger_name)+"___"+str(k)) in self.all_data_dict.keys()):
                    self.all_data_dict[str(logger_name)+"___"+str(k)]=input_data_dict[k]


    def csv_log(self):
        while(1):
            try:
                if(self._csv_log_state.is_set()):
                    #### add column names if not added already.first time
                    if(not self._csv_file_headers.is_set()):
                        self.csv_file=open(self.csv_path, "a")   

                        date = "Date"
                        time = "Time"
                        ms="Microseconds"
                        cloumn_list=sorted(self.csv_log_column_list)                 
                        a = ""
                        for l in cloumn_list:
                            a=a+l+","                   
                        a=a[:-1]             
                        
                        self.csv_file.write(
                            "{},{},{},{}\n".format(date, time,ms, a)
                        )
                        self.csv_file.close()
                        self._csv_file_headers.set()
                    ### add data values
                    else:
                        self.csv_file=open(self.csv_path, "a")                            
                        ctime = datetime.datetime.now()
                        date = ctime.strftime("%Y-%m-%d")
                        time = ctime.strftime("%H:%M:%S")
                        ms=ctime.strftime("%H:%M:%S.%f")[-6:]                   
                        all_sig_list=sorted(self.csv_log_column_list)
                        data_list=[]
                        for k in all_sig_list:
                            data_list.append(self.all_data_dict[k])
                        a = str(data_list)[1:-1]                
                        self.csv_file.write(
                            "{},{},{},{}\n".format(date, time,ms, a)
                        )
                        self.csv_file.close()
            except:
                pass
            sleep(self.csv_log_interval)

    def start_csv_log(self):
        if self.data_folder_path and os.path.exists(self.data_folder_path): 
            try:
                dateString = str(datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S_"))    
                self.csv_path = os.path.join(self.data_folder_path,dateString+"_"+str(self.data_csv_file_name)+".csv")
                self.csv_thread = Thread(target=self.csv_log)
                self.csv_thread.daemon = True
                self.csv_thread.start()
                self._csv_log_state.set()
                self._csv_file_headers.clear()
                return True
            except:
                return False

        else:
            return False    

    def stop_csv_log(self):
        self._csv_log_state.clear()
        
       
    def print_with_log(self,input_str):
        ctime = datetime.datetime.now()
        dt_str = ctime.strftime("%Y-%m-%d_%H:%M:%S.%f")
        in_str=str(input_str)
        print(in_str)
        self.test_log += "{}: {}\n".format(dt_str, in_str)
        try:
            sleep(self.txt_log_delay)
            self.txt_file=open(self.txt_path, "a")        
            self.txt_file.write(
                "{},{}\n".format(dt_str, in_str)
            )
            self.txt_file.close()
        except:
            pass

    def get_data_dict(self):
        """Get all stored messages"""
        with self.data_lock:
            return self.all_data_dict.copy()
    
    def get_data_value(self, signal_name):
        """Get a specific message by name"""
        with self.data_lock:
            return self.all_data_dict.get(signal_name, None)
        

        
        
        
