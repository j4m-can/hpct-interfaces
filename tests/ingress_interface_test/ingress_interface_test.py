#! /usr/bin/env python3
#
# ingress_interface_test.py


import json
import os.path
import logging
import sys

sys.path.insert(0, os.path.realpath("../../lib"))

from hpctinterfaces.base import test

from ingress import IngressRelationSuperInterface


logger = logging.getLogger(__name__)


# TODO: need a mock of the relation and bucket storage


def xtest(interface, value):
    """Test interface set and get. Assume interface attribute name is
    "value" in all cases. The storage key is _<classname>_store_value.
    """

    try:
        print(f"interface ({interface})")
        print(f"codec ({getattr(interface.__class__, 'value').codec})")
        print(f"checker ({getattr(interface.__class__, 'value').checker})")

        # assign
        print(f"original ({value})")
        interface.value = value

        # interface store
        print(f"store ({interface._store})")

        # get encoded value
        encoded = interface._store.get("value")
        print(f"encoded ({encoded})")

        # get back
        decoded = interface.value
        print(f"decoded ({decoded})")

        # validate
        print(f"match? ({decoded == value})")
    except Exception as e:
        # import traceback
        # traceback.print_exc()
        print(f"exception e ({e})")

    print("-----")
    print(json.dumps(interface.get_doc(), indent=2))
    print("==========")


if __name__ == "__main__":
    ingress_provider = IngressRelationSuperInterface(
        charm=None, relname="ingress", role="provider"
    )
    ingress_requirer = IngressRelationSuperInterface(
        charm=None, relname="ingress", role="requirer"
    )

    provider_app = ingress_provider.select("app")
    provider_app.set_mock()
    requirer_unit = ingress_requirer.select("unit")
    requirer_unit.set_mock()

    test(provider_app, "url", "http://x")
    test(provider_app, "url", "http://host:9999/app-model/0")

    test(requirer_unit, "name", "unit-name")
    test(requirer_unit, "host", "hostname")
    test(requirer_unit, "port", 4242)
    test(requirer_unit, "model", "model-name")

    print(json.dumps(ingress_provider.get_doc(), indent=2))
