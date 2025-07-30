# Copyright (c) 2024 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import inspect
import pickle
import re
from dataclasses import dataclass
from functools import wraps
from itertools import islice
from pathlib import Path
from typing import (
    Any,
    Callable,
    Optional,
    Iterable,
    Iterator,
    Type,
    TypeVar,
    Sequence,
    overload,
)

from intelhex import IntelHex

from devicetree import edtlib

from nrfregtool import log, uicr
from nrfregtool.platform import (
    CTRLSEL_DEFAULT,
    AddressRegion,
    Ctrlsel,
    ProcessorID,
    Product,
    DomainID,
    OwnerID,
    secure_address_get,
)

NON_PROG_OWNER_COMPATS = [
    "nordic,nrf-gpio",
    "nordic,nrf-gpiote",
    "nordic,nrf-grtc",
    "nordic,nrf-dppic-global",
    "nordic,nrf-ipct-global",
    "nordic,nrf-clic",
    "nordic,nrf-bellboard",
    "nordic,nrf-vevif-task-tx",
    # Note: this has programmable ownership, but this aligns with current usage of the peripheral
    # where the secure domain configures it.
    "nordic,nrf-tddconf",
]
NON_PROG_OWNER_COMPAT_PATTERN = (
    "^" + "|".join((f"({c})" for c in NON_PROG_OWNER_COMPATS)) + "$"
)
# Every compatible starting with "nordic," that is not a non-programmable ownership compatible
PROG_OWNER_COMPAT_PATTERN = rf"(?!{NON_PROG_OWNER_COMPAT_PATTERN})^nordic,.+$"
# Status values that indicate ownership either by the processor or a child processor
STATUS_OWNED = ("okay", "reserved")


class BadDevicetreeError(RuntimeError):
    """Error raised when the devicetree is misconfigured
    or if assumptions about the devicetree are not met.
    """

    ...


C = TypeVar("C")
VisitMethod = Callable[[C, edtlib.Node], None]
BoundVisitMethod = Callable[[edtlib.Node], None]


@dataclass
class DtMatch:
    """Decorator used to annotate DT node visitor methods with a devicetree node pattern.

    A node match occurs when all of the parameters in the pattern match the node.

    :param compat: node compatible string or regex, matched against every member in node.compats.
    :param path: node path string or regex, matched against node.path.
    :param label: node label string or regex, matched against every member in node.labels.
    :param status: one or more node status strings, matched against node.status.
    :param props: list of property name string or regex, matched against node.props.keys().
    """

    compat: str | re.Pattern | None = None
    path: str | re.Pattern | None = None
    label: str | re.Pattern | None = None
    status: str | Sequence[str] | None = None
    regs: Callable[[int], bool] | None = None
    props: Sequence[str | re.Pattern] | None = None

    def __call__(self, method: VisitMethod) -> VisitMethod:
        @wraps(method)
        def visit_method_wrapper(c: C, node: edtlib.Node, /) -> None:
            match self.path:
                case str(path):
                    if node.path != path:
                        return
                case re.Pattern() as pattern:
                    if not re.search(pattern, node.path):
                        return

            match self.compat:
                case str(compat):
                    if not any((c == compat for c in node.compats)):
                        return
                case re.Pattern() as pattern:
                    if not any((re.search(pattern, c) for c in node.compats)):
                        return

            match self.label:
                case str(label):
                    if not any((l == label for l in node.labels)):
                        return
                case re.Pattern() as pattern:
                    if not any((re.search(pattern, l) for l in node.labels)):
                        return

            match self.status:
                case str(status):
                    if node.status != status:
                        return
                case list() | tuple() as statuses:
                    if node.status not in statuses:
                        return

            if isinstance(self.regs, Callable):
                if not node.regs or not self.regs(node.regs[0].addr):
                    return

            if self.props:
                any_found = False

                for expected in self.props:
                    match expected:
                        case str(prop):
                            any_found = prop in node.props

                        case re.Pattern() as pattern:
                            any_found = any((re.search(pattern, p) for p in node.props))

                    if any_found:
                        break

                if not any_found:
                    return

            method(c, node)

        return visit_method_wrapper


DtLocation = (
    edtlib.Node
    | edtlib.Property
    | tuple[edtlib.Property, int]
    | list[edtlib.Node | edtlib.Property | tuple[edtlib.Property, int]]
)
"""Specifer for a location in the devicetree."""


def uicr_from_devicetree(
    edt_pickle_file: Path,
    product: Product,
    output_file: Path,
    output_debug_file: Optional[Path] = None,
) -> None:
    """Populate a UICR based on a devicetree."""
    with edt_pickle_file.open("rb") as file:
        dt = pickle.load(file)

    processor = dt_processor_id(dt)
    uicr_builder = uicr.Uicr()

    visitor = UicrMatcher(builder=uicr_builder, product=product, processor=processor)
    visit_methods: list[BoundVisitMethod] = [
        method
        for name, method in inspect.getmembers(visitor, inspect.ismethod)
        if not name.startswith("_")
    ]
    for node in dt.nodes:
        for visit in visit_methods:
            visit(node)

    log.info(uicr_builder.pretty_print(verbose=log.getEffectiveLevel() < log.INFO))

    uicr_hex = IntelHex()
    uicr_hex.frombytes(uicr_builder.build_bytes(), offset=visitor.uicr_address)

    with output_file.open("w", encoding="utf-8") as file:
        uicr_hex.write_hex_file(file)
    if output_debug_file:
        with output_debug_file.open("w", encoding="utf-8") as file:
            file.write(uicr_builder.build_debug_info())


def address_is_global_periph(address: int) -> bool:
    try:
        domain = DomainID.from_address(address)
    except ValueError:
        return False

    if domain != DomainID.GLOBAL:
        return False

    if AddressRegion.from_address(address) not in (
        AddressRegion.PERIPHERAL,
        AddressRegion.STM,
    ):
        return False

    return True


