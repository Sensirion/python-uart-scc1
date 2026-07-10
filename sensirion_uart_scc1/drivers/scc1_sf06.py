# -*- coding: utf-8 -*-

import struct
import time
from typing import List, Tuple, Optional, Any

from sensirion_uart_scc1.drivers.slf_common import SlfMeasurementCommand, SlfMode, SLF_PRODUCT_LIQUI_MAP, SlfProduct
from sensirion_uart_scc1.scc1_exceptions import Scc1InvalidDataReceived
from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice


class Scc1Sf06:
    """
    Driver for the SF06 sensor family connected via SCC1 cable.
    SF06 sensors are sensor type 3.
    """
    SENSOR_TYPE = 3
    START_MEASUREMENT_DELAY_S = 0.015

    def __init__(self, device: Scc1ShdlcDevice, liquid_mode: SlfMode = SlfMode.LIQUI_1) -> None:
        """
        Initialize object instance.

        :param device: The Scc1 device that provides the access to the sensor.
        :param liquid_mode: The liquid that is measured.
        """
        self._scc1 = device
        self._liquid_config = SLF_PRODUCT_LIQUI_MAP[SlfProduct.SF06]
        self._serial_number, self._product_id = self._get_serial_number_and_product_id()
        self._is_measuring = False
        self._sampling_interval_ms = 100  # Default 10Hz
        self._liquid_mode = liquid_mode
        self._measurement_command = SlfMeasurementCommand.from_mode(self._liquid_mode)

    @property
    def serial_number(self) -> Optional[int]:
        """
        Get the serial number

        :return: The serial number as integer
        """
        return self._serial_number

    @property
    def product_id(self) -> Optional[int]:
        """
        Get the product id

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
        from sensirion_uart_scc1.scc1_exceptions import Scc1NotSupportedException
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

        :return: The name of a specific liquid measurement mode
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
        This will not be applied while the measurement is running

        :param interval_ms: The requested measurement interval in milliseconds
        """
        self._sampling_interval_ms = interval_ms

    def get_serial_number(self) -> Optional[int]:
        """
        Get the serial number of the device.

        :return: The sensor serial number
        """
        return self._serial_number

    def get_flow_unit_and_scale(self, command: Optional[int] = None) -> Optional[Tuple[int, int]]:
        """
        Get the scale factor, unit, and sensor sanity check result of the sensor for the given argument.
        (available on SF06 sensor products)

        :param command: The 16-bit command to read flow unit and scale factor for. If no value is supplied,
            the actual measurement command is used
        :return: A tuple with (scale_factor, flow_unit), None if the command is not supported
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
        Read current measurement and starts internal continuous measurement with the configured interval, if not
        already started.

        :return: A tuple with flow, temperature, and flag
        """
        data = self._scc1.transceive(0x35, [self.SENSOR_TYPE], 0.01)
        if not data:
            # Measurement is not ready
            return None
        return struct.unpack('>hhH', data)

    def start_continuous_measurement(self, interval_ms=0) -> None:
        """
        Start a continuous measurement with a given interval.

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
        Read out measurement buffer for SF06.
        SF06 might return multiple signals.

        :return: A tuple with (bytes_remaining, bytes_lost, data)
        """
        data = self._scc1.transceive(0x36, [self.SENSOR_TYPE], 0.01)
        if not data:
            return 0, 0, []
        bytes_lost = int(struct.unpack('>I', data[:4])[0])
        bytes_remaining = int(struct.unpack('>H', data[4:6])[0])
        num_signals = struct.unpack('>H', data[6:8])[0]
        # For SF06, signals are typically i16
        num_packets = int(len(data[8:]) / 2 / num_signals)
        buffer = list(struct.unpack(">" + "h" * (num_packets * num_signals), data[8:]))

        if len(buffer) % num_signals != 0:
            raise Scc1InvalidDataReceived("Received unexpected amount of data")

        num_samples = len(buffer) // num_signals
        out = [tuple(buffer[i * num_signals:(i + 1) * num_signals])
               for i in range(num_samples)]
        return bytes_remaining, bytes_lost, out

    def get_totalizator_status(self) -> Optional[bool]:
        """
        Get the Status (enabled / disabled) of the Totalizator.
        :return: True if the totalizator is enabled, False if disabled
        """
        return self._scc1.get_totalizator_status()

    def set_totalizator_status(self, enabled: bool) -> None:
        """
        Enable or disable the Totalizator. The value of the Totalizator is not changed with this command.
        :param enabled: True to enable the totalizator, false to disable it
        """
        self._scc1.set_totalizator_status(enabled)

    def get_totalizator_value(self) -> Optional[int]:
        """
        Get the value of the Totalizator for SF06.
        For sensor type 3 only: Only the flow values (signal 1) are totalized, and
        the values are interpreted as i16 signed integers.
        :return: Totalizator value
        """
        return self._scc1.get_totalizator_value()

    def reset_totalizator(self) -> None:
        """
        Set the Totalizator value to zero, the Totalizator Status (enabled/disabled) is
        not changed. The Totalizator can be reset anytime.
        """
        self._scc1.reset_totalizator()

    def get_sensor_status(self) -> Optional[int]:
        """
        Get the status of the sensor and the continuous measurement.

        :return: Sensor status as integer, None if not available.
        """
        return self._scc1.get_sensor_status()

    def get_continuous_measurement_status(self) -> Optional[int]:
        """
        Get the interval or status of the continuous Measurement.

        :return: Measurement interval in ms if started, None if not started.
        """
        return self._scc1.get_continuous_measurement_status()

    def _get_serial_number_and_product_id(self) -> Tuple[Optional[int], Optional[int]]:
        """
        :return: The sensor serial number and product id as tuple
        """
        data = self._scc1.transceive(0x50, [], 0.01)
        if not data:
            return None, None
        data = data.rstrip(b'\x00').decode('utf-8')
        product_id = int(data[:8], 16)
        serial_number = int(data[8:], 16)
        return serial_number, product_id
