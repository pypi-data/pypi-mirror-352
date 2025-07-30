# Copyright (c) 2025 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pickle
from collections import defaultdict
from enum import auto, Flag
from itertools import chain
from pathlib import Path
from typing import Optional, Sequence, TYPE_CHECKING

from intelhex import IntelHex

if TYPE_CHECKING:
    from devicetree import edtlib

from . import uicr
from .platform import CTRLSEL_DEFAULT, DomainID, ProcessorID


class MigrateFlag(Flag):
    DEFAULTS = auto()

    @classmethod
    def all(cls) -> MigrateFlag:
        return ~MigrateFlag(0)

    @classmethod
    def default(cls) -> MigrateFlag:
        return cls.all()


def uicr_migrate_hex_files_to_periphconf(
    uicr_hex_files: list[Path],
    edt_pickle_file: Optional[Path] = None,
    flags: MigrateFlag = MigrateFlag.default(),
) -> str:
    if edt_pickle_file is not None:
        with edt_pickle_file.open("rb") as file:
            dt = pickle.load(file)

        periph_annotation_lookup = _build_periph_annotation_dt(dt)
    else:
        periph_annotation_lookup = {}

    to_migrate = []

    for uicr_hex_file in uicr_hex_files:
        ihex = IntelHex()
        with uicr_hex_file.open("r", encoding="utf-8") as fp:
            ihex.loadhex(fp)

        uicr_bytes = bytearray(ihex.tobinstr())
        to_migrate.append(uicr.Uicr.from_bytes(uicr_bytes))

    return uicr_migrate(
        to_migrate,
        flags=flags,
        periph_annotation_lookup=periph_annotation_lookup,
    )


def _build_periph_annotation_dt(dt: edtlib.EDT) -> dict[int, str]:
    lut = {}

    for node in dt.nodes:
        if not node.regs:
            continue

        addr = node.regs[0].addr
        if node.labels:
            lut[addr] = node.labels[0]
        else:
            lut[addr] = node.path

    return lut


def uicr_migrate(
    to_migrate: Sequence[uicr.Uicr],
    flags: MigrateFlag = MigrateFlag.default(),
    periph_annotation_lookup: dict[int, str] = {},
) -> str:
    header_lines = ["#include <uicr/uicr.h>", ""]

    ipcmap_idx = 0

    # For grouping lines by type so that e.g. GPIO settings from two different UICRs are grouped
    # together (the group name is arbitrary).
    pconf_lines_by_type = defaultdict(list)

    for builder in to_migrate:
        uicr_svd = builder._uicr

        for reg in uicr_svd["IPCMAP"]:
            if not reg.modified:
                break

            source_domain = DomainID(reg["DOMAINIDSOURCE"].content)
            source_ch = reg["IPCTCHSOURCE"].content
            sink_domain = DomainID(reg["DOMAINIDSINK"].content)
            sink_ch = reg["IPCTCHSINK"].content

            pconf_lines_by_type["IPCMAP"].append(
                f"/* {source_domain.name} IPCT ch. {source_ch} => "
                f"{sink_domain.name} IPCT ch. {sink_ch} */"
            )
            pconf_lines_by_type["IPCMAP"].append(
                (
                    "UICR_IPCMAP_CHANNEL_CFG("
                    f"{ipcmap_idx}, "
                    f"{source_domain.c_enum}, {source_ch}, "
                    f"{sink_domain.c_enum}, {sink_ch});"
                )
            )
            ipcmap_idx += 1

        for reg in uicr_svd["DPPI"]:
            if not reg["INSTANCE"].modified:
                break

            address = reg["INSTANCE"].content
            dppic_name = _DPPIC_ADDR_TO_NAME[address]
            if dppic_name == "DPPIC130":
                continue

            reg_link = reg["CH"]["LINK"]
            for ch, (enabled, direction) in enumerate(
                zip(reg_link["EN"].values(), reg_link["DIR"].values())
            ):
                if enabled.content_enum != "Enabled":
                    continue

                local_ppib_name, local_ppib_ch_map = _DPPIC_TO_PPIB[dppic_name]
                local_ppib_ch = local_ppib_ch_map[ch]

                remote_ppib_name, remote_ppib_ch_map = _PPIB_TO_PPIB[local_ppib_name]
                remote_ppib_ch = remote_ppib_ch_map[local_ppib_ch]

                if direction.content_enum == "Source":
                    sub_name, sub_ch = local_ppib_name, local_ppib_ch
                    pub_name, pub_ch = remote_ppib_name, remote_ppib_ch
                else:
                    sub_name, sub_ch = remote_ppib_name, remote_ppib_ch
                    pub_name, pub_ch = local_ppib_name, local_ppib_ch

                sub_addr = _PPIB_NAME_TO_ADDR[sub_name]
                sub_final_name = periph_annotation_lookup.get(sub_addr, sub_name)
                pub_addr = _PPIB_NAME_TO_ADDR[pub_name]
                pub_final_name = periph_annotation_lookup.get(pub_addr, pub_name)

                pconf_lines_by_type["DPPI"].append(
                    f"/* {sub_final_name} ch. {sub_ch} => {pub_final_name} ch. {pub_ch} */"
                )
                pconf_lines_by_type["DPPI"].append(
                    f"UICR_PPIB_SUBSCRIBE_SEND_ENABLE({_c_hex_addr(sub_addr)}, {sub_ch});"
                )
                pconf_lines_by_type["DPPI"].append(
                    f"UICR_PPIB_PUBLISH_RECEIVE_ENABLE({_c_hex_addr(pub_addr)}, {pub_ch});"
                )

        for i, reg in enumerate(uicr_svd["GPIO"]):
            if not reg["INSTANCE"].modified:
                break

            address = reg["INSTANCE"].content
            gpio_name = periph_annotation_lookup.get(address, _c_hex_addr(address))

            for pin, own in enumerate(reg["OWN"].values()):
                if own.content_enum != "Own":
                    continue

                ctrlsel = uicr_svd["GPIO_PIN"][i]["CTRLSEL"][pin]
                if not ctrlsel.modified:
                    continue

                ctrlsel_val = ctrlsel.content

                if MigrateFlag.DEFAULTS not in flags and ctrlsel_val == CTRLSEL_DEFAULT:
                    continue

                pconf_lines_by_type["GPIO"].append(
                    f"/* {gpio_name} pin {pin}: CTRLSEL = {ctrlsel_val}*/"
                )
                pconf_lines_by_type["GPIO"].append(
                    f"UICR_GPIO_PIN_CNF_CTRLSEL_SET({_c_hex_addr(address)}, "
                    f"{pin}, {ctrlsel.content});"
                )

        for reg in uicr_svd["PERIPH"]:
            reg_cfg = reg["CONFIG"]
            if not reg_cfg.modified:
                break

            address = reg_cfg["ADDRESS"].content << reg_cfg["ADDRESS"].bit_offset
            irq_processor = ProcessorID(reg_cfg["PROCESSOR"].content)
            periph_name = periph_annotation_lookup.get(address, _c_hex_addr(address))

            if (
                MigrateFlag.DEFAULTS not in flags
                and irq_processor == ProcessorID.APPLICATION
            ):
                continue

            pconf_lines_by_type["IRQMAP"].append(
                f"/* {periph_name} IRQ => {irq_processor.name} */"
            )
            pconf_lines_by_type["IRQMAP"].append(
                f"UICR_IRQMAP_IRQ_SINK_SET(NRFX_IRQ_NUMBER_GET({_c_hex_addr(address)}), "
                f"{irq_processor.c_enum});"
            )

    full_lines = header_lines + list(chain.from_iterable(pconf_lines_by_type.values()))

    return "\n".join(full_lines)