class UicrMatcher:
    def __init__(
        self, builder: uicr.Uicr, product: Product, processor: ProcessorID
    ) -> None:
        self.uicr_address = 0
        self._processor = processor
        self._product = product
        self._builder = builder
        try:
            self._owner = OwnerID.from_processor(self._processor)
        except Exception:
            raise RuntimeError(
                f"Processor ID {self._processor} does not correspond to an owner"
            )
        try:
            self._domain = DomainID.from_processor(self._processor)
        except Exception:
            raise RuntimeError(
                f"Processor ID {self._processor} does not correspond to a domain"
            )

        header = uicr.Header(
            part_code=self._product.product_code.part_number,
            hardware_revision=self._product.product_code.revision,
            domain=self._domain.value,
        )
        self._builder.set_header(header)

    @DtMatch(path="/chosen")
    def visit_chosen(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        if prop := node._node.props.get("zephyr,code-partition"):
            code_partition = node.edt.get_node(prop.to_path().path)
            vtor_address = dt_partition_address_get(code_partition)
            secure = dt_mem_node_is_secure(code_partition)
            if secure.val:
                self._builder.set_secure_vtor(vtor_address)
            else:
                self._builder.set_nonsecure_vtor(vtor_address)

    @DtMatch(compat="nordic,owned-partitions", status=STATUS_OWNED)
    def visit_owned_partitions(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        if not node.children:
            return

        partitions = list(node.children.values())
        abs_addresses = [dt_partition_address_get(p) for p in partitions]
        end_addresses = [
            uicr.Value(a.val + p.regs[0].size, a.src)
            for a, p in zip(abs_addresses, partitions)
        ]
        min_addr = min(abs_addresses, key=lambda a: a.val)
        max_addr = max(end_addresses, key=lambda a: a.val)
        size = uicr.Value(max_addr.val - min_addr.val, src=max_addr.src)
        access = self._parse_access_props(node)

        memory = uicr.Memory(address=min_addr, size=size, access=access)
        self._builder.add_memory(memory)

    @DtMatch(compat="nordic,owned-memory", status=STATUS_OWNED)
    def visit_owned_memory(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        addr = dt_reg_addr(node)
        size = dt_reg_size(node)
        access = self._parse_access_props(node)

        memory = uicr.Memory(address=addr, size=size, access=access)
        self._builder.add_memory(memory)

    def _parse_access_props(self, node: edtlib.Node) -> list[uicr.Memory.Access]:
        accesses = []
        props = node.props

        if "nordic,access" not in props:
            # TODO: drop deprecated props with zephyr 4.2.0
            owner = dt_prop(node, "owner-id", default=self._owner.value)
            readable = dt_prop(node, "perm-read")
            writable = dt_prop(node, "perm-write")
            executable = dt_prop(node, "perm-execute")
            secure = dt_prop(node, "perm-secure")
            non_secure_callable = dt_prop(node, "non-secure-callable")

            access = uicr.Memory.Access(
                owner=owner,
                read=readable,
                write=writable,
                execute=executable,
                secure=secure,
                non_secure_callable=non_secure_callable,
            )
            accesses.append(access)
        else:
            if len(props["nordic,access"].val) % 2 != 0:
                raise BadDevicetreeError(
                    f"nordic,access property in {node.path} "
                    "does not contain an even number of values"
                )

            nordic_access = dt_array_prop(node, "nordic,access")
            for owner, permission in batched(nordic_access, 2):
                access_perm = NordicAccessPerm(permission.val)
                access = uicr.Memory.Access(
                    owner=owner,
                    read=uicr.Value(
                        NordicAccessPerm.NRF_PERM_R in access_perm, permission.src
                    ),
                    write=uicr.Value(
                        NordicAccessPerm.NRF_PERM_W in access_perm, permission.src
                    ),
                    execute=uicr.Value(
                        NordicAccessPerm.NRF_PERM_X in access_perm, permission.src
                    ),
                    secure=uicr.Value(
                        NordicAccessPerm.NRF_PERM_S in access_perm, permission.src
                    ),
                    non_secure_callable=uicr.Value(
                        NordicAccessPerm.NRF_PERM_NSC in access_perm, permission.src
                    ),
                )
                accesses.append(access)

        return accesses

    @DtMatch(
        compat="nordic,nrf-gpiote",
        status=STATUS_OWNED,
        regs=address_is_global_periph,
    )
    def visit_nrf_gpiote(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        addr = dt_reg_addr(node)
        channels = dt_channels_get(node)

        for num, secure in channels:
            self._builder.add_gpiote_channel(addr, uicr.Feature(num=num, secure=secure))

    @DtMatch(
        compat="nordic,nrf-dppic-global",
        status=STATUS_OWNED,
        regs=address_is_global_periph,
    )
    def visit_nrf_dppic(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        addr = dt_reg_addr(node)
        channels = dt_channels_get(node)
        channel_groups = dt_channels_get(
            node,
            owned_name="owned-channel-groups",
            nonsecure_name="nonsecure-channel-groups",
        )

        source_channels = dt_array_prop(node, "source-channels", [])
        sink_channels = dt_array_prop(node, "sink-channels", [])

        for num, secure in channels:
            self._builder.add_dppi_channel(addr, uicr.Feature(num=num, secure=secure))

        for num, secure in channel_groups:
            self._builder.add_dppi_channel_group(
                addr, uicr.Feature(num=num, secure=secure)
            )

        # NCSDK-33140: The DPPI driver needs to have the same channel number in source-channels and
        # sink-channels on the dppic130 node, which leads to a conflict when trying to configure
        # both below. The link settings on dppic130 are ignored by SDFW in runtime, therefore we
        # simply skip generating them here to allow the driver to use both properties.
        if "dppic130" in node.labels:
            return

        for num in source_channels:
            self._builder.add_dppi_link(
                addr,
                uicr.DppiLink(
                    num, uicr.Value(uicr.DppiLink.Direction.SOURCE, src=num.src)
                ),
            )

        for num in sink_channels:
            self._builder.add_dppi_link(
                addr,
                uicr.DppiLink(
                    num, uicr.Value(uicr.DppiLink.Direction.SINK, src=num.src)
                ),
            )

    @DtMatch(
        compat="nordic,nrf-ipct-global",
        status=STATUS_OWNED,
        regs=address_is_global_periph,
    )
    def visit_nrf_ipct_global(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        addr = dt_reg_addr(node)
        channels = dt_channels_get(node)

        for num, secure in channels:
            self._builder.add_ipct_channel(addr, uicr.Feature(num=num, secure=secure))

    @DtMatch(
        compat=re.compile("^nordic,nrf-ipct-((local)|(global))$"),
        status=STATUS_OWNED,
        props=["source-channel-links", "sink-channel-links"],
    )
    def visit_nrf_ipct(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        source_channel_links = dt_array_prop(node, "source-channel-links", [])
        if len(source_channel_links) % 3 != 0:
            raise BadDevicetreeError()
        sink_channel_links = dt_array_prop(node, "sink-channel-links", [])

        domain = dt_prop(node, "global-domain-id", None)
        if domain.val is None:
            addr = dt_reg_addr(node)
            domain_id = DomainID.from_address(addr.val)
            if domain_id is None:
                raise BadDevicetreeError(
                    f"Failed to determine domain ID for address 0x{addr.val:08x} "
                    f"specified on node {node.path}"
                )
            domain = uicr.Value(domain_id.value, src=addr.src)

        for source_ch, sink_domain, sink_ch in batched(source_channel_links, 3):
            link = uicr.IpcLink(
                source_domain=domain,
                source_channel_num=source_ch,
                sink_domain=sink_domain,
                sink_channel_num=sink_ch,
            )
            self._builder.add_ipc_link(link)

        for sink_ch, source_domain, source_ch in batched(sink_channel_links, 3):
            link = uicr.IpcLink(
                source_domain=source_domain,
                source_channel_num=source_ch,
                sink_domain=domain,
                sink_channel_num=sink_ch,
            )
            self._builder.add_ipc_link(link)

    @DtMatch(compat="zephyr,ipc-icmsg", status=STATUS_OWNED)
    def visit_ipc_icmsg(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        tx_idx = node.props["mbox-names"].val.index("tx")
        tx_mbox = node.props["mboxes"].val[tx_idx]

        tx_processor = dt_node_processor_id(tx_mbox.controller, interrupts_only=False)
        if (
            tx_processor.val != ProcessorID.SECURE
            or self._processor == ProcessorID.SYSCTRL
        ):
            # We only care about secure domain IPC
            return

        tx_region = node.props["tx-region"].val
        tx_addr = dt_reg_addr(tx_region)
        tx_size = dt_reg_size(tx_region)

        rx_region = node.props["rx-region"].val
        rx_addr = dt_reg_addr(rx_region)
        rx_size = dt_reg_size(rx_region)

        mailbox = uicr.Mailbox(
            tx_address=tx_addr, tx_size=tx_size, rx_address=rx_addr, rx_size=rx_size
        )
        self._builder.set_secure_mailbox(mailbox)

    @DtMatch(
        compat=re.compile(PROG_OWNER_COMPAT_PATTERN),
        status=STATUS_OWNED,
        regs=address_is_global_periph,
    )
    def visit_nordic_split_ownership_peripheral(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        addr = dt_reg_addr(node)
        processor = dt_node_processor_id(node, default=self._processor.value)
        secure = dt_node_is_secure(node)

        peripheral = uicr.Peripheral(
            address=addr, irq_processor=processor, secure=secure, dma_secure=secure
        )
        self._builder.add_peripheral(peripheral)

    @DtMatch(
        compat="nordic,nrf-grtc",
        status=STATUS_OWNED,
        regs=address_is_global_periph,
    )
    def visit_nrf_grtc(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        channels = dt_channels_get(node)
        for num, secure in channels:
            self._builder.add_grtc_channel(uicr.Feature(num=num, secure=secure))

    @DtMatch(status=STATUS_OWNED, props=[re.compile(r"^(.+-)?gpios$")])
    def visit_peripheral_with_gpios(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        # TODO: this could be solved better with e.g. a property matcher
        for name in node.props:
            if not re.fullmatch(r"^(.+-)?gpios$", name):
                continue

            if node.props[name].type != "phandle-array":
                log.debug(
                    f"skipping *-gpios prop {name} in {node.path} (not a phandle-array)"
                )
                continue

            for entry in dt_array_prop(node, name):
                gpio_node = entry.val.controller
                if "nordic,nrf-gpio" not in gpio_node.compats:
                    continue

                port = gpio_node.props["port"].val
                num = uicr.Value(entry.val.data["pin"], src=entry.src)
                secure = dt_node_is_secure(gpio_node)
                ctrlsel = dt_lookup_ctrlsel(
                    self._product, node.props[name], (port, num.val)
                )
                gpio_addr = dt_reg_addr(entry.val.controller)
                pin = uicr.Pin(num=num, secure=secure, ctrlsel=ctrlsel)
                self._builder.add_gpio_pin(gpio_addr, pin)

    @DtMatch(status=STATUS_OWNED, props=["pinctrl-0"])
    def visit_peripheral_with_pinctrls(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        secure = dt_node_is_secure(node)
        for pinctrl in node.pinctrls:
            for config_node in pinctrl.conf_nodes:
                for group_node in config_node.children.values():
                    for i, psel_val in enumerate(dt_array_prop(group_node, "psels")):
                        psel = NrfPsel.from_raw(psel_val.val)
                        if psel.is_disconnected():
                            # Pin is unused and should be ignored
                            continue
                        gpio_node = find_gpio_node_by_port(
                            node.edt,
                            psel.port,
                            err_suffix=f" (referenced by {group_node.path}:psels[{i}])",
                        )
                        num = uicr.Value(psel.pin, src=psel_val.src)
                        ctrlsel = dt_lookup_ctrlsel(self._product, pinctrl, psel)
                        gpio_addr = dt_reg_addr(gpio_node)
                        pin = uicr.Pin(num=num, secure=secure, ctrlsel=ctrlsel)
                        self._builder.add_gpio_pin(gpio_addr, pin)

    @DtMatch(compat="nordic,nrf-saadc", status=STATUS_OWNED)
    def visit_nrf_saadc(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        secure = dt_node_is_secure(node)
        for name, child in node.children.items():
            if not name.startswith("channel"):
                continue
            for port, num in dt_lookup_adc_channel_pins(child):
                gpio_node = find_gpio_node_by_port(node.edt, port.val)
                gpio_addr = dt_reg_addr(gpio_node)
                pin = uicr.Pin(num, secure)
                self._builder.add_gpio_pin(gpio_addr, pin)

    @DtMatch(compat=re.compile(r"^nordic,nrf-(lp)?comp$"), status=STATUS_OWNED)
    def visit_nrf_comp_lpcomp(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        secure = dt_node_is_secure(node)
        for port, num in dt_lookup_comp_lpcomp_pins(node):
            gpio_node = find_gpio_node_by_port(node.edt, port.val)
            gpio_addr = dt_reg_addr(gpio_node)
            pin = uicr.Pin(num, secure)
            self._builder.add_gpio_pin(gpio_addr, pin)

    @DtMatch(compat="nordic,nrf-tddconf", status=STATUS_OWNED)
    def visit_nrf_tddconf(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        self_processor = self._processor.value

        for sources_name, sink_enum in [
            ("etbsources", uicr.Trace.Sink.ETB),
            ("tpiusources", uicr.Trace.Sink.TPIU),
            ("etrsources", uicr.Trace.Sink.ETR),
        ]:
            if sources_name not in node.props:
                continue

            sources_val = dt_prop(node, sources_name)
            tdd_sources = NordicTddSource(sources_val.val)
            for sources_bit, processor, source_enum in [
                (
                    NordicTddSource.SOURCE_STMMAINCORE,
                    self_processor,
                    uicr.Trace.Source.STM,
                ),
                (
                    NordicTddSource.SOURCE_ETMMAINCORE,
                    self_processor,
                    uicr.Trace.Source.ETM,
                ),
                (
                    NordicTddSource.SOURCE_STMPPR,
                    ProcessorID.PPR.value,
                    uicr.Trace.Source.STM,
                ),
                (
                    NordicTddSource.SOURCE_STMFLPR,
                    ProcessorID.FLPR.value,
                    uicr.Trace.Source.STM,
                ),
                (
                    NordicTddSource.SOURCE_STMHWEVENTS,
                    self_processor,
                    uicr.Trace.Source.STM_HW_EVENTS,
                ),
            ]:
                if sources_bit in tdd_sources:
                    trace = uicr.Trace(
                        processor=processor,
                        source=uicr.Value(source_enum, src=sources_val.src),
                        sink=uicr.Value(sink_enum, sources_val.src),
                    )
                    self._builder.add_trace_link(trace)

        if "portconfig" in node.props:
            speed = dt_prop(node, "portconfig")
            self._builder.set_trace_port_config(uicr.TracePortConfig(speed=speed))

        if "etrbuffer" in node.props:
            buffer_node = node.props["etrbuffer"].val
            address = dt_reg_addr(buffer_node)
            size = dt_reg_size(buffer_node)
            self._builder.set_etr_buffer(uicr.EtrBuffer(address=address, size=size))

    @DtMatch(compat="nordic,nrf-uicr-v2", status=STATUS_OWNED)
    def visit_nrf_uicr_v2(self, node: edtlib.Node, /) -> None:
        log.trace_function()

        node_domain = DomainID(node.props["domain"].val)
        if node_domain == self._domain:
            self.uicr_address = dt_reg_addr(node).val


def find_gpio_node_by_port(
    dt: edtlib.EDT, port: int, err_suffix: str = ""
) -> edtlib.Node:
    for gpio_node in dt.compat2nodes["nordic,nrf-gpio"]:
        if gpio_node.props["port"].val == port:
            return gpio_node
    raise BadDevicetreeError(
        f"Failed to find Nordic GPIO node with port {port}{err_suffix}"
    )


# Equivalent to itertools.batched(), using the recipe provided in the docs.
def batched(iterable: Iterable, n: int, *, strict: bool = False) -> Iterator:
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


@overload
def dt_to_unit_src(dt_src: None, /) -> None: ...


@overload
def dt_to_unit_src(dt_src: DtLocation, /) -> uicr.UnitSrc: ...


def dt_to_unit_src(dt_src, /):
    """Create a unique string identifier for a devicetree location.

    Uses ';' as a separator as that is not allowed as part of a node/property name.

    Each unique location is converted to one of three forms:
    - A node path, e.g. "/my/path"
    - A node property path, e.g. "/my/path;my-prop"
    - A node property element path, e.g., "/my/path;my-prop;0"

    Lists of locations are converted into lists of identifiers.
    """
    match dt_src:
        case None:
            return None
        case edtlib.Node() as node:
            return f"{node.path}"
        case edtlib.Property() as prop:
            return f"{prop.node.path};{prop.name}"
        case (edtlib.Property() as prop, idx):
            return f"{prop.node.path};{prop.name};{idx}"
        case list():
            return [dt_to_unit_src(e) for e in dt_src]
        case _:
            raise ValueError(f"Unrecognized dt src {dt_src}")


class NoDefault: ...


NO_DEFAULT = NoDefault


def dt_prop(node: edtlib.Node, name: str, default: Any = NO_DEFAULT) -> uicr.Value[Any]:
    """Get the property value and identfier of a property.
    Optionally returns a default value.
    """
    try:
        prop = node.props[name]
    except KeyError:
        if default != NO_DEFAULT:
            return uicr.Value(default, src=[])
        raise

    return uicr.Value(prop.val, src=dt_to_unit_src(prop))


def dt_array_prop(
    node: edtlib.Node, name: str, default: list[Any] | Type[NO_DEFAULT] = NO_DEFAULT
) -> list[uicr.Value[Any]]:
    """Get the member values and identifiers of an array property.
    Optionally returns a default value.
    """
    try:
        prop = node.props[name]
    except KeyError:
        if default != NO_DEFAULT:
            return [uicr.Value(e, src=[]) for e in default]
        raise

    return [
        uicr.Value(v, src=dt_to_unit_src((prop, i))) for i, v in enumerate(prop.val)
    ]


def dt_partition_address_get(node: edtlib.Node) -> uicr.Value[int]:
    """Get the absolute address and identifiers for a "fixed-partitions" child node."""
    gparent = node.parent.parent
    gparent_addr = gparent.regs[0].addr
    self_addr = node.regs[0].addr
    self_src = dt_to_unit_src((node.props["reg"], 0))
    full_addr = gparent_addr + self_addr
    return uicr.Value(full_addr, src=self_src)


def dt_mem_node_is_secure(node: edtlib.Node) -> uicr.Value[bool]:
    """Get the secure permission and identifers for a memory node."""
    n = node
    while n is not None:
        if "nordic,owned-partitions" in n.compats or "nordic,owned-memory" in n.compats:
            if "nordic,access" in n.props:
                prop = (n.props["nordic,access"], 1)
                secure = bool(
                    n.props["nordic,access"].val[1] & NordicAccessPerm.NRF_PERM_S
                )
            else:
                prop = n.props["perm-secure"]
                secure = prop.val
            return uicr.Value(secure, src=dt_to_unit_src(prop))
        n = n.parent

    return uicr.Value(False, src=[])


def dt_reg_addr(node: edtlib.Node, index: int = 0) -> uicr.Value[int]:
    """Get a register address and property identifier for a node."""
    addr = node.regs[index].addr
    src = dt_to_unit_src((node.props["reg"], index))
    return uicr.Value(addr, src=src)


def dt_reg_size(node: edtlib.Node, index: int = 0) -> uicr.Value[int]:
    """Get a register size and property identifier for a node."""
    size = node.regs[index].size
    src = dt_to_unit_src((node.props["reg"], index))
    return uicr.Value(size, src=src)


def dt_node_processor_id(
    node: edtlib.Node,
    default: int | uicr.Value[int] | Type[NO_DEFAULT] = NO_DEFAULT,
    *,
    interrupts_only: bool = True,
) -> uicr.Value[int]:
    """Determine the processor ID a node corresponds to.
    This can be used to determine the CPU that will receive IRQs for a given peripheral.
    """
    processors: list[uicr.Value[int]] = []

    for irq in node.interrupts:
        irq_ctrl = irq.controller
        try:
            irq_processors = processor_ids_from_nodelabels(irq_ctrl.labels)
        except ValueError:
            continue
        for processor_id in irq_processors:
            processors.append(
                uicr.Value(processor_id.value, src=dt_to_unit_src(irq_ctrl))
            )

    if not processors:
        try:
            node_processors = processor_ids_from_nodelabels(node.labels)
            for processor_id in node_processors:
                processors.append(
                    uicr.Value(processor_id.value, src=dt_to_unit_src(node))
                )
        except ValueError:
            pass

    if not processors:
        if default == NO_DEFAULT:
            raise RuntimeError(
                "No unique processor ID could be found based on interrupt controllers "
                f"{'or nodelabels ' if not interrupts_only else ''}for node {node.path}"
            )
        if isinstance(default, uicr.Value):
            return default
        return uicr.Value(default, src=[])

    unique_processor_ids = set((i.val for i in processors))
    if len(unique_processor_ids) > 1:
        raise RuntimeError(
            f"Peripheral node {node.path} corresponds to multiple processors "
            f"({unique_processor_ids}), which is not supported."
        )

    return processors[0]


def processor_ids_from_nodelabels(labels: list[str]) -> list[ProcessorID]:
    """Deduce a processor ID from a list of devicetree nodelabels."""
    substring_processor = {
        "cpusec": ProcessorID.SECURE,
        "cpuapp": ProcessorID.APPLICATION,
        "cpurad": ProcessorID.RADIOCORE,
        "cpucell": ProcessorID.CELLCORE,
        "cpubbpr": ProcessorID.BBPR,
        "cpusys": ProcessorID.SYSCTRL,
        "cpuppr": ProcessorID.PPR,
        "cpuflpr": ProcessorID.FLPR,
    }
    processors = {
        processor_id
        for substring, processor_id in substring_processor.items()
        if any(substring in label for label in labels)
    }
    return list(processors)


def dt_channels_get(
    node: edtlib.Node,
    owned_name: str = "owned-channels",
    nonsecure_name: str = "nonsecure-channels",
) -> list[tuple[uicr.Value[int], uicr.Value[bool]]]:
    owned = []
    owned.extend(dt_array_prop(node, owned_name, default=[]))
    owned.extend(dt_array_prop(node, f"child-{owned_name}", default=[]))

    sec_lookup = {}
    if nonsecure_name in node.props:
        nonsecure = dt_array_prop(node, nonsecure_name)
        sec_lookup.update({v.val: uicr.Value(False, src=v.src) for v in nonsecure})

    default_sec = dt_node_is_secure(node)
    channels = []
    for ch in owned:
        sec = sec_lookup.setdefault(ch.val, default_sec)
        channels.append((ch, sec))

    return channels


def dt_node_is_secure(node: edtlib.Node) -> uicr.Value[bool]:
    if node.bus_node is not None and node.bus_node.regs:
        addr = dt_reg_addr(node.bus_node)
    elif node.regs:
        addr = dt_reg_addr(node)
    else:
        raise ValueError(
            f"Failed to determine security of {node.path} "
            "from the address of its bus node or itself"
        )

    secure = addr.val == secure_address_get(addr.val)

    return uicr.Value(secure, src=addr.src)


def dt_processor_id(devicetree: edtlib.EDT) -> ProcessorID:
    """Get processor information from a domain's devicetree."""
    cpus = [
        node
        for node in devicetree.get_node("/cpus").children.values()
        if node.name.startswith("cpu@")
    ]
    if len(cpus) != 1:
        raise RuntimeError(
            f"Expected exactly 1 'cpu' node, but devicetree contained {len(cpus)} nodes"
        )

    try:
        return ProcessorID(cpus[0].regs[0].addr)
    except Exception:
        raise RuntimeError(
            f"Devicetree 'cpu' node has invalid Processor ID {cpus[0].regs[0].addr}"
        )


@dataclass(frozen=True)
class NrfPsel:
    """Decoded NRF_PSEL values."""

    fun: int
    port: int
    pin: int

    @classmethod
    def from_raw(cls, psel_value: int) -> NrfPsel:
        """Decode a raw NRF_PSEL encoded int value to its individual parts."""
        port, pin = divmod(psel_value & (~NRF_PSEL_FUN_MASK), NRF_PSEL_GPIO_PIN_COUNT)
        fun = (psel_value & NRF_PSEL_FUN_MASK) >> NRF_PSEL_FUN_POS
        return NrfPsel(fun=fun, port=port, pin=pin)

    def is_disconnected(self) -> bool:
        """True if the value represents a disconnected pin"""
        return (self.port * NRF_PSEL_GPIO_PIN_COUNT + self.pin) == NRF_PSEL_PIN_MASK


@enum.unique
class NordicAccessPerm(enum.IntFlag):
    """Permission flags used with the "nordic,owned-memory" devicetree binding."""

    NRF_PERM_R = 1 << 0
    NRF_PERM_W = 1 << 1
    NRF_PERM_X = 1 << 2
    NRF_PERM_S = 1 << 3
    NRF_PERM_NSC = 1 << 4


@enum.unique
class NordicTddSource(enum.IntFlag):
    """Trace source flags used with the "nordic,tddconf" binding"""

    SOURCE_STMMAINCORE = 1 << 0
    SOURCE_ETMMAINCORE = 1 << 1
    SOURCE_STMHWEVENTS = 1 << 2
    SOURCE_STMPPR = 1 << 3
    SOURCE_STMFLPR = 1 << 4


# # Bit position of the function bits in the pinctrl pin value encoded from NRF_PSEL()
NRF_PSEL_FUN_POS = 24
# # Mask for the function bits in the pinctrl pin value encoded from NRF_PSEL()
NRF_PSEL_FUN_MASK = 0xFF << NRF_PSEL_FUN_POS
# Number of pins per port used in NRF_PSEL()
NRF_PSEL_GPIO_PIN_COUNT = 32
# Mask for the port, pin bits in the pinctrl pin value encoded from NRF_PSEL()
NRF_PSEL_PIN_MASK = 0x1FF

# Pin functions used with pinctrl, see include/zephyr/dt-bindings/pinctrl/nrf-pinctrl.h
# Only the functions relevant for CTRLSEL deduction have been included.
NRF_FUN_UART_TX = 0
NRF_FUN_UART_RX = 1
NRF_FUN_UART_RTS = 2
NRF_FUN_UART_CTS = 3
NRF_FUN_SPIM_SCK = 4
NRF_FUN_SPIM_MOSI = 5
NRF_FUN_SPIM_MISO = 6
NRF_FUN_SPIS_SCK = 7
NRF_FUN_SPIS_MOSI = 8
NRF_FUN_SPIS_MISO = 9
NRF_FUN_SPIS_CSN = 10
NRF_FUN_TWIM_SCL = 11
NRF_FUN_TWIM_SDA = 12
NRF_FUN_PWM_OUT0 = 22
NRF_FUN_PWM_OUT1 = 23
NRF_FUN_PWM_OUT2 = 24
NRF_FUN_PWM_OUT3 = 25
NRF_FUN_EXMIF_CK = 35
NRF_FUN_EXMIF_DQ0 = 36
NRF_FUN_EXMIF_DQ1 = 37
NRF_FUN_EXMIF_DQ2 = 38
NRF_FUN_EXMIF_DQ3 = 39
NRF_FUN_EXMIF_DQ4 = 40
NRF_FUN_EXMIF_DQ5 = 41
NRF_FUN_EXMIF_DQ6 = 42
NRF_FUN_EXMIF_DQ7 = 43
NRF_FUN_EXMIF_CS0 = 44
NRF_FUN_EXMIF_CS1 = 45
NRF_FUN_CAN_TX = 46
NRF_FUN_CAN_RX = 47
NRF_FUN_TWIS_SCL = 48
NRF_FUN_TWIS_SDA = 49
NRF_FUN_EXMIF_RWDS = 50
NRF_FUN_GRTC_CLKOUT_FAST = 55
NRF_FUN_GRTC_CLKOUT_32K = 56

# Under PR here https://github.com/nrfconnect/sdk-zephyr/pull/2314/files
NRF_FUN_TDM_SCK_M = 71
NRF_FUN_TDM_SCK_S = 72
NRF_FUN_TDM_FSYNC_M = 73
NRF_FUN_TDM_FSYNC_S = 74
NRF_FUN_TDM_SDIN = 75
NRF_FUN_TDM_SDOUT = 76
NRF_FUN_TDM_MCK = 77

# Value used to ignore the function field and only check (port, pin)
FUN_IGNORE = -1

# Deliberately defined as placeholders
NRF_FUN_I3C_SDA = 0xFF - 1
NRF_FUN_I3C_SCL = 0xFF


@dataclass(frozen=True)
class GpiosProp:
    """CTRLSEL lookup table entry for *-gpios properties"""

    name: str
    port: int
    pin: int


PINCTRL_CTRLSEL_LOOKUP_NRF54H20 = {
    # I3C120
    0x5F8D_3000: {
        # P2
        NrfPsel(fun=NRF_FUN_I3C_SDA, port=2, pin=1): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_I3C_SCL, port=2, pin=0): Ctrlsel.CAN_PWM_I3C,
        # P6
        NrfPsel(fun=NRF_FUN_I3C_SDA, port=6, pin=2): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_I3C_SCL, port=6, pin=1): Ctrlsel.CAN_PWM_I3C,
    },
    # CAN120
    0x5F8D_8000: {
        # P2
        NrfPsel(fun=NRF_FUN_CAN_TX, port=2, pin=9): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_CAN_RX, port=2, pin=8): Ctrlsel.CAN_PWM_I3C,
        # P9
        NrfPsel(fun=NRF_FUN_CAN_TX, port=9, pin=5): Ctrlsel.CAN,
        NrfPsel(fun=NRF_FUN_CAN_RX, port=9, pin=4): Ctrlsel.CAN,
    },
    # I3C121
    0x5F8D_E000: {
        # P2
        NrfPsel(fun=NRF_FUN_I3C_SDA, port=2, pin=3): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_I3C_SCL, port=2, pin=2): Ctrlsel.CAN_PWM_I3C,
        # P7
        NrfPsel(fun=NRF_FUN_I3C_SDA, port=7, pin=3): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_I3C_SCL, port=7, pin=2): Ctrlsel.CAN_PWM_I3C,
    },
    # PWM120
    0x5F8E_4000: {
        # P2
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=2, pin=4): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=2, pin=5): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=2, pin=6): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=2, pin=7): Ctrlsel.CAN_PWM_I3C,
        # P6
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=6, pin=6): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=6, pin=7): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=6, pin=8): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=6, pin=9): Ctrlsel.CAN_PWM_I3C,
        # P7
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=7, pin=0): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=7, pin=1): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=7, pin=6): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=7, pin=7): Ctrlsel.CAN_PWM_I3C,
    },
    # PWM130
    0x5F9A_4000: {
        # P9
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=9, pin=2): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=9, pin=3): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=9, pin=4): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=9, pin=5): Ctrlsel.CAN_PWM_I3C,
    },
    # SPIM130/SPIS130/TWIM130/TWIS130/UARTE130
    0x5F9A_5000: {
        # SPIM mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=9, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=9, pin=2): Ctrlsel.SERIAL0,
        GpiosProp(name="cs-gpios", port=9, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=9, pin=4): Ctrlsel.SERIAL0,
        # SPIS mappings
        NrfPsel(fun=NRF_FUN_SPIS_MISO, port=9, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_MOSI, port=9, pin=2): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_CSN, port=9, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_SCK, port=9, pin=4): Ctrlsel.SERIAL0,
        # TWIM mappings
        NrfPsel(fun=NRF_FUN_TWIM_SDA, port=9, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_TWIM_SCL, port=9, pin=4): Ctrlsel.SERIAL0,
        # TWIS mappings
        NrfPsel(fun=NRF_FUN_TWIS_SDA, port=9, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_TWIS_SCL, port=9, pin=4): Ctrlsel.SERIAL0,
        # UARTÈ mappings
        NrfPsel(fun=NRF_FUN_UART_TX, port=9, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RX, port=9, pin=4): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_UART_CTS, port=9, pin=2): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=9, pin=3): Ctrlsel.SERIAL0,
    },
    # SPIM131/SPIS131/TWIM131/TWIS131/UARTE131
    0x5F9A_6000: {
        # SPIM mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=9, pin=0): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=9, pin=2): Ctrlsel.CAN_TDM_SERIAL2,
        GpiosProp(name="cs-gpios", port=9, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=9, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        # SPIS mappings
        NrfPsel(fun=NRF_FUN_SPIS_MISO, port=9, pin=0): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_SPIS_MOSI, port=9, pin=2): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_SPIS_CSN, port=9, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_SPIS_SCK, port=9, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        # TWIM mappings
        NrfPsel(fun=NRF_FUN_TWIM_SDA, port=9, pin=0): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TWIM_SCL, port=9, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        # TWIS mappings
        NrfPsel(fun=NRF_FUN_TWIS_SDA, port=9, pin=0): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TWIS_SCL, port=9, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        # UARTÈ mappings
        NrfPsel(fun=NRF_FUN_UART_TX, port=9, pin=0): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_UART_RX, port=9, pin=1): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_CTS, port=9, pin=2): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=9, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
    },
    # VPR121 (FLPR)
    0x5F8D_4000: {
        # P1
        NrfPsel(fun=FUN_IGNORE, port=1, pin=8): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=9): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=10): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=11): Ctrlsel.VPR_GRC,
        # P2
        NrfPsel(fun=FUN_IGNORE, port=2, pin=0): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=1): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=2): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=3): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=4): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=5): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=6): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=7): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=8): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=9): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=10): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=11): Ctrlsel.VPR_GRC,
        # P6
        NrfPsel(fun=FUN_IGNORE, port=6, pin=0): Ctrlsel.VPR_GRC,
        # (pin 1-2 are not connected with VIO)
        NrfPsel(fun=FUN_IGNORE, port=6, pin=3): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=4): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=5): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=6): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=7): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=8): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=9): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=10): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=11): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=12): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=6, pin=13): Ctrlsel.VPR_GRC,
        # P7
        NrfPsel(fun=FUN_IGNORE, port=7, pin=0): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=7, pin=1): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=7, pin=2): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=7, pin=3): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=7, pin=4): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=7, pin=5): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=7, pin=6): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=7, pin=7): Ctrlsel.VPR_GRC,
        # P9
        NrfPsel(fun=FUN_IGNORE, port=9, pin=0): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=9, pin=1): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=9, pin=2): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=9, pin=3): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=9, pin=4): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=9, pin=5): Ctrlsel.VPR_GRC,
    },
    # SPIS120
    0x5F8E_5000: {
        NrfPsel(fun=NRF_FUN_SPIS_MISO, port=6, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_MOSI, port=6, pin=4): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_CSN, port=6, pin=9): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_SCK, port=6, pin=0): Ctrlsel.SERIAL0,
    },
    # SPIM120/UARTE120
    0x5F8E_6000: {
        # SPIM P6 mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=6, pin=8): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=6, pin=7): Ctrlsel.SERIAL0,
        GpiosProp(name="cs-gpios", port=6, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=6, pin=1): Ctrlsel.SERIAL0,
        # SPIM P7 mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=7, pin=7): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=7, pin=6): Ctrlsel.SERIAL0,
        GpiosProp(name="cs-gpios", port=7, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=7, pin=3): Ctrlsel.SERIAL0,
        # SPIM P2 mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=2, pin=6): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=2, pin=5): Ctrlsel.SERIAL0,
        GpiosProp(name="cs-gpios", port=2, pin=7): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=2, pin=3): Ctrlsel.SERIAL0,
        # UARTÈ P6 mappings
        NrfPsel(fun=NRF_FUN_UART_TX, port=6, pin=8): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_CTS, port=6, pin=7): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RX, port=6, pin=6): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=6, pin=5): Ctrlsel.SERIAL0,
        # UARTÈ P7 mappings
        NrfPsel(fun=NRF_FUN_UART_TX, port=7, pin=7): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_CTS, port=7, pin=6): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RX, port=7, pin=4): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=7, pin=5): Ctrlsel.SERIAL0,
        # UARTÈ P2 mappings
        NrfPsel(fun=NRF_FUN_UART_TX, port=2, pin=6): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_CTS, port=2, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RX, port=2, pin=4): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=2, pin=7): Ctrlsel.SERIAL0,
    },
    # SPIM121
    0x5F8E_7000: {
        # SPIM P6 mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=6, pin=13): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=6, pin=12): Ctrlsel.SERIAL0,
        GpiosProp(name="cs-gpios", port=6, pin=10): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=6, pin=2): Ctrlsel.SERIAL0,
        # SPIM P7 mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=7, pin=1): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_SPIS_MISO, port=7, pin=1): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=7, pin=0): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_SPIS_MOSI, port=7, pin=0): Ctrlsel.EXMIF_RADIO_SERIAL1,
        GpiosProp(name="cs-gpios", port=7, pin=4): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_SPIS_CSN, port=7, pin=4): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=7, pin=2): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_SPIS_SCK, port=7, pin=2): Ctrlsel.EXMIF_RADIO_SERIAL1,
        # SPIM P2 mappings
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=2, pin=11): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=2, pin=10): Ctrlsel.SERIAL0,
        GpiosProp(name="cs-gpios", port=2, pin=8): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=2, pin=2): Ctrlsel.SERIAL0,
    },
    # EXMIF
    0x5F09_5000: {
        NrfPsel(fun=NRF_FUN_EXMIF_CK, port=6, pin=0): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_RWDS, port=6, pin=2): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_CS0, port=6, pin=3): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ7, port=6, pin=4): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ1, port=6, pin=5): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ6, port=6, pin=6): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ0, port=6, pin=7): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ5, port=6, pin=8): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ3, port=6, pin=9): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ2, port=6, pin=10): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_DQ4, port=6, pin=11): Ctrlsel.EXMIF_RADIO_SERIAL1,
        NrfPsel(fun=NRF_FUN_EXMIF_CS1, port=6, pin=13): Ctrlsel.EXMIF_RADIO_SERIAL1,
    },
    # VPR130 (PPR)
    0x5F90_8000: {
        # P0
        NrfPsel(fun=FUN_IGNORE, port=0, pin=4): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=0, pin=5): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=0, pin=6): Ctrlsel.VPR_GRC,
        NrfPsel(fun=FUN_IGNORE, port=0, pin=7): Ctrlsel.VPR_GRC,
    },
    # TDM130
    0x5F99_2000: {
        # TDM P1 mappings
        NrfPsel(fun=NRF_FUN_TDM_MCK, port=1, pin=2): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_M, port=1, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_S, port=1, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDOUT, port=1, pin=4): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDIN, port=1, pin=5): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_M, port=1, pin=6): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_S, port=1, pin=6): Ctrlsel.CAN_TDM_SERIAL2,
        # TDM P2 mappings
        NrfPsel(fun=NRF_FUN_TDM_MCK, port=2, pin=0): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_M, port=2, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_S, port=2, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDOUT, port=2, pin=9): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDIN, port=2, pin=10): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_M, port=2, pin=11): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_S, port=2, pin=11): Ctrlsel.CAN_TDM_SERIAL2,
    },
    # TDM131
    0x5F99_7000: {
        # TDM P1 mappings
        NrfPsel(fun=NRF_FUN_TDM_MCK, port=1, pin=0): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_M, port=1, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_S, port=1, pin=1): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDOUT, port=1, pin=9): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDIN, port=1, pin=10): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_M, port=1, pin=11): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_S, port=1, pin=11): Ctrlsel.CAN_TDM_SERIAL2,
        # TDM P2 mappings
        NrfPsel(fun=NRF_FUN_TDM_MCK, port=2, pin=2): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_M, port=2, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SCK_S, port=2, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDOUT, port=2, pin=4): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_SDIN, port=2, pin=6): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_M, port=2, pin=7): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_TDM_FSYNC_S, port=2, pin=7): Ctrlsel.CAN_TDM_SERIAL2,
    },
    # GPIOTE0 (RAD)
    0x5302_7000: {
        # P1
        NrfPsel(fun=FUN_IGNORE, port=1, pin=4): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=5): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=6): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=7): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=8): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=9): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=10): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=1, pin=11): Ctrlsel.CAN,
        # P2
        NrfPsel(fun=FUN_IGNORE, port=2, pin=0): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=1): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=2): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=3): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=4): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=5): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=6): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=7): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=8): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=9): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=10): Ctrlsel.CAN,
        NrfPsel(fun=FUN_IGNORE, port=2, pin=11): Ctrlsel.CAN,
    },
}

