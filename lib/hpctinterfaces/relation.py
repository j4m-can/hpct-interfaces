# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/relation.py


"""Base collection of operator relation-oriented interfaces.
"""


import logging
from typing import Any, Union

from . import interface_registry
from .base import BaseInterface, Interface, NoValue, SuperInterface
from .value import Blob, Ready
from .value.network import IPAddress, IPNetwork


logger = logging.getLogger(__name__)

OTHER_ROLE = {
    "peer": "peer",
    "provider": "requirer",
    "requirer": "provider",
}


#
# base classes
#


class MockRelation:
    def __init__(self):
        self.data = {
            "app": {},
            "unit": {},
        }


class BucketInterface(BaseInterface):
    """Interface for relation bucket storage."""

    def __init__(
        self,
        charm,
        relname: str,
        bucketkey: str,
        relation_id: Union[int, None] = None,
        mock=False,
        *args,
        **kwargs
    ):
        self._charm = charm
        self._relname = relname
        self._bucketkey = bucketkey
        self._relation_id = relation_id
        self._mock = False
        if mock:
            self.set_mock()

        super().__init__(*args, **kwargs)

    def _store_clear(self, fqkey):
        """Clear/delete key from storage (bucket).

        According to `RelationDataContent.__delitem__()`.
        """

        self._store_set(fqkey, "")

    def _store_get(self, fqkey: str, default=None):
        """Accessor (for raw data) to the relation store."""

        fqkey = fqkey.replace("_", "-")

        bucketkey = self._bucketkey
        relation = self.get_relation()

        if relation:
            value = relation.data[bucketkey].get(fqkey, NoValue)
            if value == NoValue:
                value = default
            return value

    def _store_set(self, fqkey: str, value: Any):
        """Accessor (for raw data) to the relation store."""

        fqkey = fqkey.replace("_", "-")

        bucketkey = self._bucketkey

        for relation in self.get_relations():
            relation.data[bucketkey].update({fqkey: value})

    def get_relation(self, relation_id=None):
        """Return relation associated with registered relation name."""

        if self._mock:
            return self._mock_relation
        else:
            relation_id = relation_id if relation_id != None else self._relation_id
            return self._charm.model.get_relation(self._relname, relation_id)

    def get_relations(self):
        """Return relations associated with registered relation name."""

        if self._mock:
            relations = [self._mock_relation]
        else:
            if self._relation_id != None:
                relations = [self.get_relation()]
            else:
                relations = self._charm.model.relations.get(self._relname, [])

        return relations

    def get_leader_relations(self):
        """Return relations associated with registered relation name,
        only if leader.
        """

        if self._mock:
            relations = [self._mock_relation]
        else:
            if self._charm.unit.is_leader():
                relations = self.get_relations()
            else:
                relations = []

        return relations

    def is_ready(self, relation_id=None):
        """Return if the relation is ready."""

        return len(self.get_relations(relation_id)) > 0

    def set_mock(self):
        self._mock = True
        self._mock_relation = MockRelation()


class AppBucketInterface(BucketInterface):
    """Base app relation bucket interface.

    Note All app relation bucket interfaces should subclass this!
    """

    pass


class AppConfigBucketInterface(AppBucketInterface):
    """ """

    config = Blob()


class AppSecureConfigBucketInterface(AppBucketInterface):
    """ """

    config = Blob()


class UnitBucketInterface(BucketInterface):
    """Base unit relation bucket interface.

    The egress_subnets, ingress_address, private_address are available
    for all unit relation data buckets.

    Note: All unit relation bucket interfaces should subclass this!
    """

    egress_subnets = IPNetwork(access="r")
    ingress_address = IPAddress(access="r")
    private_address = IPAddress(access="r")


#
# other subclasses
#


class AppReadyBucketInterface(AppBucketInterface):
    """Provides status that the application is "ready"."""

    status = Ready(False)


class UnitReadyBucketInterface(UnitBucketInterface):
    """Provides status that the unit is "ready"."""

    status = Ready(False)


