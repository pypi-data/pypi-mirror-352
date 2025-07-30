# Copyright (c) 2023 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import sys
from importlib.util import find_spec
from pathlib import Path
from textwrap import dedent
from typing import Any, Optional

import nrfregtool
from nrfregtool import RegtoolLogger, log
from nrfregtool.platform import Product
from nrfregtool.uicr_migrate import MigrateFlag, uicr_migrate_hex_files_to_periphconf


class CliError(RuntimeError):
    """An error caused by improper usage of the CLI."""

    ...


def cli(prog: Optional[str] = None, args_override: Optional[list[str]] = None) -> None:
    """Top level CLI entrypoint"""
    parser = make_arg_parser(prog)
    args = parser.parse_args(args_override)

    log_level = {
        0: RegtoolLogger.WARNING,
        1: RegtoolLogger.INFO,
        2: RegtoolLogger.DEBUG,
        3: RegtoolLogger.TRACE,
    }.get(args.verbose, RegtoolLogger.TRACE)
    log.setLevel(log_level)

    if not hasattr(args, "_command"):
        parser.print_help()
        sys.exit(2)

    kwargs = dict(vars(args))
    try:
        if args._command == "uicr-compile":
            cmd_uicr_compile(**kwargs)
        elif args._command == "uicr-migrate":
            cmd_uicr_migrate(**kwargs)
        else:
            raise NotImplementedError(f"Unhandled command {args._command}")
    except CliError as e:
        log.error(str(e))
        sys.exit(2)
    except Exception as e:
        log.exception(e)
        sys.exit(2)

    sys.exit(0)


def make_arg_parser(prog: Optional[str] = None) -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(
        prog=prog,
        description=dedent(
            """\
            CLI for generating UICR blobs for Haltium products.

            User Information Configuration Registers (UICR), in the context of certain
            Nordic SoCs, are used by Secure Domain Firmware (SDFW) to configure system
            resources, like memory and peripherals. When used in singular, a UICR refers
            to a complete set of registers for one domain.

            Use the -h or --help option with each command to see more information about
            them and their individual options/arguments.
            """
        ),
        allow_abbrev=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    top.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        help="Print verbose output such as debug information.",
    )
    top.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s, version {nrfregtool.__version__}",
        help="Print program version",
    )

    sub = top.add_subparsers(title="subcommands")
    comp = sub.add_parser(
        "uicr-compile",
        help="Compile UICR from a devicetree",
        description=dedent(
            """\
            This command compiles a UICR binary blob from devicetree input, which should
            indicate the system resource configuration required for a single domain.

            For example, on nRF54H20:

                PYTHONPATH=zephyr/scripts/dts/python-devicetree/src \\
                nrf-regtool uicr-compile \\
                -e _build/zephyr/edt.pickle \\
                -o uicr.hex \\
                -P NRF54H20

            This command is intended for use as part of the Zephyr RTOS application
            development workflow. nrf-regtool depends on edtlib, a devicetree parsing
            library provided by the Zephyr Project, and the input file would usually be
            the edt.pickle artifact from a Zephyr build system. Using the pickle input
            requires a matching revision of edtlib from the Zephyr repository.
            """
        ),
        allow_abbrev=False,
        exit_on_error=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    comp.set_defaults(_command="uicr-compile")
    comp_in = comp.add_argument_group("Input file")
    comp_in.add_argument(
        "-e",
        "--edt-pickle-file",
        type=Path,
        required=True,
        help=(
            "Pickled edtlib.EDT object with parsed devicetree contents,\n"
            "containing information that is relevant for a domain's UICR. "
        ),
    )
    comp_in_opt = comp.add_argument_group("Input options")
    comp_in_opt.add_argument(
        "-P",
        "--product-name",
        required=True,
        help=(
            "Name of the Nordic SoC or SiP for which to compile the UICR.\n"
            f"Supported values are: {', '.join(x.name for x in Product)}.\n\n"
        ),
    )
    comp_out = comp.add_argument_group("Output files")
    comp_out.add_argument(
        "-o",
        "--output-file",
        required=True,
        type=Path,
        help="Generated output file of the encoded UICR in intel hex format.",
    )
    comp_out.add_argument(
        "--output-debug-file",
        type=Path,
        help="Debug information output in JSON format.",
    )

    migrate = sub.add_parser(
        "uicr-migrate",
        help=(
            "Migrate a UICR HEX file to a format compatible with IRONside SE\n"
            f"(only supported for {Product.NRF54H20.name})"
        ),
        allow_abbrev=False,
        exit_on_error=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    migrate.set_defaults(_command="uicr-migrate")
    migrate_in = migrate.add_argument_group("Inputs")
    migrate_in.add_argument(
        "-i",
        "--uicr-hex-file",
        dest="uicr_hex_files",
        type=Path,
        action="append",
        required=True,
        help="Compiled UICR HEX file to be migrated.",
    )
    migrate_in.add_argument(
        "-e",
        "--edt-pickle-file",
        type=Path,
        default=None,
        help=(
            "Pickled edtlib.EDT object with parsed devicetree contents,\n"
            "containing information that is relevant for a domain's UICR.\n"
            "If provided, devicetree macros are used in the generated source file."
        ),
    )
    migrate_out = migrate.add_argument_group("Output files")
    migrate_out.add_argument(
        "-o",
        "--output-periphconf-file",
        type=Path,
        required=True,
        help="Path to write the generated PERIPHCONF source file to.",
    )
    migrate_opt = migrate.add_argument_group("Options")
    migrate_opt.add_argument(
        "--no-defaults",
        default=False,
        action="store_true",
        help="Omit peripheral configurations that set registers to their default value.",
    )

    return top


def cmd_uicr_compile(
    edt_pickle_file: Path,
    product_name: str,
    output_file: Path,
    output_debug_file: Optional[Path] = None,
    **kwargs: Any,
):
    if find_spec("devicetree") is None:
        raise CliError(
            "Devicetree support is not available outside the zephyr build system"
        )
    try:
        product = Product(product_name)
    except ValueError:
        raise CliError(
            f"Unknown product name {product_name}; must be one of {[x.name for x in Product]}"
        )

    from nrfregtool.zephyr.uicr_compile import uicr_from_devicetree

    uicr_from_devicetree(edt_pickle_file, product, output_file, output_debug_file)


def cmd_uicr_migrate(
    uicr_hex_files: list[Path],
    edt_pickle_file: Optional[Path],
    output_periphconf_file: Path,
    no_defaults: bool,
    **kwargs: Any,
):
    if edt_pickle_file is not None and find_spec("devicetree") is None:
        raise CliError(
            "Devicetree support is not available outside the zephyr build system"
        )

    flags = MigrateFlag.default()
    if no_defaults:
        flags = flags & ~MigrateFlag.DEFAULTS

    periphconf = uicr_migrate_hex_files_to_periphconf(
        uicr_hex_files, edt_pickle_file, flags=flags
    )

    with output_periphconf_file.open("w", encoding="utf-8") as fp:
        fp.write(periphconf)