PINCTRL_CTRLSEL_LOOKUP_NRF9280 = {
    # I3C120
    0x5F8D_3000: {
        NrfPsel(fun=NRF_FUN_I3C_SCL, port=2, pin=8): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_I3C_SDA, port=2, pin=9): Ctrlsel.CAN_PWM_I3C,
    },
    # CAN120
    0x5F8D_8000: {
        # P2
        NrfPsel(fun=NRF_FUN_CAN_RX, port=2, pin=10): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_CAN_TX, port=2, pin=11): Ctrlsel.CAN_TDM_SERIAL2,
        # P9
        NrfPsel(fun=NRF_FUN_CAN_RX, port=9, pin=4): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_CAN_TX, port=9, pin=5): Ctrlsel.CAN_TDM_SERIAL2,
    },
    # CAN121
    0x5F8D_B000: {
        # P2
        NrfPsel(fun=NRF_FUN_CAN_RX, port=2, pin=8): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_CAN_TX, port=2, pin=9): Ctrlsel.CAN_TDM_SERIAL2,
        # P9
        NrfPsel(fun=NRF_FUN_CAN_RX, port=9, pin=2): Ctrlsel.CAN_TDM_SERIAL2,
        NrfPsel(fun=NRF_FUN_CAN_TX, port=9, pin=3): Ctrlsel.CAN_TDM_SERIAL2,
    },
    # I3C121
    0x5F8D_E000: {
        NrfPsel(fun=NRF_FUN_I3C_SCL, port=2, pin=10): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_I3C_SDA, port=2, pin=11): Ctrlsel.CAN_PWM_I3C,
    },
    # PWM120
    0x5F8E_4000: {
        # P2
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=2, pin=0): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=2, pin=1): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=2, pin=2): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=2, pin=3): Ctrlsel.CAN_PWM_I3C,
        # P6
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=6, pin=0): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=6, pin=6): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=6, pin=1): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=6, pin=7): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=6, pin=2): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=6, pin=8): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=6, pin=3): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=6, pin=9): Ctrlsel.CAN_PWM_I3C,
    },
    # SPIS120
    0x5F8E_5000: {
        NrfPsel(fun=NRF_FUN_SPIS_CSN, port=6, pin=9): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_MISO, port=6, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_MOSI, port=6, pin=4): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_SCK, port=6, pin=0): Ctrlsel.SERIAL0,
    },
    # SPIM120/UARTE120
    0x5F8E_6000: {
        # SPIM P2 mappings
        GpiosProp(name="cs-gpios", port=2, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=2, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=2, pin=4): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=2, pin=0): Ctrlsel.SERIAL0,
        # SPIM P6 mappings
        GpiosProp(name="cs-gpios", port=6, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=6, pin=7): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=6, pin=8): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=6, pin=1): Ctrlsel.SERIAL0,
        # UARTE P2 mappings
        NrfPsel(fun=NRF_FUN_UART_CTS, port=2, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=2, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RX, port=2, pin=2): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_TX, port=2, pin=4): Ctrlsel.SERIAL0,
        # UARTE P6 mappings
        NrfPsel(fun=NRF_FUN_UART_CTS, port=6, pin=7): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=6, pin=5): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RX, port=6, pin=6): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_TX, port=6, pin=8): Ctrlsel.SERIAL0,
    },
    # SPIM121
    0x5F8E_7000: {
        # P2
        GpiosProp(name="cs-gpios", port=2, pin=6): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=2, pin=8): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=2, pin=9): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=2, pin=1): Ctrlsel.SERIAL0,
        # P6
        GpiosProp(name="cs-gpios", port=6, pin=10): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=6, pin=12): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=6, pin=13): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=6, pin=2): Ctrlsel.SERIAL0,
    },
    # PWM130
    0x5F9A_4000: {
        NrfPsel(fun=NRF_FUN_PWM_OUT0, port=9, pin=2): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT1, port=9, pin=3): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT2, port=9, pin=4): Ctrlsel.CAN_PWM_I3C,
        NrfPsel(fun=NRF_FUN_PWM_OUT3, port=9, pin=5): Ctrlsel.CAN_PWM_I3C,
    },
    # SPIM130/SPIS130/TWIM130/TWIS130/UARTE130
    0x5F9A_5000: {
        # SPIM mappings
        GpiosProp(name="cs-gpios", port=9, pin=1): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MISO, port=9, pin=2): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_MOSI, port=9, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIM_SCK, port=9, pin=0): Ctrlsel.SERIAL0,
        # SPIS mappings
        NrfPsel(fun=NRF_FUN_SPIS_CSN, port=9, pin=1): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_MISO, port=9, pin=3): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_MOSI, port=9, pin=2): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_SPIS_SCK, port=9, pin=0): Ctrlsel.SERIAL0,
        # TWIM mappings
        NrfPsel(fun=NRF_FUN_TWIM_SCL, port=9, pin=0): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_TWIM_SDA, port=9, pin=3): Ctrlsel.SERIAL0,
        # UARTE mappings
        NrfPsel(fun=NRF_FUN_UART_CTS, port=9, pin=2): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RTS, port=9, pin=1): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_RX, port=9, pin=4): Ctrlsel.SERIAL0,
        NrfPsel(fun=NRF_FUN_UART_TX, port=9, pin=3): Ctrlsel.SERIAL0,
    },
}

