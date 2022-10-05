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

    def save(self, path, update_mode=False, update_owner=False, update_uidgid=False):
        """Save contents to file. Optionally set mode and ownership."""

        if self.nonce == "":
            # nothing ready to save
            return

        if update_uidgid or update_owner:
            if update_uidgid:
                uid, gid = self.uid, self.gid
            else:
                try:
                    pw = pwd.getpwnam(self.owner)
                    gr = grp.getgrnam(self.group)
                    uid, gid = pw.pw_uid, gr.gr_gid
                except:
                    raise Exception("cannot find owner/group")
        else:
            uid, gid = None

        # create/update securely
        p = pathlib.Path(path)
        p.touch()
        if None not in [uid, gid]:
            os.chown(path, uid, gid)
        if update_mode:
            p.chmod(self.mode)
        p.write_bytes(self.data)
