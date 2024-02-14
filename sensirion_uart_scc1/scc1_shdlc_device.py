# -*- coding: utf-8 -*-

import logging
from typing import Optional, Iterable, Union

from packaging.version import Version
from sensirion_shdlc_driver import ShdlcDevice, ShdlcConnection
from sensirion_shdlc_driver.command import ShdlcCommand

from sensirion_uart_scc1.protocols.i2c_transceiver import I2cTransceiver
from sensirion_uart_scc1.scc1_i2c_transceiver import Scc1I2cTransceiver

log = logging.getLogger(__name__)


class Scc1ShdlcDevice(ShdlcDevice):
    """
    The Scc1 Shdlc device is used to communicate with various sensor using the Sensirion SCC1 sensor cable.
    """

    def __init__(self, connection: ShdlcConnection, slave_address: int = 0) -> None:
        """Initialize object instance.

        :param connection: The used ShdlcConnection
        :param slave_address: The SHDLC slave address that is used by this device.
        """
        super().__init__(connection, slave_address)
        self._version = self.get_version()
        self._serial_number = self.get_serial_number()

    def __str__(self):
        return f"SCC1-{self.serial_number}@{self.com_port}"

    @property
    def com_port(self):
        return self.connection.port.description.split('@')[0]

    @property
    def serial_number(self) -> str:
        return self._serial_number

    @property
    def firmware_version(self) -> Version:
        return Version(str(self._version.firmware))

    def sensor_reset(self) -> None:
        """
        Execute a hard reset on the sensor and check for correct response. Active
        continuous/single measurement is stopped and the sensor is left in idle state.
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

        In general all functionality of the sensors are available in the public python drivers as well. The
        throughput of the public python driver will be lower than the throughput that can be achieved with
        the sensor specific api of the SCC1 sensor cable.
        """
        return Scc1I2cTransceiver(self)
