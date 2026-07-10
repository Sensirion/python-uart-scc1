# -*- coding: utf-8 -*-

from sensirion_uart_scc1.drivers.slf_common import SlfMode, SLF_PRODUCT_LIQUI_MAP, SlfProduct
from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice
from sensirion_uart_scc1.drivers.scc1_sf06 import Scc1Sf06


class Scc1Ld20(Scc1Sf06):
    """
    Scc1 LD20 Sensor Driver

    The Scc1 provides features to support the LD20 liquid flow sensors. This driver accesses the sensor through the
    API specified by scc1.
    """
    SENSOR_TYPE = 3  #: Sensor type for LD20 (same as SF06/SLF3x)

    def __init__(self, device: Scc1ShdlcDevice, liquid_mode: SlfMode = SlfMode.LIQUI_1) -> None:
        """
        Initialize object instance.

        :param device: The Scc1 device that provides the access to the sensor.
        :param liquid_mode: The liquid that is measured.
        """
        super().__init__(device, liquid_mode)
        self._liquid_config = SLF_PRODUCT_LIQUI_MAP[SlfProduct.LD20]
