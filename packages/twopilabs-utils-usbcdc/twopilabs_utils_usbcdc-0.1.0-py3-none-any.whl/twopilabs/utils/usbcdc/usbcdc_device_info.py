from typing import *
import usb.core
import usb.util
from .usbcdc_device_address import UsbCdcDeviceAddress
from .usbcdc_base import UsbCdcBase


class UsbCdcDeviceInfo(NamedTuple):
    manufacturer: str
    product: str
    serial_number: str
    address: UsbCdcDeviceAddress
    location: str
    
    @classmethod
    def from_device(cls, device: usb.core.Device) -> 'UsbCdcDeviceInfo':
        interfaces = []
        for cfg in device:
            interfaces.extend(usb.util.find_descriptor(
                    cfg,
                    find_all=True,
                    bInterfaceClass=UsbCdcBase.USBCDC_INTERFACE_CLASS,
                    bInterfaceSubClass=UsbCdcBase.USBCDC_INTERFACE_SUBCLASS))

        # Returns first interface found in configuration descriptors
        return cls(
            manufacturer=device.manufacturer,
            product=device.product,
            serial_number=device.serial_number,
            address=UsbCdcDeviceAddress(
                vid=device.idVendor,
                pid=device.idProduct,
                serial_number=device.serial_number,
                interface_number=interfaces[0].bInterfaceNumber),
            location=f'{device.bus}-{".".join([str(n) for n in device.port_numbers])}:{device.address}'
        )
