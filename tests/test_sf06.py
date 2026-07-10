# -*- coding: utf-8 -*-
import pytest

from sensirion_uart_scc1.drivers import scc1_sf06


@pytest.fixture
def sf06(scc1_device):
    yield scc1_sf06.Scc1Sf06(scc1_device)


@pytest.mark.needs_hardware
def test_sf06_serial_number_and_product_id(sf06):
    assert sf06 is not None
    assert isinstance(sf06.serial_number, int)
    assert isinstance(sf06.product_id, int)


@pytest.mark.needs_hardware
def test_sf06_start_measurements(sf06):
    assert sf06 is not None
    sf06.start_continuous_measurement(100)
    # Test get_continuous_measurement_status
    status = sf06.get_continuous_measurement_status()
    assert status == 100

    # Test get_sensor_status
    sensor_status = sf06.get_sensor_status()
    assert isinstance(sensor_status, int)

    for i in range(3):
        remaining, lost, data = sf06.read_extended_buffer()
        assert isinstance(remaining, int)
        assert isinstance(lost, int)
        assert isinstance(data, list)
        for record in data:
            assert isinstance(record, tuple)
            # SF06 might have more than 3 signals, but at least flow/temp/flags
            assert len(record) >= 3
    sf06.stop_continuous_measurement()
