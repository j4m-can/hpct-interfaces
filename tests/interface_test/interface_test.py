#! /usr/bin/env python3
#
# interface_test.py


import json
import os.path
import logging
import sys

sys.path.insert(0, os.path.realpath("../../lib"))

from hpctinterfaces import checker
from hpctinterfaces.base import Interface, StructInterface, test
from hpctinterfaces.value import Boolean, Dict, Float, Integer, PositiveInteger, String
from hpctinterfaces.value.network import IPAddress, IPNetwork


logger = logging.getLogger(__name__)


class TestInterface(Interface):
    xboolean = Boolean(False)
    xfloat = Float(0.0)
    xfloatrange = Float(0.0, checker.FloatRange(-100.3, 20.93))
    xinteger = Integer(0)
    xintegerrange = Integer(0, checker.IntegerRange(100, 204))
    xpositive_integer = PositiveInteger(0)
    ipaddress = IPAddress("0.0.0.0")
    ipnetwork = IPNetwork("0.0.0.0/32")
    xdict = Dict({"x": 101})


class X(StructInterface):
    a = Integer(1)


class TestInterface2(Interface):

    x = X()
    y = String("hi")


if __name__ == "__main__":
    if 0:
        iface = TestInterface()

        test(iface, "xboolean", True)
        test(iface, "xboolean", "hello")
        test(iface, "xboolean", 123)

        test(iface, "xinteger", 123)
        test(iface, "xintegerrange", 123)

        test(iface, "xfloat", 12.3)
        test(iface, "xfloatrange", 123.23)
        test(iface, "xfloatrange", -23.3)
        test(iface, "xdict", {"x": 102})

        print("-----")
        iface.xdict["x"] = 99
        print(iface.xdict)
        print("-----")
        d = iface.xdict
        d["x"] = 99
        iface.xdict = d
        print(f"d ({d})")
        print(f"iface.xdict ({iface.xdict})")
        print("-----")

        print(json.dumps(iface.get_doc(), indent=2))

    if 1:
        iface = TestInterface2()
        print(f"before x.a ({iface.x.a}) y ({iface.y})")
        iface.x.a = 2
        iface.y = "bye"
        iface.mount("xx", X())
        iface.xx.a = 123

        print(f"after x.a ({iface.x.a}) y ({iface.y})")

        print(f"iface.x ({iface.x})")
        print(f"dir(iface) ({dir(iface)})")
        print(f"iface.__dict__ ({iface.__dict__})")
        print(f"iface._store ({iface._store})")
        print(f"iface.x._store ({iface.x._store})")

        print(json.dumps(iface.get_doc(), indent=2))
