# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

import pytest

from sensirion_uart_scc1.drivers import scc1_ld20
from sensirion_uart_scc1.drivers.slf_common import SlfMode


def test_ld20_initialization():
    mock_device = MagicMock()
    # Mock transceive to return something valid for _get_serial_number_and_product_id
    # It expects 8 hex chars for product id and some hex chars for serial number
    mock_device.transceive.return_value = b"007010201234567\x00"
    driver = scc1_ld20.Scc1Ld20(mock_device)
    assert driver.SENSOR_TYPE == 3
    assert driver.liquid_mode == SlfMode.LIQUI_1


def test_ld20_liquid_mode_change():
    mock_device = MagicMock()
    mock_device.transceive.return_value = b"007010201234567\x00"
    driver = scc1_ld20.Scc1Ld20(mock_device)
    driver.liquid_mode = SlfMode.LIQUI_1
    assert driver.liquid_mode == SlfMode.LIQUI_1
    # Check if it uses the correct liquid config
    assert driver.get_liquid_mode_name(SlfMode.LIQUI_1) == 'Water'


@pytest.fixture
def ld20(scc1_device):
    yield scc1_ld20.Scc1Ld20(scc1_device)


@pytest.mark.needs_hardware
def test_ld20_serial_number_and_product_id(ld20):
    assert ld20 is not None
    assert isinstance(ld20.serial_number, int)
    assert isinstance(ld20.product_id, int)