PINCTRL_CTRLSEL_LOOKUP = {
    Product.NRF54H20: PINCTRL_CTRLSEL_LOOKUP_NRF54H20,
    Product.NRF9280: PINCTRL_CTRLSEL_LOOKUP_NRF9280,
}


def dt_lookup_ctrlsel(
    product: Product,
    src: edtlib.PinCtrl | edtlib.Property,
    psel: NrfPsel | tuple[int, int],
) -> uicr.Value[int]:
    lut = PINCTRL_CTRLSEL_LOOKUP[product]

    if isinstance(src, edtlib.PinCtrl):
        identifier = dt_reg_addr(src.node)
        sub_entry = psel
    elif isinstance(src, edtlib.Property):
        assert isinstance(psel, tuple)
        try:
            identifier = dt_reg_addr(src.node)
        except IndexError:
            identifier = uicr.Value(src.node.label, src=dt_to_unit_src(src.node))
        sub_entry = GpiosProp(name=src.name, port=psel[0], pin=psel[1])
    else:
        raise ValueError(f"Unsupported GPIO pin source: {src}")

    ctrlsel = CTRLSEL_DEFAULT

    if identifier.val in lut:
        ident_lut = lut[identifier.val]
        if sub_entry in ident_lut:
            ctrlsel = ident_lut[sub_entry]
        elif isinstance(sub_entry, NrfPsel):
            # Check if this entry is enumerated with "ignored" function
            sub_entry_no_fun = NrfPsel(
                fun=FUN_IGNORE, port=sub_entry.port, pin=sub_entry.pin
            )
            ctrlsel = ident_lut.get(sub_entry_no_fun, CTRLSEL_DEFAULT)

    log.debug(
        f"identifier={hex(identifier.val) if isinstance(identifier.val, int) else identifier.val}, "
        f"{sub_entry=} -> {ctrlsel=}"
    )

    return uicr.Value(ctrlsel, src=identifier.src)


