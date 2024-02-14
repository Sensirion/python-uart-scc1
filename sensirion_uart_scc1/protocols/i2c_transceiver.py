# -*- coding: utf-8 -*-

from typing import Protocol, Optional, runtime_checkable, Tuple, Any


class RxTx(Protocol):
    """
    An object which conforms to this protocol is supplied by the I2cChannel when using the public python drivers.
    """

    @property
    def tx_data(self) -> Optional[bytes]:
        """
        The byte array with the data to be sent
        """

    @property
    def rx_length(self) -> Optional[int]:
        """
        Number of bytes to read
        """

    @property
    def read_delay(self) -> float:
        """
        Time between writing and reading an i2c command.
        """

    def interpret_response(self, data: Optional[bytes]) -> Optional[Tuple[Any, ...]]:
        """Split the byte array from the response into the fields of the command.

        :param data: The byte array that needs to be interpreted.
        :return: A tuple with the interpreted data.
        """


@runtime_checkable
class I2cTransceiver(Protocol):

    def execute(self, slave_addr: int, rx_tx: RxTx) -> Tuple[Any, ...]:
        """
        Compatibility method for driver adapters.

        :param slave_addr: i2c slave address
        :param rx_tx: Object containing the information to execute the communication with the device
        :return: interpreted results
        """

    def transceive(self, slave_address: int, tx_data: Optional[bytes], rx_length: Optional[int], read_delay: float,
                   timeout: float) -> bytes:
        """
        Send data to the sensor and receive back a response. This function can be used for sending or receiving only
        as well.

        :param slave_address: I2c address of the sensor.
        :param tx_data: The data to be sent. In case no data shall be sent, this parameter is supposed to be None
        :param rx_length: Length of the repsonse of the sensor. If the request does not have a response, this parameter
            may be 0.
        :param read_delay: Defines the time in seconds that needs to be observed after sending the data before
            the read is initiated.
        :param timeout: Defines the time after receiving the response from the sensor before the next command may be
            sent.
        """
