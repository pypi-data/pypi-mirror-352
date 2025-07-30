# Copyright (c) 2024 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

"""APIs for programmatically generating a UICR structure."""

from __future__ import annotations

import importlib.resources
import json
import textwrap
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, Optional, TypeVar

import svd

from nrfregtool import log
from nrfregtool.platform import (
    DomainID,
    OwnerID,
    Product,
    ProductCode,
    ProcessorID,
    secure_address_get,
    CTRLSEL_DEFAULT,
)
from nrfregtool._common import (
    memory_to_bytes,
    ranges_overlap_inclusive,
)
from nrfregtool._svd_util import (
    SvdEnum,
    content_get_and_extend,
)
from ._common import (
    RegSrcMap,
    UnitSrc,
    Value,
)

# This API is part of the public library API.
# Any change to this API should usually result in a change of the package version.
# In general, do not break this API unless there is a very good reason for it.
# When adding support for new UICR format versions, add it in a backward compatible way.
# The API should be fully backward compatible with every UICR format change.

# Magic word used to identify the UICR header structure
UICR_MAGIC = 0x55494352


# Version tuple type
class UicrVersion(NamedTuple):
    major: int
    minor: int
    patch: int
    tweak: int


# List of all supported UICR format versions
UICR_VERSIONS: list[UicrVersion] = [UicrVersion(major=1, minor=0, patch=0, tweak=0)]

# Tuple containing the minimum supported UICR format version
UICR_VERSION_MIN = UICR_VERSIONS[0]

# Tuple containing the maximum supported UICR format version
UICR_VERSION_MAX = UICR_VERSIONS[-1]

# Tuple containing the default UICR format version
UICR_VERSION_DEFAULT = UICR_VERSION_MAX

# Fill value for empty non-volatile memory
_EMPTY_NVM_SPACE = 0xFF


class UicrError(RuntimeError):
    """Error raised by the UICR builder API"""

    ...


class UicrVersionError(UicrError):
    """Error raised when the UICR builder API is given an unsupported UICR version"""

    def __init__(
        self,
        got_version: UicrVersion,
        /,
    ) -> None:
        supported_versions = ["'{}.{}.{}+{}'".format(*v) for v in UICR_VERSIONS]
        super(UicrVersionError, self).__init__(
            "Unsupported UICR version "
            + "'{}.{}.{}+{}'. ".format(*got_version)
            + f"This package supports versions {supported_versions}"
        )


T = TypeVar("T")


def _value_unpack(value: T | Value[T]) -> tuple[T, Optional[UnitSrc]]:
    if isinstance(value, Value):
        return value.val, value.src
    return value, None


@dataclass
class Header:
    """Metadata describing the UICR structure itself.

    :var part_code: Part code of the product the UICR is generated for.
    :var hardware_revision: Hardware revision of the product the UICR is generated for.
    :var domain: domain ID of the local domain the UICR is associated with.
    """

    part_code: int | Value[int]
    hardware_revision: int | Value[int]
    domain: int | Value[int]


@dataclass
class Memory:
    """Owned global memory region.

    :var address: start address of the region.
    :var size: size of the region.
    :var access: list of access permissions for the region.
    """

    address: int | Value[int]
    size: int | Value[int]
    access: list[Access]

    @dataclass
    class Access:
        """Memory region access permissions.

        :var owner: owner ID of the owner the permissions are given to.
        :var read: the owner has read permissions.
        :var write: the owner has write permissions.
        :var execute: the owner has execute permissions.
        :var secure: access is limited to secure mode.
        :var non_secure_callable: memory region is non-secure callable.
        """

        owner: int | Value[int]
        read: bool | Value[bool] = False
        write: bool | Value[bool] = False
        execute: bool | Value[bool] = False
        secure: bool | Value[bool] = False
        non_secure_callable: bool | Value[bool] = False


@dataclass
class Mailbox:
    """SSF IPC buffer configuration.

    :var tx_address: start address of the TX buffer.
    :var tx_size: size of the TX buffer.
    :var rx_address: start address of the RX buffer.
    :var rx_size: size of the RX buffer.
    """

    tx_address: int | Value[int]
    tx_size: int | Value[int]
    rx_address: int | Value[int]
    rx_size: int | Value[int]


@dataclass
class Peripheral:
    """Owned global domain peripheral configuration.

    :var address: base address of the peripheral.
    :var irq_processor: processor ID of the processor that will receive the peripheral IRQ.
    :var secure: access is limited to secure mode.
    :var dma_secure: DMA is limited to secure mode, if applicable.
    """

    address: int | Value[int]
    irq_processor: int | Value[int]
    secure: bool | Value[bool] = False
    dma_secure: bool | Value[bool] = False


@dataclass
class Pin:
    """Owned GPIO pin configuration.

    :var num: pin number.
    :var secure: access is limited to secure mode.
    :var ctrlsel: CTRLSEL setting for the pin.
    """

    num: int | Value[int]
    secure: bool | Value[bool] = False
    ctrlsel: int | Value[int] = CTRLSEL_DEFAULT


@dataclass
class Feature:
    """Generic configuration of an owned feature in a global domain peripheral with split ownership.

    :var num: feature index.
    :var secure: access is limited to secure mode.
    """

    num: int | Value[int]
    secure: bool | Value[bool] = False


@dataclass
class DppiLink:
    """A link between a PPI channel in one PPI domain with the neighboring PPI domain.

    :var channel_num: PPI channel number.
    :var direction: link direction.
    """

    channel_num: int | Value[int]
    direction: Direction | Value[Direction]

    class Direction(str, Enum):
        SOURCE = "source"
        SINK = "sink"


@dataclass
class IpcLink:
    """A link between two IPCT channels.

    :var source_domain: domain ID of the source IPCT peripheral.
    :var source_channel_num: channel number in the source IPCT peripheral.
    :var sink_domain: domain ID of the sink IPCT peripheral.
    :var sink_channel_num: channel number in the sink IPCT peripheral.
    """

    source_domain: int | Value[int]
    source_channel_num: int | Value[int]
    sink_domain: int | Value[int]
    sink_channel_num: int | Value[int]


@dataclass
class Trace:
    """A link between a TDD trace source and sink.

    :var processor: processor ID of the processor the trace source corresponds to.
    :var source: trace source.
    :var sink: trace sink.
    """

    processor: int | Value[int]
    source: Source | Value[Source]
    sink: Sink | Value[Sink]

    class Source(str, Enum):
        STM = "stm"
        ETM = "etm"
        STM_LOCAL = "stm-local"
        STM_HW_EVENTS = "stm-hw-events"

    class Sink(str, Enum):
        ETB = "etb"
        TPIU = "tpiu"
        ETR = "etr"


