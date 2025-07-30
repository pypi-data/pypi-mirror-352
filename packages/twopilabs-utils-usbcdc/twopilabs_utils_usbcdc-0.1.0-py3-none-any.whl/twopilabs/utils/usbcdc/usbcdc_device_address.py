from typing import *

class UsbCdcDeviceAddress(NamedTuple):
    vid: int
    pid: int
    serial_number: Optional[str]
    interface_number: Optional[int]
    