NRF_SAADC_AIN0 = 1
NRF_SAADC_AIN1 = 2
NRF_SAADC_AIN2 = 3
NRF_SAADC_AIN3 = 4
NRF_SAADC_AIN4 = 5
NRF_SAADC_AIN5 = 6
NRF_SAADC_AIN6 = 7
NRF_SAADC_AIN7 = 8
NRF_SAADC_AIN8 = 9
NRF_SAADC_AIN9 = 10
NRF_SAADC_AIN10 = 11
NRF_SAADC_AIN11 = 12
NRF_SAADC_AIN12 = 13
NRF_SAADC_AIN13 = 14

CHANNEL_LOOKUP = {
    # SAADC
    0x5F98_2000: {
        NRF_SAADC_AIN0: (1, 0),
        NRF_SAADC_AIN1: (1, 1),
        NRF_SAADC_AIN2: (1, 2),
        NRF_SAADC_AIN3: (1, 3),
        NRF_SAADC_AIN4: (1, 4),
        NRF_SAADC_AIN5: (1, 5),
        NRF_SAADC_AIN6: (1, 6),
        NRF_SAADC_AIN7: (1, 7),
        NRF_SAADC_AIN8: (9, 0),
        NRF_SAADC_AIN9: (9, 1),
        NRF_SAADC_AIN10: (9, 2),
        NRF_SAADC_AIN11: (9, 3),
        NRF_SAADC_AIN12: (9, 4),
        NRF_SAADC_AIN13: (9, 5),
    }
}


