# -*- coding: utf-8 -*-

import logging
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

    def __init__(self, connection: ShdlcConnection, slave_address: int = 0) -> None:
        """Initialize object instance.

        :param connection: The used ShdlcConnection
        :param slave_address: The SHDLC slave address that is used by this device.
        """
        super().__init__(connection, slave_address)
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
        return list(unpack('>{cnt}B'.format(cnt=len(result)), result))

    def find_chips(self) -> List[int]:
        """
        Looking for chips on all ports and sets the _connected_i2c_addresses attribute
        :return: List of connected addresses
        """
        self._connected_i2c_addresses = self.perform_i2c_scan()
        return self._connected_i2c_addresses

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

    def sensor_reset(self) -> None:
        """
        Execute a hard reset on the sensor and check for the correct response.
        Active continuous/single measurement is stopped, and the sensor is left in idle state.
        """
        self.transceive(0x66, [], 0.3)

    def transceive(self, command: int, data: Union[bytes, Iterable], timeout: float = -1.0) -> Optional[bytes]:
        """
        Provides a generic way to send shdlc commands.

        :param command: The command to send (one byte).
        :param data: Byte array of the data to send as arguments to the command.
        :param timeout: Response timeout in seconds (-1 for using default value).
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
