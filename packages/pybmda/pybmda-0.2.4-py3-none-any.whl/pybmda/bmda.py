# Copyright (c) 2025 Lynkz Instruments Inc. Amos, Qc Canada

"""Representation classes and helper functions"""

import re
from typing import List, Optional

from .utils import BMDA


def discover_bmps() -> List["BMP"]:
    """
    Return list of all BlackMagicProbes connected and detected by BMDA

    Returns:
        List of BMPs

    """
    bmps = []

    for line in BMDA.exec(args=["-l"]):
        match = re.search(r"\b7f[a-fA-F0-9]+\b", line, re.IGNORECASE)

        if match:
            bmp = BMP(match.group(0))
            bmps.append(bmp)

    return bmps


class BMP:
    """
    BlackMagicProbe representation from bmda
    """

    def __init__(self, serial: str) -> None:
        """
        Create new BlackMagicProbe instance

        Arguments:
            serial: Serial number of the BMP to connect to
        """
        self.serial: str = str(serial)
        return

    def Erase(self, hwreset: bool = False) -> None:
        """
        Erase the target connected to the BMP

        Arguments:
            hwreset: Set True to use the hardware reset line
        """
        args = ["-E"]
        args.extend(self._GetSerialArg())
        if hwreset:
            args.extend(["-C"])

        BMDA.exec(args=args)

    """
    Flash a bin file to a target device

    Arguments:
        filename: Path to the bin file to write to
        verify: Set to True to perform a verify after the write
        hwreset: Set to True to use the hardware reset line
        start: Set to an address to start at a different address
        len: Set to the length to override the default length
    """

    def Flash(
        self, filename: str, verify: bool = False, hwreset: bool = False, start: int = None, len: int = None
    ) -> None:
        args = self._GetSerialArg()
        args.extend(["-w"])
        if verify:
            args.extend(["-V"])
        args.extend([filename])
        if hwreset:
            args.extend(["-C"])
        if start is not None:
            args.extend(["-a"])
            args.extend([hex(start)])
        if len is not None:
            args.extend(["-S"])
            args.extend([str(len)])
        BMDA.exec(args=args)

    def Reset(self, hwreset: bool):
        args = self._GetSerialArg()
        args.extend(["-R"])
        if hwreset:
            args.extend(["h"])
        BMDA.exec(args=args)

    def _GetSerialArg(self) -> list:
        return ["-s", f"{self.serial}"]
