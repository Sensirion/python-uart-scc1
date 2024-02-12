# python-uart-scc1
This repository provides a Python driver for [Sensirion SCC1-USB Cable](https://www.sensirion.com/products/catalog/SCC1-USB/).
The detailed technical description of the SCC1-USB cable is provided in the [datasheet](https://www.sensirion.com/media/documents/EE77392F/65290BF6/LQ_DS_SCC1-RS485-USB_Datasheet.pdf).

## Feature overview

On one hand the SCC1-USB exposes an API to efficiently use the supported sensors. So far
support is only added for the [SLF3x-Sensor family](https://sensirion.com/products/catalog/SLF3C-1300F).

On the other hand the cable can be used as USB to I2c bridge for any Sensirion I2c sensor that can be plugged to the cable.

**Note**: Using the cable as USB to I2c bridge will not allow to achieve the same throughput as with the embedded API.

## 


