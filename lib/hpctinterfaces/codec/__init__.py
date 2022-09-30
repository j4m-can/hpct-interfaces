# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/codec/__init__.py


"""Codecs perform the work of encoding and decoding according to an
encoding strategy. Encoding is integral to the codec. Codec validation
must passgit the test of ```value == decode(encode(value))```.
"""


import base64
import json
import logging
from typing import Any


NoneType = type(None)
logger = logging.getLogger(__name__)


class EncodingError(Exception):
    pass


class ParameterError(Exception):
    pass


class ValueError(Exception):
    pass


class Codec:
    """Base class for codecs."""

    types = None

    def __init__(self, *args, **kwargs):
        self.params = {}

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__})>"

    def _decode(self, s: str) -> Any:
        """Low-level decode (from string) without checks."""

        return s

    def _encode(self, value: Any) -> str:
        """Low-level encode (to string) without checks."""

        return value

    def check_type(self, value, types, e=None):
        """Check value type against list of types.

        Args:
            value: Value to check.
            types: List of types to check value against.

        Raises:
            ValueError on error.
        """

        if types == None:
            return
        elif type(value) not in types:
            if not e:
                e = ValueError(f'value type "{type(value)}" not one of "{types}"')
            raise e

    def decode(self, value: str) -> Any:
        """Decode string value to typed result.

        Subclasses should override this method with proper type
        annotations, then call super().decode().

        Args:
            value: Encoded string to decode.
        Returns:
            Decoded (original) form of value.
        """

        self.check_type(value, [str])
        value = self._decode(value)
        self.check_type(value, self.types)
        return value

    def encode(self, value) -> str:
        """Encode typed value to a string.

        Subclasses should override this method with proper type
        annotations, then call super().encode().

        Args:
            value: Value to encode.
        Returns:
            Encoded form of value.
        """

        self.check_type(value, self.types)
        value = self._encode(value)
        self.check_type(value, [str])
        return value

    def get_doc(self) -> dict:
        """Generate and return a dictionary describing the codec."""

        doc = (self.__doc__ or "").strip()
        d = {
            "type": self.__class__.__name__,
            "module": self.__module__,
            "description": doc,
            "params": self.params,
        }
        return d


class Blob(Codec):
    """Blob (byte-string)."""

    types = [bytes]

    def _decode(self, value: str) -> bytes:
        return base64.b85decode(value.encode("utf-8"))

    def _encode(self, value: bytes) -> str:
        return base64.b85encode(value).decode("utf-8")

    def decode(self, value: str) -> bytes:
        return super().decode(value)

    def encode(self, value: bytes) -> str:
        return super().encode(value)


class Boolean(Codec):
    """Boolean: True, False."""

    types = [bool]

    def _decode(self, value: str) -> Any:
        match value:
            case "1":
                return True
            case "0":
                return False
        raise ValueError()

    def _encode(self, value: bool) -> str:
        match value:
            case True:
                return "1"
            case False:
                return "0"
        raise ValueError()

    def decode(self, value: str) -> bool:
        return super().decode(value)

    def encode(self, value: bool) -> str:
        return super().encode(value)


class Float(Codec):
    """Float."""

    types = [float]

    def _decode(self, value: str) -> float:
        return float(value)

    def _encode(self, value: float) -> str:
        return str(value)

    def decode(self, value: str) -> float:
        return super().decode(value)

    def encode(self, value: float) -> str:
        return super().encode(value)


class Integer(Codec):
    """Integer."""

    codec_types = [int]

    def _decode(self, value: str) -> int:
        return int(value)

    def _encode(self, value: int) -> str:
        return str(value)

    def decode(self, value: str) -> int:
        return super().decode(value)

    def encode(self, value: int) -> str:
        return super().encode(value)


class Json(Codec):
    """JSON-type object.

    This codec works for dicts in general except for:
    * basic types
    * non-string keys
    """

    types = [dict]

    def _decode(self, value: str) -> dict:
        return json.loads(value)

    def _encode(self, value: dict) -> str:
        return json.dumps(value)

    def decode(self, value: str) -> dict:
        return super().decode(value)

    def encode(self, value: dict) -> str:
        return super().encode(value)


class Noop(Codec):
    """Noop / no change."""

    def decode(self, value: str) -> Any:
        return value

    def encode(self, value: Any) -> str:
        return value


class Ready(Boolean):
    """Convert ready status: True, False."""

    pass


class String(Codec):
    """String codec (noop)."""

    def decode(self, value: str) -> str:
        return value

    def encode(self, value: str) -> str:
        return value
