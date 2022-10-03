# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/store.py

from .base import NoValue


class BucketStore:
    """Data store for relation data bucket."""

    def __init__(self, charm, relname, bucketkey, relation_id=None):
        self.charm = charm
        self.relname = relname
        self.bucketkey = bucketkey
        self.relation_id = relation_id

    def __delitem__(self, key):
        """According to `RelationDataContent.__delitem__()."""
        self[key] = ""

    def __getitem__(self, key):
        key = key.replace("_", "-")
        relation = self.get_relation()
        if relation:
            value = relation.data[self.bucketkey].get(key, NoValue)
            if value == NoValue:
                raise KeyError
            return value

    def __setitem__(self, key, value):
        key = key.replace("_", "-")
        for relation in self.get_relations():
            relation.data[self.bucketkey].update({key: value})

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            return default

    def get_relation(self, relation_id=None):
        if relation_id == None:
            relation_id = self.relation_id
        return self.charm.model.get_relation(self.relname, relation_id)

    def get_relations(self):
        if self.relation_id != None:
            relations[self.get_relation()]
        else:
            relations = self.charm.model.relations.get(self.relname, [])
        return relations


class MockBucketStore(BucketStore):
    """Minimal mock for BucketStore."""

    def __init__(self, charm, relname, bucketkey, relation_id, *args, **kwargs):
        super().__init__(charm, relname, bucketkey, relation_id, *args, **kwargs)

        self.data = {
            "app": {},
            "unit": {},
        }

    def get_relation(self, relation_id=None):
        return self

    def get_relations(self):
        return [self]
