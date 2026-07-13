import argparse
import time

from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection

from sensirion_uart_scc1.drivers.scc1_slf3x import Scc1Slf3x
from sensirion_uart_scc1.drivers.slf_common import get_volume_unit_label, SlfProductName
from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice

parser = argparse.ArgumentParser()
parser.add_argument('--serial-port', '-p', default='COM5')
args = parser.parse_args()

with ShdlcSerialPort(port=args.serial_port, baudrate=115200) as port:
    device = Scc1ShdlcDevice(ShdlcConnection(port), target_address=0)
    device.sensor_reset()
    device.set_sensor_type(Scc1Slf3x.SENSOR_TYPE)
    sensor = Scc1Slf3x(device)

    print(f'Product: {SlfProductName.from_product_id(sensor.product_id)}')
    print(f"product id: 0x{sensor.product_id:08X}")
    print(f"Serial number: {sensor.serial_number}")

    flow_scale, unit = sensor.get_flow_unit_and_scale()
    if flow_scale is None or unit is None:
        raise RuntimeError("Could not determine the sensor flow unit and scale")
    volume_unit_label = get_volume_unit_label(unit)

    sensor.set_totalizator_status(True)
    sensor.reset_totalizator()
    # Measure as fast as possible
    sensor.start_continuous_measurement(interval_ms=0)
    try:
        for _ in range(10):
            time.sleep(1)
            totalizer_value = sensor.get_totalizator_value()
            if totalizer_value is None:
                print("Totalizer value not available")
                continue

            totalized_flow = totalizer_value / flow_scale
            print(f"Totalizer volume: {totalized_flow} {volume_unit_label}")

    finally:
        sensor.stop_continuous_measurement()
