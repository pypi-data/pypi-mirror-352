import time
from typing import *
from .usbcdc_base import UsbCdcBase
from .usbcdc_device_info import UsbCdcDeviceInfo
from .usbcdc_device_address import UsbCdcDeviceAddress
from .usbcdc_exception import *
import usb.core
import usb.util

class UsbCdcDevice(UsbCdcBase):
    @classmethod
    def get_backend(cls):
        import usb.backend.libusb1
        backend = usb.backend.libusb1.get_backend()

        if backend is None:
            # No standard backend found, try loading one from libusb package
            try:
                import libusb
                backend = usb.backend.libusb1.get_backend(find_library=lambda x: libusb.dll._name)
            except:
                pass

        return backend

    @classmethod
    def list_devices(cls, usb_vid: Optional[int] = None, usb_pid: Optional[int] = None) -> List[UsbCdcDeviceInfo]:
        def match(dev):
            for cfg in dev:
                d = usb.util.find_descriptor(
                    cfg,
                    bInterfaceClass=UsbCdcBase.USBCDC_INTERFACE_CLASS,
                    bInterfaceSubClass=UsbCdcBase.USBCDC_INTERFACE_SUBCLASS)

                if d is None:
                    # Must have (at least) one interface with USBCDC_INTERFACE_CLASS/SUBCLASS
                    return False

                return True

        # Get a backend for searching USB devices
        backend = cls.get_backend()
        matches = {'custom_match': match}
        if usb_vid is not None: matches.update({'idVendor': usb_vid})
        if usb_pid is not None: matches.update({'idProduct': usb_pid})

        # usb.core.find returns an empty list when backend is None (i.e. no backend available)
        # thus silently ignoring the UsbCdc list_devices functionality
        return [UsbCdcDeviceInfo.from_device(device) for device in usb.core.find(backend=backend, find_all=True, **matches)]

    def __init__(self,
                 address: UsbCdcDeviceAddress,
                 timeout: Optional[float] = None,
                 transfer_size_max: Optional[int] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self._opened = False
        self._reattach_kernel_driver = []
        self._union_desc = self._header_desc = None
        self._ep_bulk_in = self._ep_bulk_out = self._ep_intr_in = None
        self._timeout_ms = int(timeout*1000) if timeout is not None else UsbCdcBase.DEFAULT_TIMEOUT_MS
        self._address = address
        self._transfer_size_max = \
            transfer_size_max if transfer_size_max is not None else UsbCdcBase.DEFAULT_TRANSFER_SIZE_MAX
        self._backend = self.get_backend()

        if self._backend is None:
            raise UsbCdcConnectionException('No suitable backend for USB communication found')

        # Open device
        if self._address.serial_number is not None:
            self._device = usb.core.find(backend=self._backend,
                                         idVendor=self._address.vid, idProduct=self._address.pid,
                                         serial_number=self._address.serial_number)
        else:
            self._device = usb.core.find(backend=self._backend,
                                         idVendor=self._address.vid, idProduct=self._address.pid)

        if self._device is None:
            raise UsbCdcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' was not found') from None

        # find first USB CDC interface with matching INTERFACE_CLASS/SUBCLASS
        # and matching bInterfaceNumber (if it is given)
        for cfg in self._device:
            for iface in cfg:
                if     (iface.bInterfaceClass == UsbCdcBase.USBCDC_INTERFACE_CLASS and
                        iface.bInterfaceSubClass == UsbCdcBase.USBCDC_INTERFACE_SUBCLASS and
                        (self._address.interface_number is None or iface.bInterfaceNumber == self._address.interface_number)):
                    self._configuration = cfg
                    self._cic_interface = iface
                    break
            else:
                # Inner loop was not broken
                continue

            # Inner loop was broken
            break
        else:
            raise UsbCdcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' has no registered USB CDC interface') from None
            pass


        # find the corresponding CDC union header 
        cdc_descriptors = bytes(self._cic_interface.extra_descriptors)
        bytes_left = len(cdc_descriptors)
        while len(cdc_descriptors) > 0:
            desc_length = cdc_descriptors[0]
            desc_type = cdc_descriptors[1]
            desc_subtype = cdc_descriptors[2]

            if (desc_type == UsbCdcBase.USBCDC_CLASS_INTERFACE_TYPE) and (desc_subtype == UsbCdcBase.USBCDC_HEADER_SUBTYPE):
                # Header descriptor
                self._header_desc = UsbCdcBase.HeaderDescriptor.parse(cdc_descriptors[3:])
            elif (desc_type == UsbCdcBase.USBCDC_CLASS_INTERFACE_TYPE) and (desc_subtype == UsbCdcBase.USBCDC_UNION_SUBTYPE):
                # Union descriptor
                self._union_desc = UsbCdcBase.UnionDescriptor.parse(cdc_descriptors[3:])

            cdc_descriptors = cdc_descriptors[desc_length:]

        if self._union_desc is None:
            raise UsbCdcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' is missing a CDC union descriptor') from None

        if self._union_desc.bMasterInterface != self._cic_interface.bInterfaceNumber:
            raise UsbCdcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' has an unmatched CDC union descriptor (m: {self._union_desc.bMasterInterface}, s: {self._union_desc.bSlaveInterface0})') from None

        # Get interface object for data class
        for iface in self._configuration:
            if (iface.bInterfaceNumber == self._union_desc.bSlaveInterface0):
                self._dic_interface = iface
                break
        else:
            raise UsbCdcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + f' has no corresponding data class interface (interface {self._union_desc.bSlaveInterface0})') from None
            pass

        # Find bulk endpoints
        for ep in self._dic_interface:
            ep_dir = usb.util.endpoint_direction(ep.bEndpointAddress)
            ep_type = usb.util.endpoint_type(ep.bmAttributes)

            if ep_type == usb.util.ENDPOINT_TYPE_BULK and ep_dir == usb.util.ENDPOINT_IN:
                self._ep_bulk_in = ep
            elif ep_type == usb.util.ENDPOINT_TYPE_BULK and ep_dir == usb.util.ENDPOINT_OUT:
                self._ep_bulk_out = ep

        if self._ep_bulk_in is None or self._ep_bulk_out is None:
            raise UsbCdcConnectionException(
                f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                + ' is missing at least one required endpoint') from None
            pass

        try:
            if self._device.is_kernel_driver_active(self._cic_interface.index):
                self._reattach_kernel_driver.append(self._cic_interface)

                try:
                    self._device.detach_kernel_driver(self._cic_interface.index)
                except usb.core.USBError as e:
                    raise UsbCdcConnectionException(
                        f'USB device with VID:PID {self._address.vid:04x}:{self._address.pid:04x}'
                        + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                        + f' could not be detached from kernel driver at interface index {self._cic_interface.index} ({e})') from None
        except NotImplementedError:
            # We are on a platform that does not implement kernel driver detach/attach, just ignore then
            pass

        # claim interfaces
        usb.util.claim_interface(self._device, self._cic_interface)
        usb.util.claim_interface(self._device, self._dic_interface)

        self._opened = True


    def write(self, data: bytes) -> int:
        if not self._opened:
            raise UsbCdcConnectionException('Connection is not open') from None

        try:
            self._ep_bulk_out.write(data, timeout=self._timeout_ms)
        except usb.core.USBTimeoutError:
            raise UsbCdcTimeoutException('Timeout during bulk out write') from None

        return len(data)

    def read(self, num: int = -1, term_char: bytes = None) -> bytes:
        if not self._opened:
            raise UsbCdcConnectionException('Connection is not open') from None

        remaining = num
        index = 0

        # Allocate read buffer ahead of time if length is known, else zero-length array
        data = bytearray(num) if num > 0 else bytearray()

        while remaining != 0:
            # Receive the requested data from the device either with known number of bytes or maximum transfer size
            transfer_size = remaining if 0 < remaining < self._transfer_size_max else self._transfer_size_max

            try:
                buf = self._ep_bulk_in.read(transfer_size, timeout=self._timeout_ms)
                buffer_view = memoryview(buf)
                buffer_len = len(buf)
            except usb.core.USBTimeoutError:
                raise UsbCdcTimeoutException('Timeout during bulk in read') from None

            # Data processing depends on whether we already know the length of data or not
            if remaining < 0:
                # Append data to data array in endless read mode
                data.extend(buffer_view[:buffer_len])
            else:
                # Copy over data in known-length mode
                data[index:index + buffer_len] = buffer_view[:buffer_len]

                # Track remaining data length
                remaining = (remaining - buffer_len) if remaining > buffer_len else 0

            # In any case, abort if buffer ends with term_char
            if (term_char is not None) and (bytes(buffer_view[-len(term_char):]) == term_char):
                remaining = 0

            # Advance variables for next transfer
            index += buffer_len

        return data

    def readline(self, size: int = -1, term_char: Optional[bytes] = None) -> bytes:
        return self.read(size, term_char=term_char if term_char is not None else UsbCdcBase.DEFAULT_TERM_CHAR)

    def writelines(self, lines: Iterable[bytes]) -> None:
        for line in lines:
            self.write(line)

    def close(self) -> None:
        if not self._opened:
            return

        usb.util.release_interface(self._device, self._cic_interface)
        usb.util.release_interface(self._device, self._dic_interface)
        usb.util.dispose_resources(self._device)

        # reattach kernel driver
        for iface in self._reattach_kernel_driver:
            try:
                self._device.attach_kernel_driver(iface.index)
            except usb.core.USBError as e:
                raise UsbCdcConnectionException(
                    f'USB device with VID:PID {self._address.vid}:{self._address.pid}'
                    + (f' (serial number: {self._address.serial_number})' if self._address.serial_number is not None else '')
                    + f' could not be reattached to kernel driver at interface index {iface.index} ({str(e)})') from None

        self._reattach_kernel_driver = []
        self._opened = False

    @property
    def closed(self) -> bool:
        return True if not self._opened else False

    def __del__(self):
        self.close()
        pass