class RelationSuperInterface(SuperInterface):
    """Super interface for working with relation interfaces/data.

    Usage:
    ```
        slurm_ready = AppReadySuperInterface(self, "slurm-ready")
        slurm_ready.provider_app_interface.status = False
        slurm_ready.select(event.app).status = False
    ```
    """

    def __init__(self, charm, relname: str, role=None):
        super().__init__()

        self.charm = charm
        self.relname = relname
        self.role = role

        self.interface_classes = {
            ("provider", "app"): None,
            ("provider", "unit"): UnitBucketInterface,
            ("requirer", "app"): None,
            ("requirer", "unit"): UnitBucketInterface,
            ("peer", "app"): None,
            ("peer", "unit"): None,
        }

    def get_doc(self, show_values=False):
        """Return json doc about super interface."""

        doc = (self.__doc__ or "").strip()
        j = {
            "type": self.__class__.__name__,
            "module": self.__module__,
            "description": doc,
        }
        jj = j["interfaces"] = {}

        for role in ["provider", "requirer", "peer"]:
            for buckettype in ["app", "unit"]:
                jjj = jj[role] = {}
                interface_cls = self.get_interface_class(role, buckettype)
                if interface_cls == None:
                    jjj[buckettype] = None
                else:
                    interface = interface_cls(self.charm, self.relname, None)
                    jjj[buckettype] = interface.get_doc(show_values)

        return j

    def get_interface_class(self, role, buckettype):
        """Return interface class for role and buckettype (one of "app",
        "unit").
        """
        return self.interface_classes.get((role, buckettype))

    def get_role(self):
        """Determine "role" (provider, requirer, peer)."""

        if self.role:
            return self.role

        meta = self.charm.framework.meta
        if self.relname in meta.provides:
            return "provider"
        elif self.relname in meta.requires:
            return "requirer"
        else:
            return "peer"

    def is_ready(self):
        """Return if the relation is ready."""

        return len(self.charm.model.get_relations(self.relname)) > 0

    def select(self, bucketkey, relation_id=None):
        """Select and return interface to use.

        When determining the interface to use, the role and bucketkey
        are necessary. In particular, when the bucket key is event.app
        or event.unit, then the interface is that of the "other" side.
        E.g., when the provider wants access to the event.app, this means
        the requirer app bucket.

        When working with the bucket directly (e.g.,
        relation.data[event.app]), the "select" is done mentally in
        order to deal with the bucket data suitably.
        """

        role = self.get_role()

        if bucketkey in ["app", "unit"]:
            # special handling for explicit interface selection
            buckettype = bucketkey
            rolekey = role
        else:
            from ops.model import Application

            isapp = isinstance(bucketkey, Application)
            if isapp:
                isselfapp = bucketkey == self.charm.app
            else:
                isselfapp = bucketkey.app == self.charm.app

            buckettype = isapp and "app" or "unit"

            if role != "peer":
                rolekey = isselfapp and role or OTHER_ROLE[role]
            else:
                rolekey = "peer"

        interface_cls = self.get_interface_class(rolekey, buckettype)
        iface = interface_cls(self.charm, self.relname, bucketkey, relation_id)

        return iface


class AppConfigRelationSuperInterface(RelationSuperInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interface_classes[("provider", "app")] = AppConfigBucketInterface


class AppSecureConfigRelationSuperInterface(RelationSuperInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interface_classes[("provider", "app")] = AppSecureConfigBucketInterface


class AppReadyRelationSuperInterface(RelationSuperInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interface_classes[("provider", "app")] = ReadyBucketInterface


class SubordinateReadyRelationSuperInterface(RelationSuperInterface):
    """The relation between the principal and subordinate operators.
    The "ready" status, set by the *requirer*/subordinate indicates
    the the subordinate is ready.

    The relation is typically labelled "<x>-ready" and the interface
    is labelled "unit-ready". See the registry for "relation-unit-ready"."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interface_classes[("requirer", "unit")] = UnitReadyBucketInterface


# register interfaces

interface_registry.register("relation-app-config", AppConfigRelationSuperInterface)
interface_registry.register("relation-app-secure-config", AppSecureConfigRelationSuperInterface)
interface_registry.register("relation-app-ready", AppReadyRelationSuperInterface)
interface_registry.register("relation-subordinate-ready", SubordinateReadyRelationSuperInterface)
