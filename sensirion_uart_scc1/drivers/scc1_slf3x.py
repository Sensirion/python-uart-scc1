# -*- coding: utf-8 -*-

import math
import struct
import time
from typing import List, Tuple, Optional, Any, cast

from sensirion_uart_scc1.drivers.slf_common import SlfMeasurementCommand, SlfMode, SLF_PRODUCT_LIQUI_MAP, SlfProduct
from sensirion_uart_scc1.scc1_exceptions import Scc1NotSupportedException, Scc1InvalidDataReceived
from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice


class Scc1Slf3x:
    """
    Scc1 Slf3x Sensor Driver

    The Scc1 provides features to support the Slf3x liquid flow sensors. This driver accesses the sensor through the
    API specified by scc1.
    """
    SENSOR_TYPE = 3  #: Sensor type for Slf3x
    START_MEASUREMENT_DELAY_S = 0.015

    def __init__(self, device: Scc1ShdlcDevice, liquid_mode: SlfMode = SlfMode.LIQUI_1) -> None:
        """
        Initialize object instance.

        :param device: The Scc1 device that provides the access to the sensor.
        :param liquid_mode: The liquid that is measured.
        """
        self._scc1 = device
        self._liquid_config = SLF_PRODUCT_LIQUI_MAP[SlfProduct.SLF3x]
        self._serial_number, self._product_id = self._get_serial_number_and_product_id()
        self._is_measuring = False
        self._sampling_interval_ms = 100  # Default 10Hz
        self._liquid_mode = liquid_mode
        self._measurement_command = SlfMeasurementCommand.from_mode(self._liquid_mode)

    @property
    def serial_number(self) -> int:
        """
        Get the serial number

        :return: The serial number as integer
        """
        return self._serial_number

    @property
    def product_id(self) -> int:
        """
        Get the product Id

        :return: The product identifier as integer
        """
        return self._product_id

    @property
    def liquid_mode(self) -> SlfMode:
        """
        Liquid measurement mode
        """
        return self._liquid_mode

    @liquid_mode.setter
    def liquid_mode(self, mode: SlfMode) -> None:
        """
        Set liquid measurement mode.

        :param mode: One of the liquid measurement modes
        """
        if not isinstance(mode, SlfMode):
            raise Scc1NotSupportedException(f"Invalid liquid mode: {mode}")

        if self._is_measuring:
            raise Scc1NotSupportedException("Set liquid mode not allowed while measurement is running")

        self._liquid_mode = mode
        self._measurement_command = SlfMeasurementCommand.from_mode(self._liquid_mode)

    @property
    def liquid_mode_name(self) -> str:
        """
        Get the name of the liquid.

        :return: Name of current liquid measurement mode
        """
        return self.get_liquid_mode_name(self._liquid_mode)

    def get_liquid_mode_name(self, mode: SlfMode) -> str:
        """
        Get the name of the liquid

        :param mode: A liquid mode
        :return: Get name of a specific liquid measurement mode
        """
        return self._liquid_config.liqui_mode_name(mode)

    @property
    def sampling_interval_ms(self) -> int:
        """
        Sampling interval for synchronous measurement

        :return: Current internal sampling interval
        """
        return self._sampling_interval_ms

    @sampling_interval_ms.setter
    def sampling_interval_ms(self, interval_ms: int):
        """
        Set sampling interval for continuous measurement
        This will not be applied while measurement is running

        :param interval_ms: The requested measurement interval in milliseconds
        """
        self._sampling_interval_ms = interval_ms

    def get_serial_number(self) -> int:
        """
        Get the serial number of the device.

        :return: The sensor serial number
        """
        return self._serial_number

    def get_flow_unit_and_scale(self, command: Optional[int] = None) -> Optional[Tuple[int, int]]:
        """
        Get the scale factor, unit and sensor sanity check result of the sensor for the given argument.
        (only available on some SLF3x sensor products)

        :param command: The 16-bit command to read flow unit and scale factor for. If no value is supplied
            the actual measurement command is used
        :return: A tuple with (scale_factor, flow_unit), None if command is not supported
        """
        if command is None:
            command = self._measurement_command
        args = list(struct.pack('>h', command))
        data = self._scc1.transceive(0x53, args, 0.01)
        if len(data) != 6:
            return None
        scale, unit, _ = struct.unpack('>HHH', data)
        return scale, unit

    def get_last_measurement(self) -> Optional[Tuple[int, int, int]]:
        """
        Read current measurement and starts internal continuous measurement with configured interval, if not
        already started.

        :return: A tuple with flow, temperature and flag
        """
        data = self._scc1.transceive(0x35, [self.SENSOR_TYPE], 0.01)
        if not data:
            # Measurement not ready
            return None
        return cast(Tuple[int, int, int], struct.unpack('>hhH', data))

    def start_continuous_measurement(self, interval_ms=0) -> None:
        """
        Start a continuous measurement with a give interval.

        :param interval_ms: Measurement interval in milliseconds.
        """
        if self._is_measuring:
            return
        data = bytearray()
        data.extend(bytearray(struct.pack('>H', int(interval_ms))))
        data.extend(bytearray(struct.pack('>H', int(self._measurement_command))))
        self._scc1.transceive(0x33, data, 0.01)
        time.sleep(self.START_MEASUREMENT_DELAY_S)
        self._is_measuring = True

    def stop_continuous_measurement(self) -> None:
        """Stop continuous measurement"""
        if not self._is_measuring:
            return
        self._scc1.transceive(0x34, [], 0.01)
        self._is_measuring = False

    def read_extended_buffer(self) -> Tuple[int, int, List[Tuple[Any, ...]]]:
        """
        Read out measurement buffer

        :return: A tuple with (bytes_remaining, bytes_lost, data)
        """
        data = self._scc1.transceive(0x36, [self.SENSOR_TYPE], 0.01)
        bytes_lost = int(struct.unpack('>I', data[:4])[0])
        bytes_remaining = int(struct.unpack('>H', data[4:6])[0])
        num_signals = struct.unpack('>H', data[6:8])[0]
        num_packets = int(len(data[8:]) / 2 / num_signals)
        buffer = list(struct.unpack(">" + "hhh" * num_packets, data[8:]))
        fractional, integer = math.modf(len(buffer) / num_signals)
        if fractional != 0:
            raise Scc1InvalidDataReceived("Received unexpected amount of data")
        num_samples = int(integer)
        # Output buffer a list of tuples with (flow, temp, flags).
        out = [tuple(buffer[i * num_signals:i * num_signals + num_signals])
               for i in range(num_samples)]
        return bytes_remaining, bytes_lost, out

    def _get_serial_number_and_product_id(self) -> Tuple[int, int]:
        """
        :return: The sensor serial number and product id as tuple
        """
        data = self._scc1.transceive(0x50, [], 0.01)
        data = data.rstrip(b'\x00').decode('utf-8')
        product_id = int(data[:8], 16)
        serial_number = int(data[8:], 16)
        return serial_number, product_id
