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

import grp
import hashlib
import os
import pathlib
import pwd
import secrets

from hpctinterfaces.base import Interface
from hpctinterfaces.value import Blob, Integer, String


class FileDataInterface(Interface):
    """Holds the contents and metadata for a file."""

    comment = String("")
    checksum = String()
    data = Blob()
    gid = Integer()
    group = String()
    mode = Integer()
    name = String()
    nonce = String()
    owner = String()
    path = String()
    size = Integer()
    uid = Integer()

    def load(self, path, checksum=False):
        """Load file contents and metadata. Optionally, add sha224 checksum."""

        p = pathlib.Path(path)
        if not p.exists():
            raise Exception("path does not exist")

        self.data = data = p.read_bytes()
        if checksum:
            self.checksum = hashlib.sha224(data).hexdigest()
        self.size = len(data)

        self.path = str(p.resolve())
        self.name = p.name
        self.owner = p.owner()
        self.group = p.group()
        stat = p.stat()
        self.mode = stat.st_mode
        self.uid = stat.st_uid
        self.gid = stat.st_gid
        self.nonce = secrets.token_urlsafe()

    def save(self, path, mode=None, user=None, group=None):
        """Save contents to file. Optionally set mode and ownership.

        user (name or uid) and group (name or gid) take integers
        (uid/gid) or strings (owner/group)."""

        if self.nonce == "":
            # nothing ready to save
            return

        try:
            user = user if user != None else -1
            group = group if group != None else -1
            uid = user if type(user) == int else pwd.getpwnam(user).pw_uid
            gid = group if type(group) == int else grp.getgrnam(group).gr_gid
        except:
            raise Exception("cannot find owner/group")

        # create/update securely
        p = pathlib.Path(path)
        p.touch()

        if (uid, gid) != (-1, -1):
            os.chown(path, uid, gid)

        if mode != None:
            p.chmod(mode)

        p.write_bytes(self.data)
