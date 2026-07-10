# -*- coding: utf-8 -*-
import re

import pytest


@pytest.mark.needs_hardware
def test_scc1_device(scc1_device):
    assert scc1_device is not None
    assert re.match("SCC1-([^@])*@*", str(scc1_device))


@pytest.mark.needs_hardware
def test_scc1_baudrate(scc1_device):
    baudrate = scc1_device.get_baudrate()
    assert isinstance(baudrate, int)
    # Test setting it back to the same value
    scc1_device.set_baudrate(baudrate)


@pytest.mark.needs_hardware
def test_scc1_i2c_delay(scc1_device):
    delay = scc1_device.get_i2c_delay()
    assert isinstance(delay, int)
    scc1_device.set_i2c_delay(delay)


@pytest.mark.needs_hardware
def test_scc1_user_data(scc1_device):
    data = scc1_device.get_user_data(0)
    assert isinstance(data, bytes)
    assert len(data) == 20
    scc1_device.set_user_data(0, data)


def test_scc1_user_data_invalid_block():
    from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice
    from unittest.mock import MagicMock
    # Mock connection to return something for execute to avoid initialization errors
    connection = MagicMock()
    connection.execute.return_value = (b'', 0)
    device = Scc1ShdlcDevice(connection)
    with pytest.raises(ValueError, match="Block number must be between 0 and 4."):
        device.get_user_data(5)
    with pytest.raises(ValueError, match="Block number must be between 0 and 4."):
        device.set_user_data(5, b'0' * 20)
    with pytest.raises(ValueError, match="User data must be 20 bytes long."):
        device.set_user_data(0, b'0' * 19)


def test_scc1_get_user_data_parsing():
    from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice
    from unittest.mock import MagicMock
    connection = MagicMock()
    # Correct response: block number 2 followed by 20 bytes of 'A'
    mock_data = b'\x02' + b'A' * 20
    # Initialization calls: get_version, get_serial_number, get_sensor_type, get_sensor_address
    # Then get_user_data
    connection.execute.side_effect = [
        (b'\x01\x02\x00\x01\x02\x03', 0),  # get_version (6 bytes)
        (b'123456', 0),                 # get_serial_number
        (b'\x03', 0),                    # get_sensor_type (1 byte)
        (b'\x10', 0),                    # get_sensor_address (1 byte)
        (mock_data, 0),                 # get_user_data (first call)
        (mock_data, 0),                 # get_user_data (second call)
        (b'\x02' + b'A' * 19, 0),       # get_user_data (third call, wrong length)
    ]
    device = Scc1ShdlcDevice(connection)

    # Test successful parsing
    data = device.get_user_data(2)
    assert data == b'A' * 20

    # Test block number mismatch
    with pytest.raises(ValueError, match="Received block number 2 does not match requested block 1"):
        device.get_user_data(1)

    # Test invalid response length
    with pytest.raises(ValueError, match="Unexpected response length for User Data: 20 bytes"):
        device.get_user_data(2)


@pytest.mark.needs_hardware
def test_scc1_device_selftest(scc1_device):
    result = scc1_device.device_selftest()
    assert isinstance(result, int)


@pytest.mark.needs_hardware
def test_scc1_sensor_voltage(scc1_device):
    voltage = scc1_device.get_sensor_voltage()
    assert voltage in [0, 1]
    scc1_device.set_sensor_voltage(voltage)


@pytest.mark.needs_hardware
def test_scc1_measure_sensor_voltage(scc1_device):
    voltage_mv = scc1_device.measure_sensor_voltage()
    assert isinstance(voltage_mv, int)
    assert 3000 <= voltage_mv <= 6000
