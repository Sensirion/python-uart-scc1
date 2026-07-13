# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-7-13

### Added
- Add SHDLC commands: User Data (0x21), Device Selftest (0x22), Sensor Voltage (0x23), Measure Sensor Voltage (0x26)
- Add interface for totalizer

### Changed
- Improve usage examples
- Ensure linux file endings across the package
- Update GitHub actions to the latest versions
- Update dependencies

### Fixed
- Fix several typos

## [1.1.1] - 2024-4-10

### Fixed

- Accidental release due to wrong GitHub action definition

## [1.1.0] - 2024-4-10

### Added

- Interface to get and set the sensor type
- Interface to scan for i2c addresses
- Interface to get/set i2c address

## [1.0.0] - 2024-2-14

### Added

- Provide initial version of this repository containing a driver for the Sensirion SCC1-USB cable.

[Unreleased]: https://github.com/Sensirion/python-uart-scc1/compare/2.0.0...HEAD
[2.0.0]: https://github.com/Sensirion/python-uart-scc1/compare/1.1.0...2.0.0
[1.1.0]: https://github.com/Sensirion/python-uart-scc1/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/Sensirion/python-uart-scc1/releases/tag/1.0.0
