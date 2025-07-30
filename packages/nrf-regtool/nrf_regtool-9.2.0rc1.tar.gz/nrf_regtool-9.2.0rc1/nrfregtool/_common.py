# Copyright (c) 2022 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import inspect
import logging
from itertools import pairwise
from typing import Iterable


def memory_to_bytes(memory_iter: Iterable[tuple[int, int]], padding: int) -> bytearray:
    out = bytearray()

    for (addr_a, value_a), (addr_b, value_b) in pairwise(memory_iter):
        if not out:
            out.append(value_a)

        num_empty = addr_b - addr_a - 1
        if num_empty > 0:
            out.extend([padding] * num_empty)

        out.append(value_b)

    return out


def ranges_overlap_inclusive(
    a_start: int, a_end: int, b_start: int, b_end: int
) -> bool:
    return a_end >= b_start and b_end >= a_start


class RegtoolLogger(logging.Logger):
    NOTSET = logging.NOTSET
    TRACE = 5
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def trace_function(self) -> None:
        self.log(RegtoolLogger.TRACE, "%s", _get_func_call_formatter(1))


def _get_func_call_formatter(stack_offset: int = 0) -> _FunctionCallFormatter:
    frame_info = inspect.stack()[stack_offset + 1]
    return _FunctionCallFormatter(frame_info)


class _FunctionCallFormatter:
    def __init__(self, frame_info: inspect.FrameInfo) -> None:
        self._frame_info = frame_info

    def __call__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        args = inspect.getargvalues(self._frame_info.frame)
        arg_strings = [f"{k}={v}" for k, v in args.locals.items() if k in args.args]
        return f"{self._frame_info.function}({', '.join(arg_strings)})"
