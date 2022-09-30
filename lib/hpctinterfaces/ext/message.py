# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/ext/message.py

"""Interface to support message data.

To use:
    class MyInterface(UnitInterface):
        msg = MessageInterface()

    iface = MyInterface()
    iface.msg.dtype = "t"
    iface.msg.tdata = "Hello World!"
    iface.msg.src = self.unit.name
    iface.msg.dst = other.unit.name
    iface.msg.set_nonce()
"""

import secrets

from hpctinterfaces import checker as _checker
from hpctinterfaces.base import Interface
from hpctinterfaces.value import Blob, String


class MessageInterface(Interface):
    """Holds a message ([b]inary or [t]ext) and helpful metadata."""

    bdata = Blob()
    comment = String("")
    dtype = String(checker=_checker.OneOf(["b", "t"]))
    dst = String("")
    nonce = String("")
    src = String("")
    tag = String("")
    tdata = String("")

    def set_nonce(self):
        self.nonce = secrets.token_urlsafe()
