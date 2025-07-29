import os
import importlib.util
import inspect
from ..data_collection import *
import datetime

class AutomatedTestInterface:
    def __init__(self, tests_folder_path=None, data_interface:DataCollectionInterface=None):
        self.name = self.__class__.__name__
        self.test_classes = []
        self.tests_folder_path = tests_folder_path        
        self.data_interface_obj = data_interface


    def load_tests(self):
        print("in load test function")
        self.test_classes = []
        for file in os.listdir(self.tests_folder_path):
            if file.endswith(".py") and file != "__init__.py":
                module_name = file[:-3]  # remove .py
                module_path = os.path.join(self.tests_folder_path, file)
                print("Loading module:", module_name, "from path:", module_path)
                
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, 'is_test_class') and obj.is_test_class:
                        self.test_classes.append(obj)

    




