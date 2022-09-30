# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/codec/network.py


"""Interface network codec objects.
"""


from . import Codec

import ipaddress
import logging
from typing import Any, Union


logger = logging.getLogger(__name__)


class IPAddress(Codec):
    """IP address: IPv4Address, IPv6Address."""

    types = [ipaddress.IPv4Address, ipaddress.IPv6Address]

    def _decode(self, value: str) -> Any:
        return ipaddress.ip_address(value)

    def _encode(self, value: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> str:
        return str(value)

    def decode(self, value: str) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
        return super().decode(value)

    def encode(self, value: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> str:
        return super().encode(value)


class IPNetwork(Codec):
    """IP network: IPv4Network, IPv6Network."""

    types = [ipaddress.IPv4Network, ipaddress.IPv6Network]

    def _decode(self, value: str) -> Any:
        return ipaddress.ip_network(value)

    def _encode(self, value: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> str:
        return str(value)

    def decode(self, value: str) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network]:
        return super().decode(value)

    def encode(self, value: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]) -> str:
        return super().encode(value)