@dataclass
class TracePortConfig:
    """Trace port configuration.

    :var speed: TPIU clock divisor.
    """

    speed: int | Value[int]


@dataclass
class EtrBuffer:
    """ETR buffer configuration.

    :var address: start address of the ETR buffer.
    :var size: size of the ETR buffer.
    """

    address: int | Value[int]
    size: int | Value[int]


class Uicr:
    """Builder used to construct a UICR programmatically
    and output the structure in various formats.
    """

    def __init__(
        self, version: UicrVersion | Value[UicrVersion] = UICR_VERSION_DEFAULT
    ) -> None:
        log.trace_function()

        version, version_src = _value_unpack(version)
        if version not in UICR_VERSIONS:
            raise UicrVersionError(version)

        uicr_svd = importlib.resources.files("nrfregtool.resources").joinpath(
            "uicr.svd"
        )
        with importlib.resources.as_file(uicr_svd) as svd_file:
            device = svd.parse(
                svd_file,
                options=svd.Options(
                    parent_relative_cluster_address=True,
                ),
            )

        self._uicr = device["UICR"]

        self._map = RegSrcMap()

        header = self._uicr["HEADER"]

        self._map.reg_set(header["MAGIC"], UICR_MAGIC, None)

        self._map.reg_set(header["VERSION"]["MAJOR"], version.major, version_src)
        self._map.reg_set(header["VERSION"]["MINOR"], version.minor, version_src)
        self._map.reg_set(header["VERSION"]["PATCH"], version.patch, version_src)
        self._map.reg_set(header["VERSION"]["TWEAK"], version.tweak, version_src)

    def build_debug_info(self) -> str:
        """Create a string containing debug information used for improved error reporting.

        The returned string should be treated as an opaque object.

        :returns: debug information string.
        """
        return json.dumps(self._map.src_dict, indent=2)

    def build_bytes(self) -> bytearray:
        """Encode the UICR as bytes.

        :returns: byte representation of the UICR content.
        """
        log.trace_function()

        return memory_to_bytes(self._uicr.memory_iter(), _EMPTY_NVM_SPACE)

    @classmethod
    def from_bytes(cls, memory: bytearray) -> Uicr:
        """Initialize the UICR from bytes.

        An exception is raised if the length of the input exceeds the size of the UICR structure.
        """
        log.trace_function()

        builder = cls()
        uicr = builder._uicr

        req_address_bounds = uicr.address_bounds
        uicr_size = req_address_bounds[1] - req_address_bounds[0]

        input_size = len(memory)
        if input_size > uicr_size:
            raise UicrError(
                f"Memory with size 0x{input_size:x} "
                f"does not fit in the UICR structure with size 0x{uicr_size:x}"
            )

        for reg in uicr.register_iter(leaf_only=True):
            try:
                content_parts = [memory[a] for a in reg.address_range]
            except KeyError:
                if reg.path[0] == "HEADER":
                    raise UicrError("Memory does not contain a full UICR header")

                # TODO: can we fail for other regs as well here?
                continue

            content = int.from_bytes(content_parts, "little")

            # We don't currently support UICR version conversion.
            # Therefore we check that the blob is the same version that is used by the constructor.
            if reg.path == svd.EPath("HEADER.MAGIC"):
                if content != UICR_MAGIC:
                    raise UicrError(
                        "Memory magic value does not match the UICR magic value. "
                        f"Expected 0x{reg.content:08x}, got 0x{content:08x}"
                    )
            # Need to be able to set reset values
            reg.unconstrain()
            reg.content = content

            if reg.path == svd.EPath("HEADER.VERSION"):
                v_mem = (
                    reg["MAJOR"].content,
                    reg["MINOR"].content,
                    reg["PATCH"].content,
                    reg["TWEAK"].content,
                )
                if v_mem not in UICR_VERSIONS:
                    raise UicrVersionError(v_mem)

        return builder

    def set_header(self, header: Header) -> Uicr:
        """Configure the UICR metadata.

        :param header: header data.
        :returns: builder instance.
        """
        log.trace_function()

        reg = self._uicr["HEADER"]

        part_code, part_code_src = _value_unpack(header.part_code)
        self._map.reg_set(reg["PARTNO"]["PARTNO"], part_code, part_code_src)

        rev, rev_src = _value_unpack(header.hardware_revision)
        self._map.reg_set(reg["HWREVISION"]["HWREVISION"], rev, rev_src)

        domain, domain_src = _value_unpack(header.domain)
        self._map.reg_set(reg["DOMAIN"]["DOMAIN"], domain, domain_src)

        return self

    def set_secure_vtor(self, vtor_addr: int | Value[int]) -> Uicr:
        """Set the initial Vector Table Offset Register for the secure image.

        :param vtor_addr: VTOR address.
        :returns: builder instance.
        """
        log.trace_function()

        self._map.reg_set(
            self._uicr["INITSVTOR"]["INITSVTOR"], *_value_unpack(vtor_addr)
        )
        return self

    def set_nonsecure_vtor(self, vtor_addr: int | Value[int]) -> Uicr:
        """Set the initial Vector Table Offset Register for the nonsecure image.

        :param vtor_addr: VTOR address.
        :returns: builder instance.
        """
        log.trace_function()

        self._map.reg_set(
            self._uicr["INITNSVTOR"]["INITNSVTOR"], *_value_unpack(vtor_addr)
        )
        return self

    def add_memory(self, memory: Memory) -> Uicr:
        """Add an owned global memory region for the local domain.

        :param memory: memory region.
        :returns: builder instance.
        """
        log.trace_function()

        for access in memory.access:
            self._add_memory_with_access(memory, access)
        return self

    def _add_memory_with_access(
        self,
        memory: Memory,
        access: Memory.Access,
    ) -> None:
        addr, addr_src = _value_unpack(memory.address)
        size, size_src = _value_unpack(memory.size)
        addr_end_exc = addr + size
        read, read_src = _value_unpack(access.read)
        write, write_src = _value_unpack(access.write)
        execute, execute_src = _value_unpack(access.execute)
        secure, secure_src = _value_unpack(access.secure)
        owner, owner_src = _value_unpack(access.owner)
        nsc, nsc_src = _value_unpack(access.non_secure_callable)

        mem_entries = self._uicr["MEM"]
        mem_mergeable = []
        for i, mem in enumerate(mem_entries):
            mem_config0 = mem["CONFIG0"]
            mem_config1 = mem["CONFIG1"]

            if not mem_config0.modified:
                # No more occupied entries after this point
                mem_count = i
                # If we found overlapping entries, then we will overwrite the first one.
                # Otherwise, we will overwrite the first vacant entry.
                mem_target = mem_mergeable[0] if mem_mergeable else mem
                break

            mem_addr = content_get_and_extend(mem_config0["ADDRESS"])
            mem_size = content_get_and_extend(mem_config1["SIZE"])
            mem_addr_end_exc = mem_addr + mem_size

            # Check if we can merge this entry with the existing entry
            if ranges_overlap_inclusive(
                addr,
                addr_end_exc,
                mem_addr,
                mem_addr_end_exc,
            ) and (
                mem_config1["OWNERID"].content,
                mem_config0["READ"].modified,
                mem_config0["WRITE"].modified,
                mem_config0["EXECUTE"].modified,
                not mem_config0["SECURE"].modified,
                mem_config0["NSC"].modified,
            ) == (
                owner,
                read,
                write,
                execute,
                secure,
                nsc,
            ):
                mem_mergeable.append(mem)
        else:
            # All entries are occupied
            mem_count = len(mem_entries)
            if not mem_mergeable:
                raise UicrError(
                    f"Too many UICR memory configurations (max: {mem_count})"
                )
            mem_target = mem_mergeable[0]

        # Merge existing entries
        for mem in mem_mergeable:
            mem_addr = content_get_and_extend(mem["CONFIG0"]["ADDRESS"])
            mem_size = content_get_and_extend(mem["CONFIG1"]["SIZE"])
            mem_addr_end_exc = mem_addr + mem_size

            addr = min(addr, mem_addr)
            addr_end_exc = max(addr_end_exc, mem_addr_end_exc)
            size = addr_end_exc - addr

            if mem != mem_target:
                self._map.reg_move(mem_target, mem)

        # Write final values into the target entry
        mem_config0 = mem_target["CONFIG0"]
        mem_config1 = mem_target["CONFIG1"]
        self._map.reg_set(mem_config0["ADDRESS"], addr, addr_src, lsb_truncate=True)
        self._map.reg_set(
            mem_config0["READ"], SvdEnum.allowed_if(access.read), read_src
        )
        self._map.reg_set(mem_config0["WRITE"], SvdEnum.allowed_if(write), write_src)
        self._map.reg_set(
            mem_config0["EXECUTE"], SvdEnum.allowed_if(execute), execute_src
        )
        self._map.reg_set(mem_config0["SECURE"], SvdEnum.secure_if(secure), secure_src)
        self._map.reg_set(mem_config0["NSC"], SvdEnum.enabled_if(nsc), nsc_src)
        self._map.reg_set(mem_config1["SIZE"], size, size_src, lsb_truncate=True)
        self._map.reg_set(mem_config1["OWNERID"], owner, owner_src)

        # Move occupied entries to fill any gaps left by the merging procedure
        mem_gaps = mem_mergeable[1:]
        if not mem_gaps:
            return
        for mem in mem_entries[mem_count - 1 :: -1]:
            if mem == mem_gaps[-1]:
                # Nothing to fill
                mem_gaps.pop()
            else:
                self._map.reg_move(mem_gaps.pop(0), mem)

            if not mem_gaps:
                break

    def add_peripheral(self, peripheral: Peripheral) -> Uicr:
        """Add and configure an owned global domain peripheral for the local domain.

        :param peripheral: peripheral.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(peripheral.address)
        secure_addr = secure_address_get(addr)
        for reg in self._uicr["PERIPH"]:
            cfg = reg["CONFIG"]
            if (
                not cfg.modified
                or content_get_and_extend(cfg["ADDRESS"]) == secure_addr
            ):
                break
        else:
            raise UicrError(
                f"Too many entries in PERIPH (max: {len(self._uicr['PERIPH'])})"
            )

        if not reg["CONFIG"].modified:
            self._map.reg_set(
                reg["CONFIG"]["ADDRESS"], secure_addr, addr_src, lsb_truncate=True
            )

        irq_processor, irq_processor_src = _value_unpack(peripheral.irq_processor)
        reg_processor = reg["CONFIG"]["PROCESSOR"]
        if reg_processor.modified and reg_processor.content != irq_processor:
            raise UicrError(
                f"Conflicting IRQ processor for peripheral 0x{addr:08x}: "
                f"{reg_processor.content}, {irq_processor}"
            )
        self._map.reg_set(reg_processor, irq_processor, irq_processor_src)

        secure, secure_src = _value_unpack(peripheral.secure)
        self._map.reg_set(
            reg["CONFIG"]["SECURE"],
            _resolve_secure(reg["CONFIG"]["SECURE"], secure),
            secure_src,
        )

        dma_secure, dma_secure_src = _value_unpack(peripheral.dma_secure)
        self._map.reg_set(
            reg["CONFIG"]["DMASEC"],
            _resolve_secure(reg["CONFIG"]["DMASEC"], dma_secure),
            dma_secure_src,
        )

        return self

    def add_grtc_channel(self, channel: Feature) -> Uicr:
        """Add an owned GRTC channel for the local domain.

        :param channel: GRTC channel.
        :returns: builder instance.
        """
        log.trace_function()

        reg = self._uicr["GRTC"]
        num, num_src = _value_unpack(channel.num)
        self._map.reg_set(reg["CC"]["OWN"][f"CC_{num}"], SvdEnum.OWN, num_src)
        secure, secure_src = _value_unpack(channel.secure)
        self._map.reg_set(
            reg["CC"]["SECURE"][f"CC_{num}"],
            _resolve_secure(reg["CC"]["SECURE"][f"CC_{num}"], secure),
            secure_src,
        )

        return self

    def add_gpiote_channel(
        self,
        gpiote_addr: int | Value[int],
        channel: Feature,
    ) -> Uicr:
        """Add an owned global domain GPIOTE channel for the local domain.

        :param gpiote_addr: base address of the GPIOTE peripheral.
        :param channel: GPIOTE channel.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(gpiote_addr)
        secure_addr = secure_address_get(addr)
        _, reg = _alloc_instanced_reg(self._uicr["GPIOTE"], secure_addr)

        if not reg["INSTANCE"].modified:
            self._map.reg_set(reg["INSTANCE"]["ADDRESS"], secure_addr, addr_src)

        num, num_src = _value_unpack(channel.num)
        self._map.reg_set(reg["CH"]["OWN"][f"CH_{num}"], SvdEnum.OWN, num_src)
        secure, secure_src = _value_unpack(channel.secure)
        self._map.reg_set(
            reg["CH"]["SECURE"][f"CH_{num}"],
            _resolve_secure(reg["CH"]["SECURE"][f"CH_{num}"], secure),
            secure_src,
        )

        return self

    def add_dppi_channel(
        self,
        dppic_addr: int | Value[int],
        channel: Feature,
    ) -> Uicr:
        """Add an owned global domain DPPI channel for the local domain.

        :param dppic_addr: base address of the DPPIC peripheral managing the PPI domain.
        :param channel: PPI channel.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(dppic_addr)
        secure_addr = secure_address_get(addr)
        _, reg = _alloc_instanced_reg(self._uicr["DPPI"], secure_addr)

        if not reg["INSTANCE"].modified:
            self._map.reg_set(reg["INSTANCE"]["ADDRESS"], secure_addr, addr_src)

        num, num_src = _value_unpack(channel.num)
        self._map.reg_set(reg["CH"]["OWN"][f"CH_{num}"], SvdEnum.OWN, num_src)
        secure, secure_src = _value_unpack(channel.secure)
        self._map.reg_set(
            reg["CH"]["SECURE"][f"CH_{num}"],
            _resolve_secure(reg["CH"]["SECURE"][f"CH_{num}"], secure),
            secure_src,
        )

        return self

    def add_dppi_channel_group(
        self,
        dppic_addr: int | Value[int],
        channel_group: Feature,
    ) -> Uicr:
        """Add an owned global domain DPPI group for the local domain.

        :param dppic_addr: base address of the DPPIC peripheral managing the PPI domain.
        :param channel_group: PPI channel group.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(dppic_addr)
        secure_addr = secure_address_get(addr)
        _, reg = _alloc_instanced_reg(self._uicr["DPPI"], secure_addr)

        if not reg["INSTANCE"].modified:
            self._map.reg_set(reg["INSTANCE"]["ADDRESS"], secure_addr, addr_src)

        num, num_src = _value_unpack(channel_group.num)
        self._map.reg_set(reg["CHG"]["OWN"][f"CHG_{num}"], SvdEnum.OWN, num_src)
        secure, secure_src = _value_unpack(channel_group.secure)
        self._map.reg_set(
            reg["CHG"]["SECURE"][f"CHG_{num}"],
            _resolve_secure(reg["CHG"]["SECURE"][f"CHG_{num}"], secure),
            secure_src,
        )

        return self

    def add_dppi_link(
        self,
        dppic_addr: int | Value[int],
        link: DppiLink,
    ) -> Uicr:
        """Link a global domain DPPI channel with a neighboring PPI domain.

        :param dppic_addr: base address of the DPPIC peripheral managing the PPI domain.
        :param link: PPI channel link description.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(dppic_addr)
        secure_addr = secure_address_get(addr)
        _, reg = _alloc_instanced_reg(self._uicr["DPPI"], secure_addr)

        if not reg["INSTANCE"].modified:
            self._map.reg_set(reg["INSTANCE"]["ADDRESS"], secure_addr, addr_src)

        direction, direction_src = _value_unpack(link.direction)
        if direction == DppiLink.Direction.SINK:
            dir_enum = SvdEnum.SINK
        elif direction == DppiLink.Direction.SOURCE:
            dir_enum = SvdEnum.SOURCE
        else:
            raise ValueError(f"Unrecognized DPPI link direction: {direction}")

        num, num_src = _value_unpack(link.channel_num)
        reg_en = reg["CH"]["LINK"]["EN"][f"CH_{num}"]
        reg_dir = reg["CH"]["LINK"]["DIR"][f"CH_{num}"]
        if reg_en.content_enum == SvdEnum.ENABLED and reg_dir.content_enum != dir_enum:
            raise UicrError(
                f"Conflicting link direction for DPPIC 0x{addr:08x}: "
                f"{reg_dir.content_enum.lower()}, {dir_enum.lower()}"
            )
        self._map.reg_set(reg_en, SvdEnum.ENABLED, num_src)
        self._map.reg_set(reg_dir, dir_enum, direction_src)

        return self

    def add_ipct_channel(
        self,
        ipct_addr: int | Value[int],
        channel: Feature,
    ) -> Uicr:
        """Add an owned global domain IPCT channel for the local domain.

        :param ipct_addr: base address of the IPCT peripheral.
        :param channel: IPCT channel.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(ipct_addr)
        secure_addr = secure_address_get(addr)
        _, reg = _alloc_instanced_reg(self._uicr["IPCT"], secure_addr)

        if not reg["INSTANCE"].modified:
            self._map.reg_set(reg["INSTANCE"]["ADDRESS"], secure_addr, addr_src)

        num, num_src = _value_unpack(channel.num)
        self._map.reg_set(reg["CH"]["OWN"][f"CH_{num}"], SvdEnum.OWN, num_src)
        secure, secure_src = _value_unpack(channel.secure)
        self._map.reg_set(
            reg["CH"]["SECURE"][f"CH_{num}"],
            _resolve_secure(reg["CH"]["SECURE"][f"CH_{num}"], secure),
            secure_src,
        )

        return self

    def add_ipct_interrupt(
        self,
        ipct_addr: int | Value[int],
        interrupt: Feature,
    ) -> Uicr:
        """Add an owned global domain IPCT interrupt for the local domain.

        :param ipct_addr: base address of the IPCT peripheral.
        :param interrupt: IPCT interrupt.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(ipct_addr)
        secure_addr = secure_address_get(addr)
        _, reg = _alloc_instanced_reg(self._uicr["IPCT"], secure_addr)

        if not reg["INSTANCE"].modified:
            self._map.reg_set(reg["INSTANCE"]["ADDRESS"], secure_addr, addr_src)

        num, num_src = _value_unpack(interrupt.num)
        self._map.reg_set(reg["INTERRUPT"]["OWN"][f"INT_{num}"], SvdEnum.OWN, num_src)
        secure, secure_src = _value_unpack(interrupt.secure)
        self._map.reg_set(
            reg["INTERRUPT"]["SECURE"][f"INT_{num}"],
            _resolve_secure(reg["INTERRUPT"]["SECURE"][f"INT_{num}"], secure),
            secure_src,
        )

        return self

    def add_ipc_link(
        self,
        link: IpcLink,
    ) -> Uicr:
        """Link two IPCT channels together.

        :param link: IPCT channel link description.
        :returns: builder instance.
        """
        log.trace_function()

        source_domain, source_domain_src = _value_unpack(link.source_domain)
        source_num, source_num_src = _value_unpack(link.source_channel_num)
        sink_domain, sink_domain_src = _value_unpack(link.sink_domain)
        sink_num, sink_num_src = _value_unpack(link.sink_channel_num)

        for reg in self._uicr["IPCMAP"]:
            if not reg.modified or (
                reg["DOMAINIDSOURCE"].content,
                reg["IPCTCHSOURCE"].content,
                reg["DOMAINIDSINK"].content,
                reg["IPCTCHSINK"].content,
            ) == (source_domain, source_num, sink_domain, sink_num):
                self._map.reg_set(
                    reg["DOMAINIDSOURCE"], source_domain, source_domain_src
                )
                self._map.reg_set(reg["IPCTCHSOURCE"], source_num, source_num_src)
                self._map.reg_set(reg["DOMAINIDSINK"], sink_domain, sink_domain_src)
                self._map.reg_set(reg["IPCTCHSINK"], sink_num, sink_num_src)
                break
        else:
            raise UicrError(
                f"Too many entries in IPCMAP (max: {len(self._uicr['IPCMAP'])})"
            )

        return self

    def add_gpio_pin(self, gpio_addr: int | Value[int], pin: Pin) -> Uicr:
        """Add and configure an owned GPIO pin for the local domain.

        :param gpio_addr: base address of the GPIO peripheral.
        :param pin: GPIO pin description.
        :returns: builder instance.
        """
        log.trace_function()

        addr, addr_src = _value_unpack(gpio_addr)
        secure_addr = secure_address_get(addr)
        i, reg = _alloc_instanced_reg(self._uicr["GPIO"], secure_addr)

        if not reg["INSTANCE"].modified:
            self._map.reg_set(reg["INSTANCE"]["ADDRESS"], secure_addr, addr_src)

        num, num_src = _value_unpack(pin.num)
        self._map.reg_set(reg["OWN"][f"PIN_{num}"], SvdEnum.OWN, num_src)
        secure, secure_src = _value_unpack(pin.secure)
        self._map.reg_set(
            reg["SECURE"][f"PIN_{num}"],
            _resolve_secure(reg["SECURE"][f"PIN_{num}"], secure),
            secure_src,
        )
        ctrlsel, ctrlsel_src = _value_unpack(pin.ctrlsel)
        reg_ctrlsel = self._uicr["GPIO_PIN"][i]["CTRLSEL"][num]["CTRLSEL"]
        if reg_ctrlsel.modified and not (
            reg_ctrlsel.content == CTRLSEL_DEFAULT
            or ctrlsel == CTRLSEL_DEFAULT
            or ctrlsel == reg_ctrlsel.content
        ):
            raise UicrError(
                f"Conflicting CTRLSEL for GPIO 0x{addr:08x} pin {num}: "
                f"{reg_ctrlsel.content}, {ctrlsel}"
            )

        if not reg_ctrlsel.modified or ctrlsel != CTRLSEL_DEFAULT:
            self._map.reg_set(reg_ctrlsel, ctrlsel, ctrlsel_src)

        return self

    def set_secure_mailbox(self, mailbox: Mailbox) -> Uicr:
        """Configure the secure mode SSF IPC buffers for the local domain.

        :param mailbox: IPC buffer configuration.
        :returns: builder instance.
        """
        log.trace_function()

        reg = self._uicr["MAILBOX"]["SECURE"]

        self._map.reg_set(
            reg["TX_CONFIG0"]["ADDRESS"],
            *_value_unpack(mailbox.tx_address),
            lsb_truncate=True,
        )
        self._map.reg_set(
            reg["TX_CONFIG1"]["SIZE"],
            *_value_unpack(mailbox.tx_size),
            lsb_truncate=True,
        )
        self._map.reg_set(
            reg["RX_CONFIG0"]["ADDRESS"],
            *_value_unpack(mailbox.rx_address),
            lsb_truncate=True,
        )
        self._map.reg_set(
            reg["RX_CONFIG1"]["SIZE"],
            *_value_unpack(mailbox.rx_size),
            lsb_truncate=True,
        )

        return self

    def add_trace_link(self, link: Trace) -> Uicr:
        """Link a TDD trace source to a trace sink.

        :param link: trace link description.
        :returns: builder instance.
        """
        log.trace_function()

        sink, sink_src = _value_unpack(link.sink)
        if sink == Trace.Sink.ETB:
            reg = self._uicr["TRACE"]["ETBSINK"]["SOURCES"]
        elif sink == Trace.Sink.TPIU:
            reg = self._uicr["TRACE"]["TPIUSINK"]["SOURCES"]
        elif sink == Trace.Sink.ETR:
            reg = self._uicr["TRACE"]["ETRSINK"]["SOURCES"]
        else:
            raise ValueError(f"Invalid sink {link.sink}")

        source, source_src = _value_unpack(link.source)
        processor, processor_src = _value_unpack(link.processor)
        match (source, processor):
            case (Trace.Source.STM, ProcessorID.PPR):
                reg = reg["STMPPR"]
            case (Trace.Source.STM, ProcessorID.FLPR):
                reg = reg["STMFLPR"]
            case (Trace.Source.STM, ProcessorID.BBPR):
                reg = reg["STMBBPR"]
            case (Trace.Source.STM, _):
                reg = reg["STMMAINCORE"]
            case (Trace.Source.STM_HW_EVENTS, _):
                reg = reg["STMHWEVENTS"]
            case (Trace.Source.ETM, _):
                reg = reg["ETMMAINCORE"]
            case (Trace.Source.STM_LOCAL, _):
                raise NotImplementedError(
                    "Local STM trace links are not yet suppported"
                )
            case _:
                raise ValueError(f"Unrecognized trace link config: {link}")

        src_combined = []
        if processor_src is not None:
            src_combined.append(processor_src)
        if source_src is not None:
            src_combined.append(source_src)
        if sink_src is not None:
            src_combined.append(sink_src)

        self._map.reg_set(
            reg, SvdEnum.REQUESTED, src_combined if src_combined else None
        )

        return self

    def set_trace_port_config(self, config: TracePortConfig) -> Uicr:
        """Configure the trace port.

        :param config: trace port configuration.
        :returns: builder instance.
        """
        log.trace_function()

        self._map.reg_set(
            self._uicr["TRACE"]["PORTCONFIG"]["PORTCONFIG"],
            *_value_unpack(config.speed),
        )
        return self

    def set_etr_buffer(self, buffer: EtrBuffer) -> Uicr:
        """Configure the ETR buffer.

        :param buffer: ETR buffer configuration.
        :returns: builder instance.
        """
        log.trace_function()

        reg = self._uicr["TRACE"]["ETRBUF"]
        self._map.reg_set(
            reg["CONFIG0"]["ADDRESS"], *_value_unpack(buffer.address), lsb_truncate=True
        )
        self._map.reg_set(
            reg["CONFIG1"]["SIZE"], *_value_unpack(buffer.size), lsb_truncate=True
        )
        return self

    def pretty_print(self, *, verbose: bool = False) -> str:
        """Format the UICR as a human readable string.

        :param verbose: include exhaustive details about the UICR.
        :returns: human readable UICR
        """
        lines = []

        lines.append(self._pp_header(verbose=verbose))
        if vtor_str := self._pp_vtor(verbose=verbose):
            lines.append(_indent(vtor_str, 1))
        if memory_str := self._pp_memory(verbose=verbose):
            lines.append(_indent(memory_str, 1))
        if mailbox_str := self._pp_mailbox(verbose=verbose):
            lines.append(_indent(mailbox_str, 1))
        if periph_str := self._pp_periph(verbose=verbose):
            lines.append(_indent(periph_str, 1))
        if gpio_str := self._pp_gpio(verbose=verbose):
            lines.append(_indent(gpio_str, 1))
        if gpiote_str := self._pp_gpiote(verbose=verbose):
            lines.append(_indent(gpiote_str, 1))
        if grtc_str := self._pp_grtc(verbose=verbose):
            lines.append(_indent(grtc_str, 1))
        if dppi_str := self._pp_dppi(verbose=verbose):
            lines.append(_indent(dppi_str, 1))
        if ipct_str := self._pp_ipct(verbose=verbose):
            lines.append(_indent(ipct_str, 1))
        if ipcmap_str := self._pp_ipcmap(verbose=verbose):
            lines.append(_indent(ipcmap_str, 1))
        if trace_str := self._pp_trace(verbose=verbose):
            lines.append(_indent(trace_str, 1))

        return "\n".join(lines)

    def _pp_header(self, *, verbose: bool = False) -> str:
        uicr_header = self._uicr["HEADER"]
        version = (
            f"{uicr_header['VERSION']['MAJOR'].content}"
            f".{uicr_header['VERSION']['MINOR'].content}"
            f".{uicr_header['VERSION']['PATCH'].content}"
            f"+{uicr_header['VERSION']['TWEAK'].content}"
        )
        product_code = ProductCode(
            part_number=uicr_header["PARTNO"]["PARTNO"].content,
            revision=uicr_header["HWREVISION"]["HWREVISION"].content,
        )
        for product in Product:
            if product.product_code == product_code:
                product_name = product.name
                break
        else:
            product_name = f"Part no. 0x{product_code.part_number:x}, Rev. 0x{product_code.revision:x}"
        domain = uicr_header["DOMAIN"]["DOMAIN"].content
        try:
            domain_name = f"{DomainID(domain).name}"
        except Exception:
            domain_name = f"domain {domain}"

        return f"{product_name} {domain_name} UICR v{version}"

    def _pp_vtor(self, *, verbose: bool = False) -> str:
        lines = []

        if self._uicr["INITSVTOR"].modified:
            svtor = f"S: 0x{self._uicr['INITSVTOR']['INITSVTOR'].content:08x}"
        else:
            svtor = ""

        if self._uicr["INITNSVTOR"].modified:
            nsvtor = f"NS: 0x{self._uicr['INITNSVTOR']['INITNSVTOR'].content:08x}"
        else:
            nsvtor = ""

        if svtor or nsvtor:
            lines.append("Initial VTORs:")
            if svtor:
                lines.append(_indent(svtor, 1))
            if nsvtor:
                lines.append(_indent(nsvtor, 1))

        return "\n".join(lines)

    def _pp_memory(self, *, verbose: bool = False) -> str:
        lines = []
        mem_entries = []

        for i, uicr_mem in enumerate(self._uicr["MEM"]):
            if not uicr_mem["CONFIG0"].modified:
                break

            mem_address_val = content_get_and_extend(uicr_mem["CONFIG0"]["ADDRESS"])
            mem_size_val = content_get_and_extend(uicr_mem["CONFIG1"]["SIZE"])
            mem_address = f"0x{mem_address_val:x}"
            mem_size = f"0x{mem_size_val:x}"
            mem_address_end = f"0x{mem_address_val + mem_size_val:x}"
            mem_access_owner_val = uicr_mem["CONFIG1"]["OWNERID"].content
            try:
                mem_access_owner = OwnerID(mem_access_owner_val).name
            except Exception:
                mem_access_owner = str(mem_access_owner_val)
            read_str = (
                "R"
                if uicr_mem["CONFIG0"]["READ"].content_enum == SvdEnum.ALLOWED
                else ""
            )
            write_str = (
                "W"
                if uicr_mem["CONFIG0"]["WRITE"].content_enum == SvdEnum.ALLOWED
                else ""
            )
            execute_str = (
                "X"
                if uicr_mem["CONFIG0"]["EXECUTE"].content_enum == SvdEnum.ALLOWED
                else ""
            )
            secure_str = (
                "S"
                if uicr_mem["CONFIG0"]["SECURE"].content_enum == SvdEnum.SECURE
                else ""
            )
            mem_access = (
                f"{mem_access_owner}:{read_str}{write_str}{execute_str}{secure_str}"
            )

            for memory in mem_entries:
                if memory["address"] == mem_address and memory["size"] == mem_size:
                    memory["access"].append((i, mem_access))
                    break
            else:
                config_mem = {
                    "address": mem_address,
                    "address_end": mem_address_end,
                    "size": mem_size,
                    "access": [(i, mem_access)],
                }
                mem_entries.append(config_mem)

        if mem_entries:
            lines.append("Owned Memory:")
            for entry in mem_entries:
                numbers = ", ".join((f"#{i}" for i, _ in entry["access"]))
                access = ", ".join((a for _, a in entry["access"]))
                lines.append(
                    _indent(
                        f"{numbers}: [{entry['address']} - {entry['address_end']}) "
                        f"({entry['size']}) [{access}]",
                        1,
                    )
                )

        return "\n".join(lines)

    def _pp_mailbox(self, *, verbose: bool = False) -> str:
        lines = []
        uicr_sec_mailbox = self._uicr["MAILBOX"]["SECURE"]
        if uicr_sec_mailbox["TX_CONFIG0"].modified:
            tx_addr_val = content_get_and_extend(
                uicr_sec_mailbox["TX_CONFIG0"]["ADDRESS"]
            )
            tx_size_val = content_get_and_extend(uicr_sec_mailbox["TX_CONFIG1"]["SIZE"])
            rx_addr_val = content_get_and_extend(
                uicr_sec_mailbox["RX_CONFIG0"]["ADDRESS"]
            )
            rx_size_val = content_get_and_extend(uicr_sec_mailbox["RX_CONFIG1"]["SIZE"])
            lines.append("Secure SSF buffer:")
            lines.append(
                _indent(
                    f"TX: [0x{tx_addr_val:08x} - 0x{tx_addr_val + tx_size_val:08x}) "
                    f"(0x{tx_size_val:x})",
                    1,
                )
            )
            lines.append(
                _indent(
                    f"RX: [0x{rx_addr_val:08x} - 0x{rx_addr_val + rx_size_val:08x}) "
                    f"(0x{rx_size_val:x})",
                    1,
                )
            )
        return "\n".join(lines)

    def _pp_periph(self, *, verbose: bool = False) -> str:
        lines = []

        if self._uicr["PERIPH"][0]["CONFIG"].modified:
            lines.append("Owned peripherals:")

        for i, uicr_periph in enumerate(self._uicr["PERIPH"]):
            if not uicr_periph["CONFIG"].modified:
                break

            address = (
                f"0x{content_get_and_extend(uicr_periph['CONFIG']['ADDRESS']):08x}"
            )
            irq_processor_val = uicr_periph["CONFIG"]["PROCESSOR"].content
            try:
                irq_processor = ProcessorID(irq_processor_val).name
            except Exception:
                irq_processor = str(irq_processor_val)
            secure = (
                "S"
                if uicr_periph["CONFIG"]["SECURE"].content_enum == SvdEnum.SECURE
                else "NS"
            )
            dma_secure = (
                "DMA-S"
                if uicr_periph["CONFIG"]["DMASEC"].content_enum == SvdEnum.SECURE
                else "DMA-NS"
            )
            lines.append(
                _indent(
                    f"#{i}: {address} [{secure}, {dma_secure}, IRQ->{irq_processor}]", 1
                )
            )

        return "\n".join(lines)

    def _pp_gpiote(self, *, verbose: bool = False) -> str:
        lines = []

        for i, uicr_gpiote in enumerate(self._uicr["GPIOTE"]):
            if not uicr_gpiote["INSTANCE"].modified:
                break

            address = (
                f"0x{content_get_and_extend(uicr_gpiote['INSTANCE']['ADDRESS']):08x}"
            )
            lines.append(f"GPIOTE#{i} @ {address}")

            owned_channels = _pretty_print_owned_common(
                uicr_gpiote["CH"]["OWN"], uicr_gpiote["CH"]["SECURE"]
            )
            lines.append(_indent(f"owned channels: {owned_channels}", 1))

        return "\n".join(lines)

    def _pp_ipct(self, *, verbose: bool = False) -> str:
        lines = []

        for i, uicr_ipct in enumerate(self._uicr["IPCT"]):
            if not uicr_ipct["INSTANCE"].modified:
                break

            address = (
                f"0x{content_get_and_extend(uicr_ipct['INSTANCE']['ADDRESS']):08x}"
            )
            lines.append(f"IPCT#{i} @ {address}")

            if uicr_ipct["CH"]["OWN"].modified:
                owned_channels = _pretty_print_owned_common(
                    uicr_ipct["CH"]["OWN"], uicr_ipct["CH"]["SECURE"]
                )
                lines.append(_indent(f"owned channels: {owned_channels}", 1))

            if uicr_ipct["INTERRUPT"]["OWN"].modified:
                owned_interrupts = _pretty_print_owned_common(
                    uicr_ipct["INTERRUPT"]["OWN"],
                    uicr_ipct["INTERRUPT"]["SECURE"],
                )
                lines.append(_indent(f"owned interrupts: {owned_interrupts}", 1))

        return "\n".join(lines)

    def _pp_ipcmap(self, *, verbose: bool = False) -> str:
        lines = []

        if self._uicr["IPCMAP"][0].modified:
            lines.append("IPC mapping:")

        for i, uicr_ipcmap in enumerate(self._uicr["IPCMAP"]):
            if not uicr_ipcmap.modified:
                break

            source_domain_val = uicr_ipcmap["DOMAINIDSOURCE"].content
            try:
                source_domain = DomainID(source_domain_val).name
            except Exception:
                source_domain = str(source_domain_val)
            source_channel_num = uicr_ipcmap["IPCTCHSOURCE"].content

            sink_domain_val = uicr_ipcmap["DOMAINIDSINK"].content
            try:
                sink_domain = DomainID(sink_domain_val).name
            except Exception:
                sink_domain = str(sink_domain_val)
            sink_channel_num = uicr_ipcmap["IPCTCHSINK"].content

            lines.append(
                _indent(
                    f"#{i}: "
                    f"{source_domain} ch{source_channel_num} -> {sink_domain} ch{sink_channel_num}",
                    1,
                )
            )

        return "\n".join(lines)

    def _pp_dppi(self, *, verbose: bool = False) -> str:
        lines = []

        for i, uicr_dppi in enumerate(self._uicr["DPPI"]):
            if not uicr_dppi["INSTANCE"].modified:
                break

            address = (
                f"0x{content_get_and_extend(uicr_dppi['INSTANCE']['ADDRESS']):08x}"
            )
            lines.append(f"DPPIC#{i} @ {address}")

            if uicr_dppi["CH"]["OWN"].modified:
                owned_channels = _pretty_print_owned_common(
                    uicr_dppi["CH"]["OWN"], uicr_dppi["CH"]["SECURE"]
                )
                lines.append(_indent(f"owned channels: {owned_channels}", 1))

            if uicr_dppi["CHG"]["OWN"].modified:
                owned_channel_groups = _pretty_print_owned_common(
                    uicr_dppi["CHG"]["OWN"], uicr_dppi["CHG"]["SECURE"]
                )
                lines.append(
                    _indent(f"owned channel groups: {owned_channel_groups}", 1)
                )

            if uicr_dppi["CH"]["LINK"]["EN"].modified:
                source_links = []
                sink_links = []

                enabled = uicr_dppi["CH"]["LINK"]["EN"]
                direction = uicr_dppi["CH"]["LINK"]["DIR"]

                for i, (en_i, dir_i) in enumerate(
                    zip(enabled.values(), direction.values())
                ):
                    if en_i.content_enum not in (SvdEnum.LINKED, SvdEnum.ENABLED):
                        continue
                    if dir_i.content_enum == SvdEnum.SOURCE:
                        source_links.append(str(i))
                    else:
                        sink_links.append(str(i))

                if source_links:
                    lines.append(
                        _indent(f"source channels: {', '.join(source_links)}", 1)
                    )
                if sink_links:
                    lines.append(_indent(f"sink channels: {', '.join(sink_links)}", 1))

        return "\n".join(lines)

    def _pp_grtc(self, *, verbose: bool = False) -> str:
        lines = []

        if self._uicr["GRTC"]["CC"]["OWN"].modified:
            lines.append("GRTC:")
            owned_channels = _pretty_print_owned_common(
                self._uicr["GRTC"]["CC"]["OWN"],
                self._uicr["GRTC"]["CC"]["SECURE"],
            )
            lines.append(_indent(f"owned channels: {owned_channels}", 1))

        return "\n".join(lines)

    def _pp_gpio(self, *, verbose: bool = False) -> str:
        lines = []

        for i, uicr_gpio in enumerate(self._uicr["GPIO"]):
            if not uicr_gpio["INSTANCE"].modified:
                continue

            address = (
                f"0x{content_get_and_extend(uicr_gpio['INSTANCE']['ADDRESS']):08x}"
            )
            lines.append(f"GPIO#{i} @ {address}")

            entries = []
            for j, (own, sec) in enumerate(
                zip(uicr_gpio["OWN"].values(), uicr_gpio["SECURE"].values())
            ):
                owned = not own.content
                if not owned:
                    continue

                secure = "S" if sec.content_enum == SvdEnum.SECURE else "NS"
                uicr_ctrlsel = self._uicr["GPIO_PIN"][i]["CTRLSEL"][j]
                if uicr_ctrlsel.modified and uicr_ctrlsel.content != 0:
                    pin_ctrlsel = f" [ctrlsel={uicr_ctrlsel.content}]"
                else:
                    pin_ctrlsel = ""

                entries.append(f"{j}:{secure}{pin_ctrlsel}")

            owned_pins = ", ".join(entries)
            lines.append(_indent(f"owned pins: {owned_pins}", 1))

        return "\n".join(lines)

    def _pp_trace(self, *, verbose: bool = False) -> str:
        default_processor = ProcessorID.from_domain(
            self._uicr["HEADER"]["DOMAIN"]["DOMAIN"].content
        )
        uicr_trace = self._uicr["TRACE"]
        lines = []

        links = []
        for uicr_trace_sources, sink in [
            (uicr_trace["ETBSINK"]["SOURCES"], "etb"),
            (uicr_trace["TPIUSINK"]["SOURCES"], "tpiu"),
            (uicr_trace["ETRSINK"]["SOURCES"], "etr"),
        ]:
            for field, source, processor in [
                ("STMMAINCORE", "stm", default_processor),
                ("ETMMAINCORE", "etm", default_processor),
                ("STMPPR", "stm", ProcessorID.PPR),
                ("STMFLPR", "stm", ProcessorID.FLPR),
                ("STMBBPR", "stm", ProcessorID.BBPR),
                ("STMHWEVENTS", "stm-hw-events", default_processor),
                # TODO: 92 fields
            ]:
                if uicr_trace_sources[field].content_enum == SvdEnum.REQUESTED:
                    links.append(f"{source}:{processor.name} -> {sink}")

        if uicr_trace["PORTCONFIG"].modified:
            port_speed = str(uicr_trace["PORTCONFIG"]["PORTCONFIG"].content)
            port_config = f"trace port speed: {port_speed}"
        else:
            port_config = ""

        if uicr_trace["ETRBUF"]["CONFIG0"].modified:
            addr_val = content_get_and_extend(
                uicr_trace["ETRBUF"]["CONFIG0"]["ADDRESS"]
            )
            size_val = content_get_and_extend(uicr_trace["ETRBUF"]["CONFIG1"]["SIZE"])
            etr_buffer = f"etr buffer: [0x{addr_val:08x} - 0x{addr_val + size_val:08x}) ({size_val})"
        else:
            etr_buffer = ""

        if links or port_config or etr_buffer:
            lines.append("Trace:")

            if links:
                lines.append(_indent("trace links", 1))
                for link in links:
                    lines.append(_indent(link, 2))

            if etr_buffer:
                lines.append(_indent(etr_buffer, 1))

            if port_config:
                lines.append(_indent(port_config, 1))

        return "\n".join(lines)


def _alloc_instanced_reg(array: svd.Array, address: int) -> tuple[int, svd.Struct]:
    for i, reg in enumerate(array):
        if (
            not reg["INSTANCE"].modified
            or content_get_and_extend(reg["INSTANCE"]["ADDRESS"]) == address
        ):
            return i, reg

    raise UicrError(f"Too many entries in {array.path} (max: {len(array)})")


def _resolve_secure(existing: svd.Field, new: bool) -> str:
    if not new or existing.content_enum == SvdEnum.NONSECURE:
        return SvdEnum.NONSECURE
    return SvdEnum.SECURE


def _indent(text: str, level: int = 0) -> str:
    return textwrap.indent(text, prefix="  " * level)


def _pretty_print_owned_common(reg_own: svd.Register, reg_sec: svd.Register) -> str:
    entries = []

    for i, (own, sec) in enumerate(zip(reg_own.values(), reg_sec.values())):
        owned = not own.content
        if not owned:
            continue

        secure = "S" if sec.content_enum == SvdEnum.SECURE else "NS"
        entries.append(f"{i}:{secure}")

    return ", ".join(entries)
