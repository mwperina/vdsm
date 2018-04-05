# Copyright 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#

"""
qemuio - wrapper for qemu-io tool

This module provides helpers for wiritng and verifying qcow2 files data.
"""

from __future__ import absolute_import
from __future__ import division

from vdsm.common import commands
from vdsm.common import cmdutils


class VerificationError(AssertionError):
    pass


def write_pattern(path, format, offset=512, len=1024, pattern=5):
    write_cmd = 'write -P %d %d %d' % (pattern, offset, len)
    cmd = ['qemu-io', '-f', format, '-c', write_cmd, path]
    rc, out, err = commands.execCmd(cmd, raw=True)
    if rc != 0:
        raise cmdutils.Error(cmd, rc, out, err)


def verify_pattern(path, format, offset=512, len=1024, pattern=5):
    read_cmd = 'read -P %d -s 0 -l %d %d %d' % (pattern, len, offset, len)
    cmd = ['qemu-io', '-f', format, '-c', read_cmd, path]
    rc, out, err = commands.execCmd(cmd, raw=True)
    if rc != 0 or err != b"":
        raise cmdutils.Error(cmd, rc, out, err)
    if b"Pattern verification failed" in out:
        raise VerificationError(
            "Verification of volume %s failed. Pattern 0x%x not found at "
            "offset %s"
            % (path, pattern, offset))
