
class UsbCdcException(Exception):
    """Generic USBTMC Exception"""
    pass
    
class UsbCdcConnectionException(UsbCdcException):
    """Exception raised in the context of a USB CDC connection"""
    pass
    
class UsbCdcTimeoutException(UsbCdcException):
    """Exception raised when an operation timed out"""
    pass

