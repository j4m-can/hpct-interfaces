# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/checker.py


"""Base implementation of Checker, and some common Checker subclasses.

A checker is not a substitue for a dedicated Value but a way to
check that a value meets specific constraints. A checker should be
general enough to be reused.
"""


import re
from typing import Any, List, Union
from urllib.parse import urlparse


class CheckError(Exception):
    pass


class Checker:
    """Holds parameters and provides a check() to check/validate a
    given value.
    """

    def __init__(self):
        self.params = {}

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__} params ({self.params})>"

    def check(self, value):
        """Return if the value check passes or not."""

        return True

    def get_doc(self):
        """Generate and return a dictionary describing the Checker."""

        doc = (self.__doc__ or "").strip()
        d = {
            "type": self.__class__.__name__,
            "module": self.__module__,
            "description": doc,
            "params": self.params,
        }
        return d


class IntegerRange(Checker):
    """Check for value within range [lo, hi].

    Note: lo/hi of None indicates no bound.
    """

    def __init__(self, lo: Union[int, None], hi: Union[int, None]):
        super().__init__()
        self.params.update(
            {
                "lo": lo,
                "hi": hi,
            }
        )

    def check(self, value: int):
        """Check value against lo and hi parameters."""

        lo = self.params["lo"]
        hi = self.params["hi"]

        if lo != None and value < lo:
            raise CheckError("value is below range")
        if hi != None and value > hi:
            raise CheckError("value is above range")
        return True


class FloatRange(Checker):
    """Check for value within range [lo, hi].

    Note: lo/hi of None indicates no bound.
    """

    def __init__(self, lo: Union[float, None], hi: Union[float, None]):
        super().__init__()
        self.params.update(
            {
                "lo": lo,
                "hi": hi,
            }
        )

    def check(self, value: float):
        """Check value against lo and hi parameters."""

        lo = self.params["lo"]
        hi = self.params["hi"]

        if lo != None and value < lo:
            raise CheckError("value is below range")
        if hi != None and value > hi:
            raise CheckError("value is above range")
        return True


class OneOf(Checker):
    """Check for value to match one of a list of values."""

    def __init__(self, values: List[Any]):
        super().__init__()
        if type(values) != list:
            raise CheckError("values must be a list")
        self.params["values"] = values

    def check(self, value: Any):
        return value in self.params["values"]


class Regexp(Checker):
    """Check that string value is matched by regular expression."""

    def __init__(self, regexp: str):
        """Setup.

        Delay compilation of regular expression to check(). Also,
        delays regexp validation check, too.
        """

        super().__init__()
        self.regexp = regexp
        self.cregexp = None

    def check(self, value: str):
        """Check value against regular expression."""

        if self.cregexp == None:
            try:
                self.cregexp = re.compile(self.regexp)
            except:
                raise CheckError("bad regular expression")
        return self.cregexp.match(value)


class URL(Checker):
    """URL with format: <scheme>://<host>.
    TODO: This approach is (embarrassingly) rudimentary. It can be
    improved to provide stronger validation/checking."""

    def check(self, value: str):
        """Check value URL format."""

        res = urlparse(str)
        return all([res.scheme, res.netloc])
