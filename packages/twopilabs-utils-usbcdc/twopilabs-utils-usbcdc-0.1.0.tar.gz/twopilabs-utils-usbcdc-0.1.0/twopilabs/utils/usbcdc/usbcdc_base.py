from typing import *
from enum import Enum, Flag
import struct
import io

class UsbCdcBase(io.RawIOBase):
    USBCDC_INTERFACE_CLASS                      = 0x02
    USBCDC_INTERFACE_SUBCLASS                   = 0x02
    USBCDC_INTERFACE_PROTOCOL                   = 0x00

    USBCDC_CLASS_INTERFACE_TYPE                 = 0x24
    USBCDC_CLASS_ENDPOINT_TYPE                  = 0x25
    USBCDC_HEADER_SUBTYPE                       = 0x00
    USBCDC_CALLMGMT_SUBTYPE                     = 0x01
    USBCDC_ACM_SUBTYPE                          = 0x02
    USBCDC_UNION_SUBTYPE                        = 0x06

    DEFAULT_TIMEOUT_MS                          = 5000
    DEFAULT_BTAG                                = 1
    DEFAULT_TRANSFER_SIZE_MAX                   = 1024 * 1024
    DEFAULT_TERM_CHAR                           = '\n'.encode('ascii')

    class HeaderDescriptor(NamedTuple):
        bcdCDC: int
        
        @classmethod
        def struct(cls) -> struct.Struct:
            # Return a Python struct object for parsing the binary header into the named tuple
            return struct.Struct('<H')

        @classmethod
        def size(cls) -> int:
            return cls.struct().size

        @classmethod
        def parse(cls, buffer: bytes) -> 'UsbCdcBase.HeaderDescriptor':
            fields = cls.struct().unpack(buffer[0:cls.struct().size])
            return cls(*fields)

    class UnionDescriptor(NamedTuple):
        bMasterInterface: int
        bSlaveInterface0: int
        
        @classmethod
        def struct(cls) -> struct.Struct:
            # Return a Python struct object for parsing the binary header into the named tuple
            return struct.Struct('<BB')

        @classmethod
        def size(cls) -> int:
            return cls.struct().size

        @classmethod
        def parse(cls, buffer: Iterable) -> 'UsbCdcBase.UnionDescriptor':
            fields = cls.struct().unpack(buffer[0:cls.struct().size])
            return cls(*fields)

    def __init__(self, *args, **kwargs):
        pass
        
    def readlines(self, hint: int = ...) -> List[AnyStr]:
        # Don't support reading until EOF
        raise io.UnsupportedOperation
        
    def isatty(self) -> bool:
        # Report as interactive
        return True
    
    def fileno(self) -> int:
        # Dont support a file object from OS
        raise OSError()

    def flush(self) -> None:
        # Flush is a NOP
        pass

    def readable(self) -> bool:
        # Stream is readable
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        # No seeking supported
        raise io.UnsupportedOperation

    def seekable(self) -> bool:
        # No seeking supported
        return False

    def tell(self) -> int:
        # No seeking supported
        raise OSError()

    def truncate(self, size: Optional[int] = ...) -> int:
        # No seeking supported
        raise OSError()

    def writable(self) -> bool:
        # Stream is writeable
        return True

    def __next__(self) -> AnyStr:
        # Don't support iterating over lines
        raise io.UnsupportedOperation

    def __iter__(self) -> Iterator[AnyStr]:
        # Don't support iterating over lines
        raise io.UnsupportedOperation

    def readall(self) -> bytes:
        # Don't support reading until EOF    
        raise io.UnsupportedOperation
