# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctinterfaces/ext/file.py

"""Interface to support File/File data.

To use:
    class MyInterface(UnitInterface):
        configfile = FileDataInterface()

    To load:
        iface = MyInterface()
        iface.load("/etc/hosts")

    To save (to the same path as loaded from):
        iface = MyInterface()
        iface.save(iface.path)
"""

import hashlib
import os
import pathlib
import secrets

from hpctinterfaces.base import Interface
from hpctinterfaces.value import Blob, Integer, String


class FileDataInterface(Interface):
    """Holds the contents and metadata for a file."""

    comment = String("")
    data = Blob()
    gid = Integer()
    group = String()
    md5sum = String()
    mode = Integer()
    name = String()
    nonce = String()
    owner = String()
    path = String()
    uid = Integer()

    def load(self, path, checksum=False):
        """Load file contents and metadata. Optionally, add md5 checksum."""

        p = pathlib.Path(path)
        if not p.exists():
            raise Exception("path does not exist")

        self.data = data = p.read_bytes()
        if checksum:
            self.md5sum = hashlib.md5(data).hexdigest()

        self.path = str(p.resolve())
        self.name = p.name
        self.owner = p.owner()
        self.group = p.group()
        stat = p.stat()
        self.mode = stat.st_mode
        self.uid = stat.st_uid
        self.gid = stat.st_gid
        self.nonce = secrets.token_urlsafe()

    def save(self, path, update_mode=False, update_owner=False):
        """Save contents to file. Optionally set mode and ownership."""

        if self.nonce == "":
            # nothing ready to save
            return

        p = pathlib.Path(path)
        p.write_bytes(self.data)
        if update_mode:
            p.chmod(self.mode)
        if update_owner:
            os.chown(path, self.uid, self.gid)
