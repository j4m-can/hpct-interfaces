#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import os.path, sys

sys.path.insert(0, os.path.realpath("../../lib"))

from hpctinterfaces.ext.file import FileDataInterface
from hpctinterfaces import interface_registry
from hpctinterfaces.relation import RelationSuperInterface, UnitBucketInterface
from hpctinterfaces.value import String


class UnitSendfileRelationSuperInterface(RelationSuperInterface):
    class FileUnitInterface(UnitBucketInterface):

        file = FileDataInterface()

    class AckUnitInterface(UnitBucketInterface):

        nonce = String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.interface_classes[("provider", "unit")] = self.FileUnitInterface
        self.interface_classes[("requirer", "unit")] = self.AckUnitInterface


interface_registry.register("relation-unit-sendfile", UnitSendfileRelationSuperInterface)

if __name__ == "__main__":
    siface = UnitSendfileRelationSuperInterface(None, "sendfile")
    print(siface)

    fileif = siface.interface_classes[("provider", "unit")](None, "sendfile", "unit", mock=True)
    ackif = siface.interface_classes[("requirer", "unit")](None, "sendfile", "unit", mock=True)

    print(fileif.__dict__)
    print(fileif.__class__)
    print(fileif._prefix)

    print(ackif)
    print(ackif.__class__)
    print(ackif._prefix)
