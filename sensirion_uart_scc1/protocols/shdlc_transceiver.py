# -*- coding: utf-8 -*-

from typing import Protocol, Optional, runtime_checkable, Union, Iterable


@runtime_checkable
class ShdlcTransceiver(Protocol):

    def transceive(self, command: int, data: Union[bytes, Iterable], timeout: float = -1.0) -> Optional[bytes]:
        """Wrapper method for legacy shdlc-driver compatibility.

        :param command: The command to send (one byte)
        :param data: byte array of the data to send as arguments to the command
        :param timeout: response timeout in seconds (-1 for using default value)
        :return: The returned data as bytes
        """
