# -*- coding: utf-8 -*-

import logging
import struct
from struct import unpack
from typing import Optional, Iterable, Union, List

from packaging.version import Version
from sensirion_shdlc_driver import ShdlcDevice, ShdlcConnection
from sensirion_shdlc_driver.command import ShdlcCommand

from sensirion_uart_scc1.protocols.i2c_transceiver import I2cTransceiver
from sensirion_uart_scc1.scc1_i2c_transceiver import Scc1I2cTransceiver

log = logging.getLogger(__name__)


class Scc1ShdlcDevice(ShdlcDevice):
    """
    The Scc1 SHDLC device is used to communicate with various sensors using the Sensirion SCC1 sensor cable.
    """

    def __init__(self, connection: ShdlcConnection, target_address: int = 0) -> None:
        """Initialize SCC1 SHDLC Device.

        :param connection: The used ShdlcConnection
        :param target_address: The SHDLC target address used by this device (default: 0).
                               Usually 0 unless multiple devices are connected to the same USB port.
        """
        super().__init__(connection, target_address)
        self._version = self.get_version()
        self._serial_number = self.get_serial_number()
        self._sensor_type = self.get_sensor_type()
        self._i2c_address = self.get_sensor_address()
        self._connected_i2c_addresses: List[int] = []

    def __str__(self) -> str:
        return f"SCC1-{self.serial_number}@{self.com_port}"

    @property
    def com_port(self) -> str:
        return self.connection.port.description.split('@')[0]

    @property
    def serial_number(self) -> str:
        return self._serial_number

    @property
    def firmware_version(self) -> Version:
        return Version(str(self._version.firmware))

    @property
    def connected_i2c_addresses(self) -> List[int]:
        """Returns the connected I2C addresses. You need to call find_chips to fill this attribute."""
        return self._connected_i2c_addresses

    def perform_i2c_scan(self) -> List[int]:
        """
        Looks for i2c devices within a certain range on a certain port
        :return: List of i2c addresses that responded to the scan
        """
        result = self.transceive(0x29, [0x01], timeout=0.025)
        if not result:
            return []
        return list(unpack('>{cnt}B'.format(cnt=len(result)), result))

    def find_chips(self) -> List[int]:
        """
        Looking for chips on all ports and sets the _connected_i2c_addresses attribute
        :return: List of connected addresses
        """
        self._connected_i2c_addresses = self.perform_i2c_scan()
        return self._connected_i2c_addresses

    def get_user_data(self, block_number: int = 0) -> bytes:
        """
        Get 20 bytes of User Data from EEPROM.
        :param block_number: The block number to read (0..4).
        :return: 20 bytes of user data.
        """
        if block_number not in range(5):
            raise ValueError("Block number must be between 0 and 4.")
        result = self.transceive(0x21, [block_number], timeout=0.01)
        if len(result) != 21:
            raise ValueError(f"Unexpected response length for User Data: {len(result)} bytes (expected 21)")
        received_block = result[0]
        if received_block != block_number:
            raise ValueError(f"Received block number {received_block} does not match requested block {block_number}")
        return result[1:]

    def set_user_data(self, block_number: int, data: bytes) -> None:
        """
        Save 20 bytes of User Data in EEPROM.
        :param block_number: The block number to write (0..4).
        :param data: 20 bytes of user data.
        """
        if block_number not in range(5):
            raise ValueError("Block number must be between 0 and 4.")
        if len(data) != 20:
            raise ValueError("User data must be 20 bytes long.")
        payload = bytearray([block_number])
        payload.extend(data)
        self.transceive(0x21, payload, timeout=0.01)

    def device_selftest(self) -> int:
        """
        Execute a device selftest.
        :return: Selftest result (0: success, other: error code).
        """
        result = self.transceive(0x22, [], timeout=0.5)
        return int(unpack('>H', result)[0])

    def get_sensor_voltage(self) -> int:
        """
        Get the configured sensor supply voltage.
        :return: Sensor voltage (0: 3.3V, 1: 5.0V).
        """
        result = self.transceive(0x23, [], timeout=0.01)
        return int(result[0])

    def set_sensor_voltage(self, voltage: int) -> None:
        """
        Set the sensor supply voltage.
        :param voltage: Sensor voltage (0: 3.3V, 1: 5.0V).
        """
        if voltage not in [0, 1]:
            raise ValueError("Voltage must be 0 (3.3V) or 1 (5.0V).")
        self.transceive(0x23, [voltage], timeout=0.01)

    def get_sensor_type(self) -> Optional[int]:
        """
        :return: the configured sensor type
        """
        result = self.transceive(0x24, [], timeout=0.025)
        if result:
            return int(unpack('>B', result)[0])
        return None

    def set_sensor_type(self, sensor_type: int):
        """
        Set sensor type
        0: Flow Sensor (SF04 based products)
        1: Humidity Sensor (SHTxx products)
        2: Flow Sensor (SF05 based products)
        3: Flow Sensor (SF06 based products) (Firmware ≥1.7)
        4: Reserved
        :param sensor_type: One of the supported sensor types 0-4

        """
        if sensor_type not in range(5):
            raise ValueError('Sensor type not supported')
        self.transceive(0x24, [sensor_type], timeout=0.01)
        self._sensor_type = sensor_type

    def get_sensor_address(self) -> Optional[int]:
        """
        :return: the configured i2c address
        """
        result = self.transceive(0x25, [], timeout=0.025)
        if result:
            return int(unpack('>B', result)[0])
        return None

    def set_sensor_address(self, i2c_address: int) -> None:
        """
        Configure the sensors i2c address and write it to EEPROM
        :param i2c_address: the i2c address
        """
        if i2c_address not in range(128):
            raise ValueError('I2C address out of range. Address has to be within the range 0...127')
        self.transceive(0x25, [i2c_address], timeout=0.01)
        self._i2c_address = i2c_address

    def measure_sensor_voltage(self) -> int:
        """
        Measure the sensor supply voltage.
        :return: Output voltage in mV.
        """
        result = self.transceive(0x26, [], timeout=0.01)
        return int(unpack('>H', result)[0])

    def get_i2c_delay(self) -> int:
        """
        Get the I2C delay.
        :return: The I2C delay in microseconds
        """
        result = self.transceive(0x28, [], timeout=0.01)
        return int(unpack('>H', result)[0])

    def set_i2c_delay(self, delay_us: int) -> None:
        """
        Set the I2C delay.
        :param delay_us: The I2C delay in microseconds
        """
        self.transceive(0x28, list(struct.pack('>H', delay_us)), timeout=0.01)

    def get_sensor_serial_number(self, sensor_type: int) -> str:
        """
        Get the serial number of the connected sensor.
        :param sensor_type: The sensors type
        :return: the sensor serial number as string
        """
        result = self.transceive(0x54, [sensor_type], timeout=0.01)
        return result.rstrip(b'\x00').decode('utf-8')

    def get_sensor_part_name(self, sensor_type: int) -> str:
        """
        Get the part name of the connected sensor.
        :param sensor_type: The sensors' type
        :return: the sensors' part name as string
        """
        result = self.transceive(0x50, [sensor_type], timeout=0.01)
        return result.rstrip(b'\x00').decode('utf-8')

    def i2c_transceive(self, i2c_address: int, tx_data: bytes, rx_length: int, timeout_ms: int) -> bytes:
        """
        Perform an I2C transceive operation.
        :param i2c_address: The I2C address
        :param tx_data: data to transmit
        :param rx_length:  the number of bytes to receive
        :param timeout_ms: timeout in milliseconds
        :return: received data
        """
        data = bytearray([i2c_address, rx_length])
        data.extend(struct.pack('>H', timeout_ms))
        data.extend(tx_data)
        return self.transceive(0x2a, data, timeout=timeout_ms / 1000.0 + 0.05)

    def get_totalizator_status(self) -> Optional[bool]:
        """
        Get the Status (enabled / disabled) of the Totalizator.
        :return: True if the totalizator is enabled, False if disabled
        """
        result = self.transceive(0x37, [], timeout=0.01)
        if result is None:
            return None
        return bool(result[0])

    def set_totalizator_status(self, enabled: bool) -> None:
        """
        Enable or disable the Totalizator. The value of the Totalizator is not changed with this command.
        :param enabled: True to enable the totalizator, false to disable it
        """
        self.transceive(0x37, [1 if enabled else 0], timeout=0.01)

    def get_totalizator_value(self) -> Optional[int]:
        """
        Get the value of the Totalizator. This value is the sum of all unscaled
        measurements while in continuous measurement.
        Note for sensor type 3 only: Only the flow values (signal 1) are totalized, and
        the values are interpreted as i16 signed integers.
        :return: Totalizator value
        """
        result = self.transceive(0x38, [], timeout=0.01)
        if result is None:
            return None
        return int(unpack('>q', result)[0])

    def reset_totalizator(self) -> None:
        """
        Set the Totalizator value to zero, the Totalizator Status (enabled/disabled) is
        not changed. The Totalizator can be reset anytime.
        """
        self.transceive(0x39, [], timeout=0.01)

    def get_sensor_status(self) -> Optional[int]:
        """
        Get the status of sensor and continuous measurement.

        :return: Sensor status as integer, None if not available.
        """
        result = self.transceive(0x30, [], timeout=0.01)
        if not result:
            return None
        return int(result[0])

    def get_continuous_measurement_status(self) -> Optional[int]:
        """
        Get the interval or status of the Continuous Measurement.

        :return: Measurement interval in ms if started, None if not started.
        """
        result = self.transceive(0x33, [], timeout=0.01)
        if not result:
            return None
        return int(unpack('>H', result)[0])

    def sensor_reset(self) -> None:
        """
        Execute a hard reset on the sensor. Sensor must be idle for execution of this command.
        Active continuous/single measurement is stopped, and the sensor is left in the idle state.
        """
        self.transceive(0x65, [], 0.3)

    def transceive(self, command: int, data: Union[bytes, Iterable], timeout: float = -1.0) -> bytes:
        """
        Provides a generic way to send SHDLC commands.

        :param command: The command to send (one byte).
        :param data: Byte array of the data to send as arguments to the command.
        :param timeout: Response timeout in seconds (-1 for using the default value).
        :return: The returned data as bytes.
        """
        if timeout <= 0.0:
            timeout = 3.0
        result = self.execute(ShdlcCommand(
            id=command,
            data=data,
            max_response_time=float(timeout)
        ))
        if not result:
            return b''
        return result

    def get_i2c_transceiver(self) -> I2cTransceiver:
        """
        An I2cTransceiver object is required in or der to use the cable with public python i2c drivers.

        In general, all functionality of the sensors is available in the public python drivers as well.
        The throughput of the public python driver will be lower than the throughput that can be achieved with
        the sensor-specific api of the SCC1 sensor cable.
        """
        return Scc1I2cTransceiver(self)
