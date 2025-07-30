# Copyright (c) 2022 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

"""Various types and definitions for the Haltium platform."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional


@enum.unique
class Product(enum.Enum):
    """Enumeration of supported product names in the Haltium family."""

    NRF54H20 = enum.auto()
    NRF9280 = enum.auto()

    @classmethod
    def _missing_(cls, value: object) -> Optional[Product]:
        """Custom enum behavior to support case insensitive values."""
        if not isinstance(value, str):
            return None
        return cls.__members__.get(value.upper())

    @property
    def product_code(self) -> ProductCode:
        match self:
            case Product.NRF54H20:
                return ProductCode(part_number=0x16, revision=0x2)
            case Product.NRF9280:
                return ProductCode(part_number=0x12, revision=0x1)
            case _:
                raise ValueError(f"No product code found for {self}")


@dataclass
class ProductCode:
    part_number: int
    revision: int


@enum.unique
class AddressOffset(enum.IntEnum):
    """Address bit offsets, defined by Address Format of the product specification."""

    REGION = 29
    SECURITY = 28
    DOMAINID = 24
    ADDR = 23


def secure_address_get(address: int) -> int:
    """Get the TrustZone secure address for the given address"""
    return address | (1 << AddressOffset.SECURITY)


@enum.unique
class AddressRegion(enum.IntEnum):
    """Address regions, defined by Address Format of the product specification."""

    PROGRAM = 0
    DATA = 1
    PERIPHERAL = 2
    EXT_XIP = 3
    EXT_XIP_ENCRYPTED = 4
    STM = 5
    CPU = 7

    @classmethod
    def from_address(cls, address: int) -> AddressRegion:
        """Get the address region of an address."""
        return cls((address >> AddressOffset.REGION) & 0b111)


@enum.unique
class DomainID(enum.IntEnum):
    """Domain IDs in Haltium products."""

    SECURE = 1
    APPLICATION = 2
    RADIOCORE = 3
    CELLCORE = 4
    CELLDSP = 5
    CELLRF = 6
    ISIMCORE = 7
    GLOBALFAST = 12
    GLOBALSLOW = 13
    GLOBAL_ = 14
    GLOBAL = 15

    @classmethod
    def from_address(cls, address: int) -> DomainID:
        """Get the domain ID of an address."""
        return cls((address >> AddressOffset.DOMAINID) & 0xF)

    @classmethod
    def from_processor(cls, processor: ProcessorID | int) -> DomainID:
        """Get the domain ID corresponding to a processor ID."""
        processor_domain = {
            ProcessorID.SECURE: cls.SECURE,
            ProcessorID.APPLICATION: cls.APPLICATION,
            ProcessorID.RADIOCORE: cls.RADIOCORE,
            ProcessorID.CELLCORE: cls.CELLCORE,
            ProcessorID.CELLDSP: cls.CELLDSP,
            ProcessorID.CELLRF: cls.CELLRF,
            ProcessorID.ISIMCORE: cls.ISIMCORE,
            ProcessorID.SYSCTRL: cls.GLOBALFAST,
            ProcessorID.PPR: cls.GLOBALSLOW,
            ProcessorID.FLPR: cls.GLOBAL_,
        }
        return processor_domain[ProcessorID(processor)]

    @property
    def c_enum(self) -> str:
        return f"NRF_DOMAIN_{self.name.upper()}"


@enum.unique
class OwnerID(enum.IntEnum):
    """Enumeration of ownership IDs in haltium products."""

    NONE = 0
    SECURE = 1
    APPLICATION = 2
    RADIOCORE = 3
    CELL = 4
    ISIMCORE = 5
    SYSCTRL = 8

    @classmethod
    def from_domain(cls, domain: DomainID | int) -> OwnerID:
        """Get the owner ID corresponding to a domain ID."""
        domain_owner = {
            DomainID.SECURE: cls.SECURE,
            DomainID.APPLICATION: cls.APPLICATION,
            DomainID.RADIOCORE: cls.RADIOCORE,
            DomainID.CELLCORE: cls.CELL,
            DomainID.CELLDSP: cls.CELL,
            DomainID.CELLRF: cls.CELL,
            DomainID.ISIMCORE: cls.ISIMCORE,
            DomainID.GLOBALFAST: cls.SYSCTRL,
        }
        return domain_owner[DomainID(domain)]

    @classmethod
    def from_processor(cls, processor: ProcessorID | int) -> OwnerID:
        """Get the owner ID corresponding to a processor ID."""
        return cls.from_domain(DomainID.from_processor(processor))

    @property
    def c_enum(self) -> str:
        return f"NRF_OWNER_{self.name.upper()}"


@enum.unique
class ProcessorID(enum.IntEnum):
    """Processor IDs in haltium products."""

    SECURE = 1
    APPLICATION = 2
    RADIOCORE = 3
    CELLCORE = 4
    CELLDSP = 5
    CELLRF = 6
    ISIMCORE = 7
    BBPR = 11
    SYSCTRL = 12
    PPR = 13
    FLPR = 14

    @classmethod
    def from_domain(cls, domain: DomainID | int) -> ProcessorID:
        """Get the processor ID corresponding to a domain ID."""
        domain_processor = {
            DomainID.SECURE: cls.SECURE,
            DomainID.APPLICATION: cls.APPLICATION,
            DomainID.RADIOCORE: cls.RADIOCORE,
            DomainID.CELLCORE: cls.CELLCORE,
            DomainID.CELLDSP: cls.CELLDSP,
            DomainID.CELLRF: cls.CELLRF,
            DomainID.ISIMCORE: cls.ISIMCORE,
            DomainID.GLOBALFAST: cls.SYSCTRL,
            DomainID.GLOBALSLOW: cls.PPR,
            DomainID.GLOBAL_: cls.FLPR,
        }
        return domain_processor[DomainID(domain)]

    @property
    def c_enum(self) -> str:
        return f"NRF_PROCESSOR_{self.name.upper()}"


@enum.unique
class Ctrlsel(enum.IntEnum):
    """
    Enumeration of GPIO.PIN_CNF[n].CTRLSEL values.
    The list here may not be exhaustive.
    """

    GPIO = 0
    VPR_GRC = 1
    CAN_PWM_I3C = 2
    SERIAL0 = 3
    EXMIF_RADIO_SERIAL1 = 4
    CAN_TDM_SERIAL2 = 5
    CAN = 6
    TND = 7


# Default CTRLSEL value indicating that CTRLSEL should not be used
CTRLSEL_DEFAULT = Ctrlsel.GPIO
