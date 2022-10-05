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


def _get_grgid(group):
    gr = grp.getgrname(group)
    return gr.gr_gid


def _get_pwuid(owner):
    pw = pwd.getpwnam(owner)
    return pw.pw_uid


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

    def save(
        self,
        path,
        mode=None,
        uid=None,
        gid=None,
        owner=None,
        group=None,
        update_mode=False,
        update_owner=False,
        update_uidgid=False,
    ):
        """Save contents to file. Optionally set mode and ownership."""

        if self.nonce == "":
            # nothing ready to save
            return

        if update_uidgid:
            _uid, _gid = self.uid, self.gid
        elif update_owner:
            try:
                _uid = _get_pwuid(self.owner)
                _gid =_get_grgid(self.group)
            except:
                raise Exception("cannot find owner/group")
        else:
            _uid, _gid = None

        try:
            _uid = _uid if uid == None else uid
            _gid = _gid if gid == None else gid
            _uid = _uid if owner == None else _get_pwuid(owner)
            _gid = _gid if group == None else _get_grgid(group)
        except:
            raise Exception("cannot find owner/group")

        _uid = _uid if _uid != None else -1
        _gid = _gid if _gid != None else -1

        # create/update securely
        p = pathlib.Path(path)
        p.touch()

        if -1 not in [_uid, _gid]:
            os.chown(path, _uid, _gid)

        if update_mode or mode != None:
            _mode = mode if mode != None or self.mode
            p.chmod(_mode)

        p.write_bytes(self.data)
