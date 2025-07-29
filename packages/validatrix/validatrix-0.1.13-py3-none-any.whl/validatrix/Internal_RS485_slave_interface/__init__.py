"""
RS485 slave Interface module for Validatrix.
Provides functionality for RS485 slave emulation
"""

from .Internal_RS485_slave import *
from .Internal_RS485_slave_server import *
from .Internal_RS485_device_data import *

__all__ = [
    'Internal_RS485_slave_class',
    'Internal_RS485_slave_server_class',
] 