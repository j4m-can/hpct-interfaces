# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/value/__init__.py

"""Base interface value objects.
"""

import ipaddress

from .. import codec as _codec
from .. import checker as _checker
from ..base import NoValue, Value


class Boolean(Value):
    codec = _codec.Boolean()
    default = False


class Blob(Value):
    codec = _codec.Blob()


class Dict(Value):
    codec = _codec.Json()


class Float(Value):
    codec = _codec.Float()
    default = 0.0


class Integer(Value):
    codec = _codec.Integer()
    default = 0


class PositiveInteger(Integer):
    checker = _checker.IntegerRange(1, None)


class NegativeInteger(Integer):
    checker = _checker.IntegerRange(1, None)


class NonNegativeFloat(Float):
    checker = _checker.FloatRange(0.0, None)


class NonNegativeInteger(Integer):
    checker = _checker.IntegerRange(0, None)


class NonPositiveFloat(Float):
    checker = _checker.FloatRange(None, 0.0)


class NonPositiveInteger(Integer):
    checker = _checker.IntegerRange(None, 0)


class Noop(Value):
    codec = _codec.Noop()


class Ready(Boolean):
    pass


class String(Value):
    codec = _codec.String()
    default = ""