def dt_lookup_adc_channel_pins(
    channel: edtlib.Node,
) -> list[tuple[uicr.Value[int], uicr.Value[int]]]:
    lut = CHANNEL_LOOKUP

    address = secure_address_get(channel.parent.regs[0].addr)
    if address not in lut:
        return []

    pins = []

    if "zephyr,input-positive" in channel.props:
        prop = channel.props["zephyr,input-positive"]
        if prop.val in lut[address]:
            port, pin = lut[address][prop.val]
            src = dt_to_unit_src(prop)
            log.debug(
                f"{address=:08x}, {channel.props['zephyr,input-positive']=} -> ({port=}, {pin=})"
            )
            pins.append((uicr.Value(port, src=src), uicr.Value(pin, src=src)))

    if "zephyr,input-negative" in channel.props:
        prop = channel.props["zephyr,input-negative"]
        if prop.val in lut[address]:
            port, pin = lut[address][prop.val]
            src = dt_to_unit_src(prop)
            log.debug(
                f"{address=:08x}, {channel.props['zephyr,input-negative']=} -> ({port=}, {pin=})"
            )
            pins.append((uicr.Value(port, src=src), uicr.Value(pin, src=src)))

    return pins


NRF_COMP_LPCOMP_AIN0 = "AIN0"
NRF_COMP_LPCOMP_AIN1 = "AIN1"
NRF_COMP_LPCOMP_AIN2 = "AIN2"
NRF_COMP_LPCOMP_AIN3 = "AIN3"
NRF_COMP_LPCOMP_AIN4 = "AIN4"
NRF_COMP_LPCOMP_AIN5 = "AIN5"
NRF_COMP_LPCOMP_AIN6 = "AIN6"
NRF_COMP_LPCOMP_AIN7 = "AIN7"
NRF_COMP_LPCOMP_AIN8 = "AIN8"
NRF_COMP_LPCOMP_AIN9 = "AIN9"

