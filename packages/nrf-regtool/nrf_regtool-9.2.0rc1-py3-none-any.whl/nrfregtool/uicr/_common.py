# Copyright (c) 2025 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

import svd

from nrfregtool._svd_util import content_truncate_and_set


UnitSrc = str | list[str]
"""A generic specifier for a source location.
This can be given to some APIs to attach a context to a configuration.
The context can later be used to give better information and error messages.
"""


T = TypeVar("T")


@dataclass(frozen=True)
class Value(Generic[T]):
    """A value with an associated source context.

    These values can be passed to the UICR API to associate debug information
    with the configuration values.

    :var val: the value.
    :var src: arbitrary source context string(s).
    """

    val: T
    src: UnitSrc


class RegSrcMap:
    def __init__(self) -> None:
        self._sources = defaultdict(list)

    def reg_set(
        self,
        reg: svd.Register | svd.Field,
        val: str | int,
        src: UnitSrc | svd.Register | svd.Field | None,
        src_mode: Literal["append", "overwrite"] = "append",
        lsb_truncate: bool = False,
    ) -> None:
        if lsb_truncate:
            assert isinstance(reg, svd.Field)
            content_truncate_and_set(reg, val)
        else:
            reg.content = val

        match src:
            case svd.Register() | svd.Field():
                new_src = self._sources[reg_path_make(src)]
            case list():
                new_src = src
            case str():
                new_src = [src]
            case _:
                new_src = []

        if src_mode == "overwrite":
            self._sources[reg_path_make(reg)] = list(new_src)
        elif src_mode == "append":
            existing = self._sources[reg_path_make(reg)]
            for s in new_src:
                if s not in existing:
                    existing.append(s)
        else:
            raise ValueError(f"Invalid {src_mode=}")

    def reg_clear(self, reg: svd.Register | svd.Field) -> None:
        reg.content = reg.reset_content
        reg_path = reg_path_make(reg)
        for key, sources in self._sources.items():
            if key.startswith(reg_path):
                sources.clear()

    def reg_move(
        self,
        reg_to: svd.RegisterUnion | svd.Field,
        reg_from: svd.RegisterUnion | svd.Field,
    ) -> None:
        src = self._sources.pop(reg_path_make(reg_from), [])
        if src:
            self._sources[reg_path_make(reg_to)].extend(src)

        if isinstance(reg_from, svd.Field):
            reg_to.content = reg_from.content
            reg_from.content = reg_from.reset_content
            return
        for child in reg_from:
            self.reg_move(reg_to[child], reg_from[child])

    @property
    def src_dict(self) -> dict[str, list[str]]:
        return self._sources

    def src_lookup(self, reg: svd.RegisterUnion) -> list[str]:
        path = reg_path_make(reg)
        combined = []
        for key, sources in self._sources.items():
            if key.startswith(path):
                combined.extend(sources)
        return combined


def reg_path_make(reg: svd.RegisterUnion | svd.Field) -> str:
    match reg:
        case svd.Array() | svd.Struct() | svd.Register():
            return repr(reg.path)
        case svd.Field():
            return f"{reg._register.path!r}:{reg.name}"
        case _:
            raise ValueError(f"Unsupported reg: {reg}")