def _c_hex_addr(address: int) -> str:
    return f"0x{address:08x}UL"


_DPPIC_ADDR_TO_NAME = {
    0x5F8E_1000: "DPPIC120",
    0x5F92_2000: "DPPIC130",
    0x5F98_1000: "DPPIC131",
    0x5F99_1000: "DPPIC132",
    0x5F9A_1000: "DPPIC133",
    0x5F9B_1000: "DPPIC134",
    0x5F9C_1000: "DPPIC135",
    0x5F9D_1000: "DPPIC136",
}

_PPIB_NAME_TO_ADDR = {
    "PPIB121": 0x5F8E_F000,
    "PPIB130": 0x5F92_5000,
    "PPIB131": 0x5F92_6000,
    "PPIB132": 0x5F98_D000,
    "PPIB133": 0x5F99_D000,
    "PPIB134": 0x5F9A_D000,
    "PPIB135": 0x5F9B_D000,
    "PPIB136": 0x5F9C_D000,
    "PPIB137": 0x5F9D_D000,
}

_DPPIC_TO_PPIB = {
    "DPPIC120": ("PPIB121", range(0, 8)),
    "DPPIC131": ("PPIB132", range(0, 8)),
    "DPPIC132": ("PPIB133", range(0, 8)),
    "DPPIC133": ("PPIB134", range(0, 8)),
    "DPPIC134": ("PPIB135", range(0, 8)),
    "DPPIC135": ("PPIB136", range(0, 8)),
    "DPPIC136": ("PPIB137", range(0, 8)),
}

_PPIB_TO_PPIB = {
    "PPIB132": ("PPIB130", range(0, 8)),
    "PPIB133": ("PPIB130", range(8, 16)),
    "PPIB134": ("PPIB130", range(16, 24)),
    "PPIB135": ("PPIB130", range(24, 32)),
    "PPIB136": ("PPIB131", range(0, 8)),
    "PPIB137": ("PPIB131", range(8, 16)),
    "PPIB121": ("PPIB131", range(16, 24)),
}
