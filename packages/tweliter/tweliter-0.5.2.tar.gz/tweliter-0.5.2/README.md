<a href="https://mono-wireless.com/jp/index.html">
    <img src="https://mono-wireless.com/common/images/logo/logo.svg" alt="mono wireless logo" title="MONO WIRELESS" align="right" height="35" />
</a>

# tweliter

A Python module for writing TWELITE series firmware. (beta)

[![MW-OSSLA](https://img.shields.io/badge/License-MW--OSSLA-e4007f)](LICENSE)

## Overview

Write firmware over TWELITE R series via USB.

This module is executable in standalone and importable for your scripts.

## Installation

The module is available in [PyPI](https://pypi.org/project/tweliter/).

Use `pip`

```
pip install tweliter
```

or `poetry`

```
poetry add tweliter
```

### Linux

Sometimes you need to set permission with `udev`.

1. Create `/etc/udev/rules.d/99-ftdi.rules`

```sh
# TWELITE R / MONOSTICK (FT232R / 0403:6001)
SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666"

# TWELITE R2 / R3 (FT230X / 0403:6015)
SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", MODE="0666"
```

2. Reload udev rules

```sh
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Usage

### Command line

Simply

```shell
$ tweliter dir/SomeApp_BLUE.bin
```

or use verification

```shell
$ tweliter --verify dir/SomeApp_BLUE.bin
```

FTDI chip can be filtered by [URL](https://eblot.github.io/pyftdi/urlscheme.html)

```shell
$ tweliter --url ftdi://:ft-x:/1 dir/SomeApp_BLUE.bin
```

or product type(s)

```shell
$ tweliter --type TWELITE_R2,TWELITE_R3 dir/SomeApp_BLUE.bin
```

### In script

```python
from pathlib import Path
from tweliter import Tweliter

file = Path("firmware/SomeApp_BLUE.bin")

try:
    with Tweliter(
        type_filter=Tweliter.Type.TWELITE_R2 | Tweliter.Type.TWELITE_R3
    ) as liter:
        # Get serial interface
        ser = liter.get_serial_instance()
        # Write firmware
        liter.write(ser, file, verify=True)
        # Show startup message
        print(liter.get_startup_message_after(ser, "!INF"))
except IOError as e:
    print(f"Couldn't connect {e}")
except RuntimeError as e:
    print(f"Failed to write {e}")
```

## LICENSE

MW-OSSLA
