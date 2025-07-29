"""
Helper functions for Validatrix operations.
"""

def validate_input(value, min_val, max_val, name="input"):
    """
    Validate if a value is within the specified range.
    
    Args:
        value: The value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Name of the parameter for error message
        
    Returns:
        bool: True if value is valid
        
    Raises:
        ValueError: If value is outside the valid range
    """
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} must be between {min_val} and {max_val}")
    return True

def convert_voltage(digital_value, vref=3.3, resolution=12):
    """
    Convert a digital value to voltage.
    
    Args:
        digital_value: Digital value to convert
        vref: Reference voltage (default: 3.3V)
        resolution: DAC resolution in bits (default: 12)
        
    Returns:
        float: Voltage value in volts
    """
    max_value = (1 << resolution) - 1
    return (digital_value / max_value) * vref

def format_message(msg_id, data, length=8):
    """
    Format a CAN message with proper padding.
    
    Args:
        msg_id: CAN message ID
        data: Message data
        length: Expected message length (default: 8 bytes)
        
    Returns:
        bytes: Formatted message data
    """
    if len(data) > length:
        raise ValueError(f"Data length exceeds maximum length of {length} bytes")
    return data + b'\x00' * (length - len(data)) 