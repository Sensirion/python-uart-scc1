# -*- coding: utf-8 -*-
import pytest

from sensirion_uart_scc1.drivers import scc1_slf3x


@pytest.fixture
def slf3x(scc1_device):
    yield scc1_slf3x.Scc1Slf3x(scc1_device)


@pytest.mark.needs_hardware
def test_slf3x_serial_number_and_product_id(slf3x):
    assert slf3x is not None
    assert isinstance(slf3x.serial_number, int)
    assert isinstance(slf3x.product_id, int)


@pytest.mark.needs_hardware
def test_scc1_sf06_start_measurements(slf3x):
    assert slf3x is not None
    slf3x.start_continuous_measurement(100)
    for i in range(3):
        remaining, lost, data = slf3x.read_extended_buffer()
        assert isinstance(remaining, int)
        assert isinstance(lost, int)
        assert isinstance(data, list)
        for record in data:
            assert isinstance(record, tuple)
            assert len(record) == 3
    slf3x.stop_continuous_measurement()
