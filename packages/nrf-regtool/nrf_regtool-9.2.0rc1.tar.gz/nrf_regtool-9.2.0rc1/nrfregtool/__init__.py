# Copyright (c) 2022 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import typing

from ._common import RegtoolLogger

_PACKAGE_NAME = "nrf-regtool"


def _get_version() -> str:
    import importlib.metadata

    return importlib.metadata.version(_PACKAGE_NAME)


__version__ = _get_version()


def _init_logger() -> RegtoolLogger:
    formatter = logging.Formatter("{message}", style="{")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Override the class returned by getLogger() below
    orig_class = logging.getLoggerClass()
    logging.setLoggerClass(RegtoolLogger)

    logger = typing.cast(RegtoolLogger, logging.getLogger("nrfregtool"))
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    # Reset custom logger class
    logging.setLoggerClass(orig_class)

    return logger


# logging.Logger instance used for log output from nrf-regtool
log = _init_logger()


# Public exports
__all__ = [
    "RegtoolLogger",
    "log",
    "__version__",
]
