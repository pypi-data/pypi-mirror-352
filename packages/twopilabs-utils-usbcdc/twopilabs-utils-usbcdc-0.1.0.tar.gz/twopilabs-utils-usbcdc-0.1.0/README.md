USB Communication Device Class (CDC) implementation in python using PyUSB
=================================================
A generic (i.e. non-specific) implementation of a USB CDC host client software to talk to USB devices implementing the CDC class instead of reyling on OS provided class drivers.

This library can beneficially be used with the WinUSB and WCID features of Windows to workaround known issues with the Microsoft CDC driver at high data rates.

See https://stackoverflow.com/questions/67804128/stm32-usb-cdc-some-data-lost-with-win-10
