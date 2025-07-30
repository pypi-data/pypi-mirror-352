# Copyright (c) 2024 Nordic Semiconductor ASA
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import svd


def content_get_and_extend(field: svd.Field, msb_pos: int = 31) -> int:
    """Bit shift the field value so that it occupies the most significant bits of a 32-bit value"""
    return field.content << ((msb_pos + 1) - field.bit_width)


def content_truncate_and_set(field: svd.Field, content: int, msb_pos: int = 31) -> int:
    """Bit shift the field value so that it occupies the most significant bits of a 32-bit value"""
    truncate_bits = (msb_pos + 1) - field.bit_width
    truncate_mask = ~((1 << truncate_bits) - 1)

    if (content & truncate_mask) != content:
        raise ValueError(f"0x{content:08x} is not aligned to {(1 << truncate_bits)} B")

    new_content = content >> truncate_bits
    field.content = new_content

    return new_content


class SvdEnum:
    """Helper class for constructing commonly used SVD enums."""

    ENABLED = "Enabled"
    DISABLED = "Disabled"

    @classmethod
    def enabled_if(cls, is_enabled: bool) -> str:
        return cls.ENABLED if is_enabled else cls.DISABLED

    ALLOWED = "Allowed"
    NOT_ALLOWED = "NotAllowed"

    @classmethod
    def allowed_if(cls, is_allowed: bool) -> str:
        return cls.ALLOWED if is_allowed else cls.NOT_ALLOWED

    SECURE = "Secure"
    NONSECURE = "NonSecure"

    @classmethod
    def secure_if(cls, is_secure: bool) -> str:
        return cls.SECURE if is_secure else cls.NONSECURE

    REQUESTED = "Requested"
    NOT_REQUESTED = "NotRequested"

    @classmethod
    def requested_if(cls, is_requested: bool) -> str:
        return cls.REQUESTED if is_requested else cls.NOT_REQUESTED

    OWN = "Own"
    NOT_OWN = "NotOwn"

    SINK = "Sink"
    SOURCE = "Source"

    LINKED = "Linked"
    NOT_LINKED = "NotLinked"
