# Copyright (c) 2022 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from nrfregtool import _PACKAGE_NAME
from nrfregtool._cli import cli


def package_main(prog: Optional[str] = None):
    """
    Main entry point for the tool when installed as a package.
    """
    cli(prog=prog)


if __name__ == "__main__":
    package_main(prog=_PACKAGE_NAME)
