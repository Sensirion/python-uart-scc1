# -*- coding: utf-8 -*-

from struct import pack
from typing import Optional, Any, Tuple

from sensirion_uart_scc1.protocols.shdlc_transceiver import ShdlcTransceiver
from sensirion_uart_scc1.protocols.i2c_transceiver import RxTx


class Scc1I2cTransceiver:
    """
    Wrapper that implements the I2cTransceiver protocol.
    This wrappers allows to use the public I2c Python drivers drivers wit the SCC1 cable
    """

    def __init__(self, device: ShdlcTransceiver) -> None:
        super().__init__()
        self._scc1 = device

    def execute(self, slave_address: int, rx_tx: RxTx) -> Tuple[Any, ...]:
        """Implements tht I2cTransceiver protocol"""
        data = self.transceive(slave_address, rx_tx.tx_data, rx_tx.rx_length, rx_tx.read_delay)
        return rx_tx.interpret_response(data)

    def transceive(self, slave_address: int, tx_data: Optional[bytes], rx_length: Optional[int], read_delay: float,
                   timeout: float = 0.01) -> bytes:
        """Implements the I2cTransceiver protocol"""

        if tx_data is None:
            tx_data = bytearray()
        else:
            tx_data = bytearray(tx_data)
        if rx_length is None:
            rx_length = 0
        tx_size = len(tx_data)
        header = pack('>BBBH', slave_address, tx_size, rx_length, int(read_delay * 1000))
        cmd_data = bytearray(header)
        cmd_data.extend(tx_data)
        result = self._scc1.transceive(0x2A, cmd_data, timeout)
        if result is None or rx_length == 0:
            return bytearray()
        return result
