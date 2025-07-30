# pyGeoCOM

**Python library for Leica GeoCOM Total Station communication**

## Overview

`pyGeoCOM` is a Python module designed to facilitate communication with Leica GeoCOM-compatible total stations. It provides a clean and modular interface to control total stations, perform measurements, and manage geodetic data efficiently.

## Features

- Control Leica total stations via serial communication
- Support for various measurement modes and instrument settings
- Enum-based constants for clear and safe API usage
- Modular design with separated geodetic classes and communication logic
- Easily extendable for different Leica GeoCOM models

## Implemented GeoCOM Commands

| Method                             | Command Format                                   | Description                                   |
|-----------------------------------|------------------------------------------------|-----------------------------------------------|
| `do_measure(command, mode)`       | `%R1Q,2008:{command.value},{mode.value}`      | Start measurement with mode and sensor program|
| `edm_laserpointer(state)`         | `%R1Q,1004:{state.value}`                       | Enable/disable laser pointer                     |
| `fine_adjust(hz_area, v_area)`    | `%R1Q,9037:{hz_area},{v_area},0`                | Perform fine adjustment                         |
| `get_angle1(mode)`                | `%R1Q,2003:{mode.value}`                        | Get complete angle measurement                  |
| `get_atm_correction()`            | `%R1Q,2029:`                                   | Get atmospheric correction data                |
| `get_edm_mode()`                  | `%R1Q,2021:`                                   | Get EDM measurement mode                       |
| `get_fine_adjust_mode()`          | `%R1Q,9030:`                                   | Get fine adjustment mode                        |
| `get_incline_switch()`            | `%R1Q,2007:`                                   | Get inclination switch status                   |
| `get_instrument_name()`           | `%R1Q,5004:`                                   | Get instrument name                             |
| `get_instrument_number()`         | `%R1Q,5003:`                                   | Get instrument number                           |
| `get_internal_temperature()`      | `%R1Q,5011:`                                   | Get internal temperature                        |
| `get_prism_constant()`            | `%R1Q,2023:`                                   | Get prism constant                              |
| `get_software_version()`          | `%R1Q,5034:`                                   | Get software version                            |
| `get_simple_measurement(...)`     | `%R1Q,2108:{wait_time},{mode.value}`           | Request simple measurement                      |
| `search_target()`                 | `%R1Q,17020:0`                                 | Start target search                             |
| `set_atm_correction(atm)`         | `%R1Q,2028:{atm}`                              | Set atmospheric correction data                |
| `set_fine_adjust_mode(adj_mode)`  | `%R1Q,9031:{adj_mode}`                          | Set fine adjustment mode                        |
| `set_incline_switch(state)`       | `%R1Q,2006:{state.value}`                       | Set inclination switch status                   |
| `set_telescope_position(...)`    | `%R1Q,9027:{direction},{zenith},{pos_mode},{atr_mode},0` | Set telescope position               |
| `set_telescope_to_second_face(...)` | `%R1Q,9028:{pos_mode},{atr_mode},0`          | Set telescope to second face                    |
| `set_user_atr_state(state)`       | `%R1Q,18005:{state.value}`                      | Set user ATR state                              |
| `turn_off()`                     | `%R1Q,112:0`                                   | Turn off instrument                             |
| `wake_up()`                      | `%R1Q,18006:\r\n`                              | Wake up instrument                              |


## Installation

Install via pip:

```bash
pip install pygeocom
