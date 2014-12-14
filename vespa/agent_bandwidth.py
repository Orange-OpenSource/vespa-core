# -*- coding: utf-8 -*-
#
# Module name: agent_bandwidth.py
# Version:     1.0
# Created:     29/04/2014 by Aurélien Wailly <aurelien.wailly@orange.com>
#
# Copyright (C) 2010-2014 Orange
#
# This file is part of VESPA.
#
# VESPA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation version 2.1.
#
# VESPA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with VESPA.  If not, see <http://www.gnu.org/licenses/>.
"""
Agent wrapper around /proc/dev/net to filter an interface statistics. The
interface *eth0* is used as default.
"""

import socket
from logging import *
from threading import Thread
import subprocess
from node import Node
from agent import Agent
import Queue
import fcntl
import socket
import struct

# End Flag
EOT_FLAG = "EndOfTransmission"
LIST_ITEM_SEPARATOR = ':'
LIST_SEPARATOR = '\r'


class Agent_Bandwidth(Agent):
    """Provide a wrapper around Linux interfaces /proc files. The Agent can
    extract information of specific interfaces, i.e. eth0 or lo.

    :return: The agent to grab informations
    :rtype: Node
    """

    def __init__(self, name, host, port, master, run=True):
        # self.proc = None
        self.devfile = "/proc/net/dev"
        self.iface = "eth0"
        super(Agent_Bandwidth, self,).__init__(name, host, port, master, run)
        self.backend = self.desc()

    def launch(self):
        """Send _recv_bytes_ and _trans_bytes_ back to the master every
        second
        """

        import time

        while not self.quitting:
            infos = self._get_ifaces()
            tm = time.time()

            r = infos[self.iface]['recv_bytes']
            # self.sendRemote(self.master, "alert|%s>recv_bytes#%s#%s" %
            # (self.name, tm, r), needack=False)
            self.sendAlert("recv_bytes#%s#%s" % (tm, r))

            t = infos[self.iface]['trans_bytes']
            # self.sendRemote(self.master, "alert|%s>trans_bytes#%s#%s" %
            # (self.name, tm, t), needack=False)
            self.sendAlert("trans_bytes#%s#%s" % (tm, t))

            time.sleep(1)

    def _get_ifaces(self):
        """Function parsing the /proc/net/dev file and feeding a table

        :return: The table mapping the device file
        :rtype: list
        """

        lines = open(self.devfile, "r").readlines()

        columnLine = lines[1]
        _, receiveCols, transmitCols = columnLine.split("|")
        receiveCols = map(lambda a: "recv_" + a, receiveCols.split())
        transmitCols = map(lambda a: "trans_" + a, transmitCols.split())

        cols = receiveCols + transmitCols

        faces = {}
        for line in lines[2:]:
            if line.find(":") < 0:
                continue
            face, data = line.split(":")
            faceData = dict(zip(cols, data.split()))
            faces[face.strip()] = faceData

        return faces

    def get_mac(self):
        """Grab the mac address of the class defined _self.iface_

        :return: The string containing the mac address, colon separated
        :rtype: str
        """

        return self._get_mac(self.iface)

    def _get_mac(self, ifname):
        """Send an ioctl to recover the mac address of a specific interface

        :return: The string containing the mac address, colon separated
        :rtype: str
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(
            s.fileno(),
            0x8927,
            struct.pack(
                '256s',
                ifname[
                    :15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
