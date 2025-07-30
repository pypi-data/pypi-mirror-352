# -*- coding: utf-8 -*-
import struct
import binascii
from os import PathLike
from enum import IntEnum, IntFlag
from typing import final, Any

import serial  # type: ignore
from tqdm import tqdm # type: ignore


@final
class Flasher:

    # MARK: Types

    class MemoryId(IntEnum):
        """
        Memory ID. See UM11138 Table 90
        """

        FLASH = 0
        PSECT = 1
        pFlash = 2
        Config = 3
        EFUSE = 4
        ROM = 5
        RAM0 = 6
        RAM1 = 7

    class MemoryType(IntEnum):
        """
        Memory Type. See UM11138 Table 91
        """

        ROM = 0
        FLASH = 1
        RAM = 2
        EFUSE_OTP = 5

    class AccessMode(IntFlag):
        """
        Memory access mode bit values. See UM11138 Table 92
        """

        Read = 1 << 0
        Write = 1 << 1
        Erase = 1 << 2
        EraseAll = 1 << 3
        # BlankCheck = 1 << 4 # official doc writes 0x0F before checking

    # MARK: variables

    __ser: serial.Serial
    __chunk_size: int
    __debugging: bool

    # MARK: Special methods

    def __init__(
        self, ser: serial.Serial, chunk_size: int = 512, debugging: bool = False
    ):
        self.__ser = ser
        self.__chunk_size = chunk_size
        self.__debugging = debugging

    def __del__(self) -> None:
        self.__ser.baudrate = 115200

    # MARK: Interfaces

    def write(self, file: PathLike[str] | str, baudrate: int = 1000000) -> None:
        """
        Write firmware file to the device

        Args:
            file (Pathlike[str]): Firmware file (.bin)
            baudrate (int): Writing baud rate in bits per second

        Raises:
            OSError: Failed to open the file
            RuntimeError: Failed to write to the device
        """
        # Read firmware binary file
        with open(file, "rb") as f:
            data = f.read()
            size = len(data)
            # Prepare ISP
            self.__ser.baudrate = 115200
            self.__initialize_communications(baudrate=baudrate)
            # Open memory
            if (
                handle := self.__open_memory_for_access(
                    Flasher.MemoryId.FLASH,
                    Flasher.AccessMode.Read
                    | Flasher.AccessMode.Write
                    | Flasher.AccessMode.Erase,
                )
            ) is None:
                raise RuntimeError("Failed to open memory for access")
            # Erase memory
            if not self.__erase_memory(0, size, handle):
                raise RuntimeError("Failed to erase memory")
            # Blank check memory
            if not self.__blank_check_memory(0, size, handle):
                raise RuntimeError("Failed to blank check memory")
            # Write memory
            with tqdm(total=size, unit="B", unit_scale=True, desc="Writing") as pbar:
                for addr in range(0, size, self.__chunk_size):
                    chunk = data[addr : addr + self.__chunk_size]
                    if not self.__write_memory(addr, chunk, handle):
                        raise RuntimeError(f"Failed to write memory at addr {addr:08x}")
                    pbar.update(len(chunk))
            if not self.__close_memory(handle):
                raise RuntimeError("Failed to close memory for access")
            if not self.__set_baudrate(115200):
                raise RuntimeError("Failed to restore baudrate to default")
            self.__ser.baudrate = 115200

    def verify(self, file: PathLike[str] | str, baudrate: int = 1000000) -> None:
        """
        Verify the device flash contents with a firmware file

        Args:
            file (Pathlike[str]): Firmware file (.bin)
            baudrate (int): Reading baud rate in bits per second

        Raises:
            OSError: Failed to open the file
            RuntimeError: Failed to read from the device or verification
        """
        # Read the local firmware file into data
        with open(file, "rb") as f:
            data = f.read()
            size = len(data)
            # Prepare ISP
            self.__ser.baudrate = 115200
            self.__initialize_communications(baudrate=baudrate)
            # Open memory
            if (
                handle := self.__open_memory_for_access(
                    Flasher.MemoryId.FLASH, Flasher.AccessMode.Read
                )
            ) is None:
                raise RuntimeError("Failed to open memory for access")
            # Verify memory
            with tqdm(total=size, unit="B", unit_scale=True, desc="Verifying") as pbar:
                for addr in range(0, size, self.__chunk_size):
                    file_chunk = data[addr : addr + self.__chunk_size]
                    if (
                        read_chunk := self.__read_memory(addr, len(file_chunk), handle)
                    ) is None:
                        raise RuntimeError("Failed to read memory")
                    if not (read_chunk == file_chunk):
                        raise RuntimeError(
                            "Firmware verification failed at addr {addr:08x}"
                        )
                    pbar.update(len(file_chunk))
            if not self.__close_memory(handle):
                raise RuntimeError("Failed to close memory for access")
            if not self.__set_baudrate(115200):
                raise RuntimeError("Failed to restore baudrate to default")
            self.__ser.baudrate = 115200

    def clear_app_nvm(self, baudrate: int = 1000000) -> None:
        """
        Clear application NVM memory in the device

        Args:
            baudrate (int): Writing baud rate in bits per second

        Raises:
            RuntimeError: Failed to clear memory in the device
        """
        # Prepare ISP
        self.__ser.baudrate = 115200
        self.__initialize_communications(baudrate=baudrate)
        # Open memory
        if (
            handle := self.__open_memory_for_access(
                Flasher.MemoryId.FLASH,
                Flasher.AccessMode.Read
                | Flasher.AccessMode.Write
                | Flasher.AccessMode.Erase,
            )
        ) is None:
            raise RuntimeError("Failed to open memory for access")
        # Constants from TWENETutils/source/eeprom_6x.h
        flash_8x_start_address = 0x80000
        flash_8x_size_segment = 512 # using only 64bytes (eeprom_6x_segment_size)
        eeprom_6x_user_segments = 60
        flash_8x_size_user = flash_8x_size_segment * eeprom_6x_user_segments
        # Erase memory
        if not self.__erase_memory(flash_8x_start_address, flash_8x_size_user, handle):
            raise RuntimeError("Failed to erase memory")
        # Blank check memory
        if not self.__blank_check_memory(flash_8x_start_address, flash_8x_size_user, handle):
            raise RuntimeError("Failed to blank check memory")
        if not self.__close_memory(handle):
            raise RuntimeError("Failed to close memory for access")
        if not self.__set_baudrate(115200):
            raise RuntimeError("Failed to restore baudrate to default")
        self.__ser.baudrate = 115200

    # MARK: Essntial sequences

    def __initialize_communications(self, baudrate: int = 115200) -> None:
        """
        It is important to use the Unlock ISP command before other commands are attempted.
        This sequence shows basic initialization and changing of the baud rate.

        Args:
            baudrate (int): Baud rate in bits per second

        Returns:
            bool: True if succeeded
        """
        self.__debug_print("Initializing communications...")
        # Unlock ISP to default state
        if not self.__unlock_isp_default():
            raise RuntimeError("Failed to unlock ISP to default state")
        # Get device info
        if not self.__get_device_info():
            raise RuntimeError("Failed to get device info")
        # Unlock ISP to start ISP functionality
        if not self.__unlock_isp_start():
            raise RuntimeError("Failed to unlock ISP to start functionality")
        # Set baud rate
        if not self.__set_baudrate(baudrate):
            raise RuntimeError(f"Failed to set baudrate to {baudrate}bps")

    def __read_mac_factory(self) -> bytes:
        """
        Read factory MAC address

        Assumes communications have been initialized.

        Returns:
            bytes: The address

        Raises:
            RuntimeError: When failed to read
        """
        # Open Memory for Access
        if (
            handle := self.__open_memory_for_access(
                Flasher.MemoryId.Config, Flasher.AccessMode.Read
            )
        ) is None:
            raise RuntimeError("Failed to open memory")
        # Read Memory (8 bytes from offset 0x0009FC70)
        if (address := self.__read_memory(0x0009FC70, 8, handle)) is None:
            raise RuntimeError("Failed to read memory")
        print(f"Read factory MAC: 0x{address.hex().upper()}")
        # Close Memory
        if not self.__close_memory(handle):
            raise RuntimeError("Failed to close memory")
        return address

    def __read_mac(self) -> bytes:
        """
        Read MAC address

        Assumes communications have been initialized.

        Returns:
            bytes: The address

        Raises:
            RuntimeError: When failed to read
        """
        # Open Memory for Access
        if (
            handle := self.__open_memory_for_access(
                Flasher.MemoryId.pFlash, Flasher.AccessMode.Read
            )
        ) is None:
            raise RuntimeError("Failed to open memory")
        # Read Memory (8 bytes from offset 0x00000040)
        if (address := self.__read_memory(0x00000040, 8, handle)) is None:
            raise RuntimeError("Failed to read memory")
        print(f"Read MAC: 0x{address.hex().upper()}")
        # Close Memory
        if not self.__close_memory(handle):
            raise RuntimeError("Failed to close memory")
        return address

    def __read_license(self) -> bytes:
        """
        Read license

        Assumes communications have been initialized.

        Returns:
            bytes: The license key

        Raises:
            RuntimeError: When failed to read
        """
        # Open Memory for Access
        if (
            handle := self.__open_memory_for_access(
                Flasher.MemoryId.pFlash, Flasher.AccessMode.Read
            )
        ) is None:
            raise RuntimeError("Failed to open memory")
        # Read Memory (10 bytes from offset 0x000000A0)
        if (license := self.__read_memory(0x000000A0, 10, handle)) is None:
            raise RuntimeError("Failed to read memory")
        print(f"Read license: 0x{license.hex().upper()}")
        # Close Memory
        if not self.__close_memory(handle):
            raise RuntimeError("Failed to close memory")
        return license

    # MARK: ISP Commands

    def __reset(self) -> bool:
        """
        This command resets the device.
        The response is sent before the device resets.

        Returns:
            bool: True if succeeded
        """
        command = 0x14
        return self.__send_packet(command) is not None

    def __execute(self, address: int) -> bool:
        """
        This command executes (runs) code in flash or RAM.
        The response is sent before execution jumps to the provided address.

        Args:
            address (int): Memory address to start execution from

        Returns:
            bool: True if succeeded
        """
        command = 0x21
        tx_payload = struct.pack("<I", address)
        return self.__send_packet(command, tx_payload) is not None

    def __set_baudrate(self, baudrate: int) -> bool:
        """
        This command sets the ISP data rate.
        Each interface may support a different range of rates.

        Args:
            baudrate (int): Baud rate, in bits per second

        Returns:
            bool: True if succeeded
        """
        command = 0x27
        tx_payload = b"\x00" + struct.pack("<I", baudrate & 0xFFFFFFFF)
        if self.__send_packet(command, tx_payload) is None:
            return False
        self.__ser.baudrate = baudrate
        return True

    def __get_device_info(self) -> bool:
        """
        This command returns device specific information
        and can be used to identify the connected device.

        Returns:
            bool: True if succeeded
        """
        command = 0x32
        if (rx_payload := self.__send_packet(command)) is None:
            return False
        info = struct.unpack(">II", rx_payload)
        self.__debug_print(f"Chip ID: 0x{info[0]:08X}")
        self.__debug_print(f"Version: 0x{info[1]:08X}")
        return True

    def __open_memory_for_access(
        self, memory_id: MemoryId, access_mode: AccessMode
    ) -> int | None:
        """
        This command selects and initializes a memory for programming.

        Args:
            memory_id (MemoryId): The ID of the memory block to be accessed
            access_mode (AccessMode): Required access mode(s)

        Returns:
            int or None: Handle to be used with subsequent access commands if succeeded, otherwise None
        """
        command = 0x40
        tx_payload = struct.pack(">BB", memory_id, access_mode)
        if (rx_payload := self.__send_packet(command, tx_payload)) is None:
            return None
        return rx_payload[0]  # handle value

    def __read_memory(self, address: int, length: int, handle: int = 0) -> bytes | None:
        """
        This command reads data from the selected memory.

        Args:
            address (int): Address within memory to start reading from
            length (int): Number of bytes to read
            handle (int): Handle returned by open memory command

        Returns:
            bytes or None: Data that was read from the memory if succeeded, otherwise None
        """
        command = 0x46
        mode = 0  # always use 0
        tx_payload = struct.pack("<BBII", handle, mode, address, length)
        return self.__send_packet(command, tx_payload)

    def __write_memory(self, address: int, data: bytes, handle: int = 0) -> bool:
        """
        This command writes data to the selected memory.

        Args:
            address (int): Address within memory to start reading from
            data (bytes): Data to write
            handle (int): Handle returned by open memory command

        Returns:
            bool: True if succeeded
        """
        command = 0x48
        mode = 0  # always use 0
        tx_payload = struct.pack("<BBII", handle, mode, address, len(data)) + data
        return self.__send_packet(command, tx_payload) is not None

    def __erase_memory(self, address: int, length: int, handle: int = 0) -> bool:
        """
        This command erases a region of the selected memory.

        Args:
            address (int): Address within memory to start reading from
            length (int): Number of bytes to read
            handle (int): Handle returned by open memory command

        Returns:
            bool: True if succeeded
        """
        command = 0x42
        mode = 0  # always use 0
        tx_payload = struct.pack("<BBII", handle, mode, address, length)
        return self.__send_packet(command, tx_payload) is not None

    def __blank_check_memory(self, address: int, length: int, handle: int = 0) -> bool:
        """
        This command checks if a region of the selected memory has been erased.

        Args:
            address (int): Address within memory to start reading from
            length (int): Number of bytes to read
            handle (int): Handle returned by open memory command

        Returns:
            bool: True if erased
        """
        command = 0x44
        mode = 0  # always use 0
        tx_payload = struct.pack("<BBII", handle, mode, address, length)
        return self.__send_packet(command, tx_payload) is not None

    def __close_memory(self, handle: int = 0) -> bool:
        """
        This command de-selects and finalizes the programming of a memory.

        Any writes of buffered data should be completed before a response is sent.
        Once this command has been successfully completed,
        the device may be reset without loss of data written to non-volatile memory.

        Args:
            handle (int): Handle returned by open memory command

        Returns:
            bool: True if succeeded
        """
        command = 0x4A
        tx_payload = struct.pack(">B", handle)
        return self.__send_packet(command, tx_payload) is not None

    def __get_memory_info(self, memory_id: MemoryId) -> dict[str, Any] | None:
        """
        This command returns information about the available memory blocks on a device.

        Each request results in information about 1 memory block.
        To retrieve information about all memory blocks, multiple requests should be made,
        each with an increasing value in the Memory ID field,
        until the response contains an error status to indicate that all memory blocks have been reported.

        Args:
            memory_id (MemoryId): First memory ID to search for (see list below)

        Returns:
            dict or None: A dictionary with the following keys if succeeded, otherwise None
                - 'memory_id' (MemoryId): Memory ID found
                - 'base_address' (int): Base address of memory block (may be "virtual" not physical)
                - 'length' (int): Size of memory block, in bytes
                - 'sector_size' (int): Size of each sector within the memory block,
                                       and hence the minimum size for each read, write or erase operation
                - 'type' (MemoryType): Memory type
                - 'access' (AccessMode): Access rights, as a bitmap of multiple options
                - 'name' (str): ASCII name of memory block
        """
        command = 0x4C
        tx_payload = struct.pack(">B", memory_id)
        if (rx_payload := self.__send_packet(command, tx_payload)) is None:
            return None
        fields = struct.unpack(">BIIIBB", rx_payload[:15])
        name = rx_payload[15:].decode("utf-8")
        return {
            "memory_id": Flasher.MemoryId(fields[0]),
            "base_address": fields[1],
            "length": fields[2],
            "sector_size": fields[3],
            "type": Flasher.MemoryType(fields[4]),
            "access": Flasher.AccessMode(fields[5]),
            "name": name,
        }

    def __unlock_isp_default(self) -> bool:
        """
        This command initiates ISP functionality on the interface.
        Until this command has been issued, other commands will not work.

        Default state: only Get Device Info command works in this mode

        Returns:
            bool: True if succeeded
        """
        command = 0x4E
        mode = 0x00  # Default state
        tx_payload = bytes([mode])
        return self.__send_packet(command, tx_payload) is not None

    def __unlock_isp_start(self) -> bool:
        """
        This command initiates ISP functionality on the interface.
        Until this command has been issued, other commands will not work.

        Start ISP functionality: all commands work in this mode if device is not locked

        Returns:
            bool: True if succeeded
        """
        command = 0x4E
        mode = 0x01  # Start ISP functionality
        key = bytes.fromhex("11223344556677881122334455667788")
        tx_payload = bytes([mode]) + key
        return self.__send_packet(command, tx_payload) is not None

    def __use_certificate(self, certificate: bytes) -> bool:
        """
        This command is used to provide a public key certificate to the device.

        The certificate must be signed with the root certificate present in the device.
        If no root certificate is present, an error is generated.

        Args:
            certificate (bytes): Certificate of 296 bytes

        Returns:
            bool: True if succeeded
        """
        command = 0x50
        tx_payload = certificate
        return self.__send_packet(command, tx_payload) is not None

    def __start_encrypted_transfer(
        self, mode: int, base: int, end: int, key: bytes, initialization_vector: int
    ) -> bool:
        """
        This command configures encrypted data transfer.

        If this command completes successfully, the data payload of all subsequent memory
        read and write commands with the encrypted flag set will be decrypted / encrypted
        using the supplied settings.

        Args:
            mode (int): Encryption mode (0x00: None, 0x01: AES CTR)
            base (int): Start address for encryption
            end (int): End address for encryption
            key (bytes): Encrypted key + integrity code in 24 bytes
            initialization_vector (int): Initialization vector

        Returns:
            bool: True if succeeded
        """
        command = 0x52
        tx_payload = (
            struct.pack(">BII", mode, base, end)
            + key
            + struct.pack(">I", initialization_vector)
        )
        return self.__send_packet(command, tx_payload) is not None

    # MARK: Utilities

    def __debug_print(self, message: str) -> None:
        """
        Print message in debugging state

        Args:
            message (str): Message to print
        """
        if self.__debugging:
            print(f"[Debug] {message}")

    def __hexfrom(self, data: bytes) -> str:
        return " ".join(f"{b:02X}" for b in data)

    def __crc32(self, data: bytes) -> int:
        """
        Calculate CRC32 checksum for ISP packets

        Args:
            data (bytes): Data to process

        Returns:
            int: CRC32 value
        """
        return binascii.crc32(data) & 0xFFFFFFFF

    def __send_packet(self, command: int, tx_payload: bytes = b"") -> bytes | None:
        """
        Send a packet, receive a packet and verify response.

        Args:
            command (int): Commands supported by the ISP in the Type field
            tx_payload (bytes): Request payload in the Payload field

        Returns:
            bytes or None: Response payload if valid, otherwise None
        """
        # Build command packet
        tx_flags = 0x00
        tx_length = (
            1 + 2 + 1 + len(tx_payload) + 4
        )  # flags(1) + length(2) + type(1) + payload + CRC(4)
        tx_headers = struct.pack(">BHB", tx_flags, tx_length, command)
        tx_checksum = struct.pack(">I", self.__crc32(tx_headers + tx_payload))
        tx_packet = tx_headers + tx_payload + tx_checksum
        # Send command packet
        self.__ser.write(tx_packet)
        self.__debug_print(f"Command 0x{command:02X} sent: {self.__hexfrom(tx_packet)}")
        # Read headers of response packet
        rx_headers: bytes = self.__ser.read(4)
        # Verify headers
        if len(rx_headers) < 4:
            self.__debug_print(f"Command 0x{command:02X} failed: Couldn't read headers")
            return None  # no headers
        response = rx_headers[3]
        if response != command + 1:
            self.__debug_print(
                f"Command 0x{command:02X} failed: Invalid response 0x{response:02X} expected 0x{command + 1:02X}, headers:{self.__hexfrom(rx_headers)}"
            )
            return None  # response type error
        # Read body
        rx_length = struct.unpack(">H", rx_headers[1:3])[0]
        rx_body: bytes = self.__ser.read(rx_length - 4)
        status = rx_body[0]
        rx_payload = rx_body[1:-4]
        rx_checksum = rx_body[-4:]
        rx_packet = rx_headers + rx_body
        # Verify body
        if len(rx_packet) != rx_length:
            self.__debug_print(
                f"Command 0x{command:02X} failed: Invalid length {len(rx_packet)}: {self.__hexfrom(rx_packet)}"
            )
            return None  # length error
        if struct.unpack(">I", rx_checksum)[0] != self.__crc32(rx_packet[:-4]):
            self.__debug_print(f"Command 0x{command:02X} failed: Checksum error")
            return None  # checksum error
        if status != 0:
            self.__debug_print(
                f"Command 0x{command:02X} failed: Invalid status 0x{status:02X} expected 0"
            )
            return None  # response status error
        # Return response payload
        self.__debug_print(
            f"Command 0x{command:02X} received: {self.__hexfrom(rx_packet)}"
        )
        if len(rx_payload) > 0:
            self.__debug_print(
                f"Command 0x{command:02X}  payload: {self.__hexfrom(rx_payload)}"
            )
        return rx_payload
