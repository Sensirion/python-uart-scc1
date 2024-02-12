# -*- coding: utf-8 -*-
import pytest
from serial.tools.list_ports import comports
from sensirion_shdlc_driver.connection import ShdlcConnection
from sensirion_shdlc_driver.port import ShdlcSerialPort
from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice


@pytest.fixture
def scc1_device():
    for port_info in comports():
        try:
            shdlc_port = ShdlcSerialPort(port=port_info.device, baudrate=115200)
            with shdlc_port:
                try:
                    device = Scc1ShdlcDevice(ShdlcConnection(shdlc_port), 0)
                    device.get_product_name()
                    yield device
                    device.sensor_reset()
                    return
                except: # noqa
                    ...
        except: # noqa
            ...
