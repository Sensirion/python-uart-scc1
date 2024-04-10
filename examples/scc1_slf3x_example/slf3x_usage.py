import argparse

from sensirion_shdlc_driver import ShdlcSerialPort, ShdlcConnection

from sensirion_uart_scc1.drivers.scc1_slf3x import Scc1Slf3x
from sensirion_uart_scc1.drivers.slf_common import get_flow_unit_label
from sensirion_uart_scc1.scc1_shdlc_device import Scc1ShdlcDevice

parser = argparse.ArgumentParser()
parser.add_argument('--serial-port', '-p', default='COM5')
args = parser.parse_args()

with ShdlcSerialPort(port=args.serial_port, baudrate=115200) as port:
    device = Scc1ShdlcDevice(ShdlcConnection(port), slave_address=0)
    device.set_sensor_type(Scc1Slf3x.SENSOR_TYPE)
    sensor = Scc1Slf3x(device)
    print("serial_number:", sensor.serial_number)
    print("product id:", sensor.product_id)
    print("Flow;\tTemperature;\t Flag")
    flow_scale, unit = sensor.get_flow_unit_and_scale()
    sensor.start_continuous_measurement(interval_ms=2)
    try:
        for _ in range(1000):
            remaining, lost, data = sensor.read_extended_buffer()
            print(f"Remaining bytes {remaining} and {lost}-sample lost")
            print()
            for flow, temperature, flag in data:
                print(f'{flow / flow_scale} {get_flow_unit_label(unit)};\t{temperature / 200} C;\t {flag}')
    finally:
        sensor.stop_continuous_measurement()
