# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/tests/ingress_interface/ingress.py

"""Proof of concept to represent description at
    https://github.com/canonical/charm-relation-interfaces/tree/main/ingress_per_unit

using SuperInterface.


provider metadata.yaml
-----
provides:
  ingress:
    interface: ingress
-----


requirer metadata.yaml
-----
requires:
  ingress:
    interface: ingress
-----

"""


import re

from hpctinterfaces import checker, codec
from hpctinterfaces import interface_registry
from hpctinterfaces.relation import (
    AppBucketInterface,
    Value,
    RelationSuperInterface,
    UnitBucketInterface,
)


INGRESS_URL_RE = (
    "(?P<schema>http|https)"
    "://(?P<hostname>[^:]+)(:(?P<port>[0-9]+))?"
    "/(?P<appname>.*)-(?P<modelname>.*)"
    "/(?P<unit>[0-9]+)$"
)


class IngressUrlChecker(checker.Checker):
    def check(self, value):
        if not re.match(INGRESS_URL_RE, value):
            raise checker.CheckError("url does not conform")


class IngressRelationSuperInterface(RelationSuperInterface):
    """From https://github.com/canonical/charm-relation-interfaces/tree/main/ingress_per_unit.

    Usage
    -----
    This relation interface describes the expected behavior of any charm
    claiming to be able to provide or consume ingress per unit data.

    In most cases, this will be accomplished using the ingress library,
    although charm developers are free to provide alternative libraries
    as long as they fulfill the behavioral and schematic requirements
    described in this document.

    Direction
    ---------
    The ingress-per-unit interface implements a provider/requirer
    pattern. The consumer is a charm that wishes to receive ingress per
    unit, and the provider is a charm able to provide it.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interface_classes[("provider", "app")] = IngressProviderAppBucketInterface
        self.interface_classes[("requirer", "unit")] = IngressRequirerUnitBucketInterface


class IngressProviderAppBucketInterface(AppBucketInterface):
    """
    Behavior
    --------
    * Is expected to provide ingress for the remote applications
        requesting it.
    * Is expected to respect the ingress parameters sent by the
        requirer: hostname, port and model name (namespace).
    * Is expected to publish the ingress url via relation data. The
        url is expected to have the following structure:
            http://[ingress hostname]:[ingress port]/[app-name]-[model-name]/

        where:
        * ingress hostname and url are the hostname and urls that the
            ingress is configured with
        * app-name is the name of the application requesting ingress
        * model-name is the name of the model the application
            requesting ingress is deployed into

        The structure of this URL is fixed in the generic ingress
        schema; specific ingress providers implementations may offer
        some way of customising it.

    Data
    ----
    Exposes a url field containing the url at which ingress is
    available. Should be placed in the application databag.
    """

    # minimal conversion/validation
    url = Value(codec.String(), None, IngressUrlChecker())


class IngressRequirerUnitBucketInterface(UnitBucketInterface):
    """
    Behavior
    --------
    * Is expected to be able to provide a hostname, a port, a unit name
        and a model name (namespace).

    Data
    ----
    Exposes the unit name, model name, hostname and port at which
    ingress should be provided. Should be placed in the unit databag of
    each unit of the requirer application.
    """

    name = Value(codec.String(), "")
    host = Value(codec.String(), "")
    port = Value(codec.Integer(), -1, checker.Port())
    model = Value(codec.String(), "")


# register interfaces

interface_registry.register("relation-ingress", IngressRelationSuperInterface)