COMP_LPCOMP_LOOKUP = {
    # COMP/LPCOMP
    0x5F98_3000: {
        NRF_COMP_LPCOMP_AIN0: (1, 0),
        NRF_COMP_LPCOMP_AIN1: (1, 1),
        NRF_COMP_LPCOMP_AIN2: (1, 2),
        NRF_COMP_LPCOMP_AIN3: (1, 3),
        NRF_COMP_LPCOMP_AIN4: (1, 4),
        NRF_COMP_LPCOMP_AIN5: (1, 5),
        NRF_COMP_LPCOMP_AIN6: (1, 6),
        NRF_COMP_LPCOMP_AIN7: (1, 7),
        NRF_COMP_LPCOMP_AIN8: (9, 0),
        NRF_COMP_LPCOMP_AIN9: (9, 1),
    }
}


def dt_lookup_comp_lpcomp_pins(
    comp_lpcomp: edtlib.Node,
) -> list[tuple[uicr.Value[int], uicr.Value[int]]]:
    lut = COMP_LPCOMP_LOOKUP

    address = secure_address_get(comp_lpcomp.regs[0].addr)
    if address not in lut:
        return []

    pins = []

    if "psel" in comp_lpcomp.props:
        prop = comp_lpcomp.props["psel"]
        if prop.val in lut[address]:
            port, pin = lut[address][prop.val]
            src = dt_to_unit_src(prop)
            log.debug(f"{address=:08x}, psel -> ({port=}, {pin=})")
            pins.append((uicr.Value(port, src=src), uicr.Value(pin, src=src)))

    if "extrefsel" in comp_lpcomp.props:
        prop = comp_lpcomp.props["extrefsel"]
        if prop.val in lut[address]:
            port, pin = lut[address][prop.val]
            src = dt_to_unit_src(prop)
            log.debug(f"{address=:08x}, extrefsel -> ({port=}, {pin=})")
            pins.append((uicr.Value(port, src=src), uicr.Value(pin, src=src)))

    return pins
