# python-uart-scc1
This repository provides a Python driver for [Sensirion SCC1-USB Cable](https://www.sensirion.com/products/catalog/SCC1-USB/).
The detailed technical description of the SCC1-USB cable is provided in the [datasheet](https://www.sensirion.com/media/documents/EE77392F/65290BF6/LQ_DS_SCC1-RS485-USB_Datasheet.pdf).

## Feature overview

On one hand the SCC1-USB exposes an API to efficiently use the supported sensors. So far support is only added for the [SLF3x-Sensor family](https://sensirion.com/products/catalog/SLF3C-1300F).

On the other hand the cable can be used as USB to I2c bridge for any Sensirion I2c sensor that can be plugged to the cable.

For both scenarios an example is available in the example subfolder of this repository.

**Note**: Using the cable as USB to I2c bridge will not allow to achieve the same throughput as with the embedded API.

The API of the driver is described on the [documentation page](https://sensirion.github.io/python-uart-scc1) of this repository

## Getting started

### Installation

It is recommended to use a virtual environment. In any case you can install the package via pip by typing:

```bash
pip install sensirion-uart-scc1
```

If you have cloned the repository you can install the package and all it dependencies using [poetry](https://python-poetry.org/).

```bash
poetry install
```

### Running the examples

We provide two examples to show two basic usage scenarios of the driver

- **SLF3x Usage**
  This example does not require any additional dependency. Once the package `sensirion-uart-scc1` is installed the example is run by typing:

  ```bash
    python ./examples/scc1_slf3x_example/slf3x_usage.py --serial-port <your-com-port>
  ```

- **USB-I2c-Bridge**
  This example shows how a public python driver can be used with the SCC1-USB cable. The example uses the public driver `sensirion_i2c_sf06_lf`. Before you run the example you need to install this driver.

  ```bash
    pip install sensirion_i2c_sf06_lf
  ```

  After having installed the driver the example is run by typing:

  ```bash
    python ./examples/scc1_usb_to_i2c/scc1_usb_2_i2c_usage.py --serial-port <your-com-port>
  ```

## Contributing

You are very welcome to open issues and to create pull requests.

Nevertheless you need to understand that we cannot consider pull request that do not pass the CI-pipeline.

This section explains in short how you can make sure that your contribution passes all the checks of the CI pipeline.

The repository uses poetry for dependency management. It is used in the CI pipeline as well.
The easiest way to be conformant to our coding style will be to use poetry for your contributions as well. This will allow to test and check your contributions locally before creating pull requests.

### Installing and running tests

For testing some extra dependencies are required that need to be installed.

```bash
poetry install --with test
```

The tests (including those that are marked) can be executed by tying:

```bash
poetry run pytest
```

**Note**: On github no tests that require hardware can be run. Test cases that rely on attached hardware need to be decorated with `@pytest.mark.needs_hardware`

### Checking code-formatting

Make sure that you code is properly formatted. The CI pipeline will check and fail if this is not the case. To check the code-formatting before pushing to the repository type:

```bash
poetry run flake8
```
