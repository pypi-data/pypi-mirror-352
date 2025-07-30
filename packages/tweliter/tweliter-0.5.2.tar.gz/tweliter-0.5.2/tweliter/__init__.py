# -*- coding: utf-8 -*-

import argparse
import time
import sys
from os import PathLike
from enum import auto, IntFlag
from typing import final, Self, Any
from types import TracebackType

import serial  # type: ignore
import pyftdi.serialext  # type: ignore
from pyftdi.ftdi import Ftdi  # type: ignore
from pyftdi.usbtools import UsbDeviceDescriptor, UsbTools  # type: ignore

import jn51xx_flasher
from . import jn5189_flasher

__all__ = ["Tweliter"]


@final
class Tweliter:
    class Type(IntFlag):
        """
        Device type
        """

        TWELITE_R1 = auto()
        TWELITE_R2 = auto()
        TWELITE_R3 = auto()
        MONOSTICK = auto()
        TWELITE_STICK = auto()
        TWELITE_STAGE_BOARD = auto()

    __ftdi: Ftdi
    __url: str
    __is_gold: bool
    __device: UsbDeviceDescriptor
    __debugging: bool

    def __init__(
        self,
        url: str | None = None,
        type_filter: Type = Type(0),
        is_gold: bool = False,
        debugging: bool = False,
    ):
        UsbTools.flush_cache()  # for reconnecting

        self.__ftdi = Ftdi()
        self.__is_gold = is_gold
        self.__debugging = debugging

        # Set __url and __device
        if url is not None:
            # URL was specified
            self.__url = url
            try:
                self.__device = self.__ftdi.get_identifiers(url)[0]
            except Exception:
                self.close()
                raise IOError(f"There's no device matches URL {url}")
        else:
            # Set dynamically
            if not sys.stdin.isatty():
                self.close()
                raise EnvironmentError("There's no console. Specify URL.")

            # Get available devices
            devices = self.__ftdi.list_devices()

            if len(devices) <= 0:
                # No devices
                self.__ftdi.close()
                raise IOError("There's no devices.")
            elif len(devices) == 1:
                # One device
                self.__url = "ftdi:///1"
                self.__device = devices[0][0]
            else:
                # Two or more devices -> Filter by types and Ask for the user
                if type_filter is None:
                    filtered_devices = devices
                else:
                    filtered_devices = []
                    for device in devices:
                        devinfo = device[0]
                        sn: str = devinfo.sn if devinfo.sn is not None else ""
                        if (
                            (
                                Tweliter.Type.TWELITE_R1 in type_filter
                                and sn.startswith("MW")
                            )
                            or (
                                Tweliter.Type.TWELITE_R2 in type_filter
                                and sn.startswith("R2")
                            )
                            or (
                                Tweliter.Type.TWELITE_R3 in type_filter
                                and sn.startswith("R3")
                            )
                            or (
                                Tweliter.Type.MONOSTICK in type_filter
                                and sn.startswith("MW")
                            )
                            or (
                                Tweliter.Type.TWELITE_STICK in type_filter
                                and sn.startswith("S1")
                            )
                            or (
                                Tweliter.Type.TWELITE_STAGE_BOARD in type_filter
                                and sn.startswith("B1")
                            )
                        ):
                            filtered_devices.append(device)
                if len(filtered_devices) <= 0:
                    # No filtered devices
                    self.__ftdi.close()
                    raise IOError(
                        f"There's no devices with the type {type_filter.name}."
                    )
                elif len(filtered_devices) == 1:
                    # One filtered device
                    devinfo = filtered_devices[0][0]
                    self.__url = f"ftdi://::{devinfo.sn}/1"
                    self.__device = devinfo
                else:
                    print("Detected multiple devices: ")
                    for index, device in enumerate(filtered_devices):
                        devinfo = device[0]
                        print(f"[{index}] {devinfo.description} ({devinfo.sn})")
                    while True:
                        try:
                            selected_index = int(input("Select device number to use: "))
                            if selected_index < 0 or selected_index >= len(
                                filtered_devices
                            ):
                                raise ValueError("Invalid number")
                            break
                        except ValueError as e:
                            print(e)
                    devinfo = filtered_devices[selected_index][0]
                    self.__url = f"ftdi://::{devinfo.sn}/1"
                    self.__device = devinfo

        if self.__debugging:
            print(f"[Debug] Set URL {self.__url}")
            print(f"[Debug] Set Device {self.__device}")

        print(f"Using {self.__device.description} ({self.__device.sn})")

        self.__ftdi.open_from_url(self.__url)
        self.__ftdi.set_bitmode(0, Ftdi.BitMode.CBUS)

        if not self.__ftdi.has_cbus:
            # CBUS gpio are not initialized; Invalid device
            self.close()
            raise IOError("Device is invalid. Cannot use CBUS pins.")

    def __del__(self) -> None:
        self.close()

    def reopen(self) -> None:
        self.close()
        self.__ftdi.open_from_url(self.__url)
        if not self.__ftdi.has_cbus:
            # CBUS gpio are not initialized; Invalid device
            self.close()
            raise IOError("Device is invalid. Cannot use CBUS pins.")

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Exit the runtime context and close the connection."""
        self.close()
        return None

    def close(self) -> None:
        if self.__ftdi.is_connected:
            self.__ftdi.close()

    @property
    def url(self) -> str:
        return self.__url

    @property
    def ftdi(self) -> Ftdi:
        return self.__ftdi

    def enter_program_mode(self) -> None:
        self.__ftdi.set_cbus_direction(0b00001100, 0b00001100)
        self.__ftdi.set_cbus_gpio(0b00000000)  # Set PRG Low, RST Low
        time.sleep(0.1)
        self.__ftdi.set_cbus_gpio(0b00000100)  # Set PRG Low, RST High
        time.sleep(0.1)
        self.__ftdi.set_cbus_gpio(0b00001100)  # Set PRG High, RST High
        time.sleep(0.3)

    def reset_device(self, set_low: bool = False) -> None:
        if not set_low:
            self.__ftdi.set_cbus_direction(0b00000100, 0b00000100)
            self.__ftdi.set_cbus_gpio(0b00000000)  # Set RST Low
            time.sleep(0.5)
            self.__ftdi.set_cbus_gpio(0b00000100)  # Set RST High
        else:
            self.__ftdi.set_cbus_direction(0b00000110, 0b00000110)
            self.__ftdi.set_cbus_gpio(0b00000100)  # Set RST High, SET Low
            time.sleep(0.1)
            self.__ftdi.set_cbus_gpio(0b00000000)  # Set RST Low, SET Low
            time.sleep(0.5)
            self.__ftdi.set_cbus_gpio(0b00000100)  # Set RST High, SET Low
        time.sleep(0.2)

    def enter_interactive_mode(self) -> None:
        self.reset_device(True)

    def get_serial_instance(self, **options: dict[str, Any]) -> serial.Serial:
        default_options = {
            "baudrate": 115200,
            "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
            "timeout": 2,
        }
        final_options = default_options | options
        ser: serial.Serial = pyftdi.serialext.serial_for_url(
            self.__url, **final_options
        )
        if ser.is_open:
            ser.close()
        if not ser.is_open:
            ser.open()
        ser.reset_output_buffer()
        ser.reset_input_buffer()
        return ser

    def get_startup_message_after(self, ser: serial.Serial, prefix: str) -> str:
        if not ser.is_open:
            ser.open()
        ser.baudrate = 115200
        ser.timeout = 1
        ser.reset_input_buffer()
        self.reset_device()
        ser.read_until(prefix.encode("utf-8"))
        line: bytes = ser.readline()
        try:
            message: str = line.decode("utf-8").strip()
        except UnicodeDecodeError:
            message = ""
        return message

    def write(
        self,
        ser: serial.Serial,
        file: PathLike[str] | str,
        verify: bool = False,
        retry: int = 2,
        safe: bool = False,
    ) -> None:
        if not ser.is_open:
            ser.open()
        for i in range(1 + retry):
            self.enter_program_mode()
            try:
                self.write_firmware(
                    ser, file, is_gold=self.__is_gold, verify=verify, safe=safe
                )
                ser.baudrate = 115200
                return
            except RuntimeError as e:
                print(e)
                if i < retry:
                    print("Retrying...")
                    continue
        raise RuntimeError("Failed to write")

    def clear(
        self,
        ser: serial.Serial,
        retry: int = 2,
        safe: bool = False,
    ) -> None:
        if not ser.is_open:
            ser.open()
        for i in range(1 + retry):
            self.enter_program_mode()
            try:
                self.clear_app_nvm(
                    ser, is_gold=self.__is_gold, safe=safe
                )
                ser.baudrate = 115200
                return
            except RuntimeError as e:
                print(e)
                if i < retry:
                    print("Retrying...")
                    continue
        raise RuntimeError("Failed to clear")


    @staticmethod
    def write_firmware(
        ser: serial.Serial,
        file: PathLike[str] | str,
        is_gold: bool = False,
        verify: bool = False,
        safe: bool = False,
    ) -> None:
        ser.reset_output_buffer()
        ser.reset_input_buffer()
        if not is_gold:
            ser.timeout = 2
            ser.baudrate = 38400
            flasher = jn51xx_flasher.Flasher(ser, "none")  # type: ignore
            try:
                flasher.run("write", file)
                if verify:
                    flasher.run("verify", file)
            except RuntimeError as e:
                raise RuntimeError(f"Failed to write ({e})")
            finally:
                ser.baudrate = 115200
        else:
            # Write to the JN5189
            ser.timeout = 2
            ser.baudrate = 115200
            flasher = jn5189_flasher.Flasher(ser, debugging=False)
            try:
                flasher.write(file, baudrate=1000000 if not safe else 115200)
                if verify:
                    flasher.verify(file, baudrate=1000000 if not safe else 115200)
            except RuntimeError as e:
                raise RuntimeError(f"Failed to write ({e})")
            finally:
                ser.baudrate = 115200

    @staticmethod
    def clear_app_nvm(
        ser: serial.Serial,
        is_gold: bool = False,
        safe: bool = False,
    ) -> None:
        if not is_gold:
            RuntimeError("Clear function is only valid with the GOLD series")
        ser.reset_output_buffer()
        ser.reset_input_buffer()
        # Clear application NVM memory in the JN5189
        ser.timeout = 2
        ser.baudrate = 115200
        flasher = jn5189_flasher.Flasher(ser, debugging=False)
        try:
            flasher.clear_app_nvm(baudrate=1000000 if not safe else 115200)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to clear ({e})")
        finally:
            ser.baudrate = 115200


def main() -> None:
    # Parse command line arguments
    def parse_type_filter(arg: str) -> Tweliter.Type:
        flags = Tweliter.Type(0)
        for name in arg.split(","):
            name = name.strip().upper()
            try:
                flags |= Tweliter.Type[name]
            except KeyError:
                raise argparse.ArgumentTypeError(f"Unknown type: {name}")
        return flags

    parser = argparse.ArgumentParser(description="Write TWELITE series firmware")
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default=None,
        help="Optional device URL starting with ftdi://",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=parse_type_filter,
        help="Device type(s), comma-separated. e.g., TWELITE_R3,MONOSTICK",
    )
    parser.add_argument(
        "-g",
        "--gold",
        action="store_true",
        help="Select GOLD series",
    )
    parser.add_argument(
        "-v",
        "--verify",
        action="store_true",
        help="Verify firmware after writing",
    )
    parser.add_argument(
        "-s",
        "--safe",
        action="store_true",
        help="Safe mode (GOLD series only, write slowly)",
    )
    parser.add_argument(
        "-m",
        "--startmsg",
        type=str,
        default="!INF",
        help="Prefix for startup message to check",
    )
    parser.add_argument(
        "-r",
        "--retry",
        type=int,
        default=2,
        help="Retry count in case of firmware writing failure",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear application NVM memory (GOLD only)",
    )
    parser.add_argument("file", nargs="?", help="Firmware file to write (not required with --clear)")
    args = parser.parse_args()

    try:
        with Tweliter(url=args.url, type_filter=args.type, is_gold=args.gold) as liter:
            ser = liter.get_serial_instance()
            if args.clear:
                # Clear application NVM memory
                if not args.gold:
                    print("The --clear option is only valid with --gold")
                    return
                # clear
                try:
                    liter.clear(ser, retry=args.retry, safe=args.safe)
                except RuntimeError:
                    print("Failed to clear")
                    return
                print("Cleared.")
            else:
                # Write firmware file
                if not args.file:
                    print("File is required unless --clear is specified")
                    return
                try:
                    liter.write(
                        ser, args.file, verify=args.verify, retry=args.retry, safe=args.safe
                    )
                except RuntimeError:
                    print("Failed to write")
                    return
                print("Done.")
                # Show startup message
                print(liter.get_startup_message_after(ser, args.startmsg))
    except IOError as e:
        print(e)


if __name__ == "__main__":
    main()
