# -*- coding: utf-8 -*-

import time

from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_driver import CrcCalculator
from sensirion_i2c_sf06_lf.commands import InvFlowScaleFactors
from sensirion_i2c_sf06_lf.device import Sf06LfDevice
from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection

from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice

with ShdlcSerialPort(port='COM5', baudrate=115200) as port:
    bridge = Scc1ShdlcDevice(ShdlcConnection(port), slave_address=0)

    channel = I2cChannel(bridge.get_i2c_transceiver(),
                         slave_address=0x08,
                         crc=CrcCalculator(8, 0x31, 0xff, 0x0))

    sensor = Sf06LfDevice(channel)
    try:
        sensor.stop_continuous_measurement()
        time.sleep(0.1)
    except BaseException:
        ...
    (product_identifier, serial_number
     ) = sensor.read_product_identifier()
    print(f"product_identifier: {product_identifier}; " f"serial_number: {serial_number}; ")
    sensor.start_h2o_continuous_measurement()
    for i in range(500):
        try:
            time.sleep(0.02)
            (a_flow, a_temperature, a_signaling_flags
             ) = sensor.read_measurement_data(InvFlowScaleFactors.SLF3C_1300F)
            print(f"a_flow: {a_flow}; " f"a_temperature: {a_temperature}; " f"a_signaling_flags: {a_signaling_flags}; ")
        except BaseException:
            continue
    sensor.stop_continuous_measurement()
