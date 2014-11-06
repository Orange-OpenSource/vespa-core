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
Most basic inherited class for a simple Node

Default config without backend
"""

import socket
from logging import *
from threading import Thread
import subprocess
from .node import Node
import Queue
import fcntl
import socket
import struct

# End Flag
EOT_FLAG = "EndOfTransmission"
LIST_ITEM_SEPARATOR = ':'
LIST_SEPARATOR = '\r'


class Agent_Bandwidth(Node):

    def __init__(self, name, host, port, master, run=True):
        # self.proc = None
        self.devfile = "/proc/net/dev"
        self.iface = "eth0"
        super(Agent_Bandwidth, self,).__init__(name, host, port, master, run)
        self.backend = self.desc()

    def launch(self):
        import time

        while not self.quitting:
            infos = self.__get_ifaces()
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

    def __get_ifaces(self):
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
        return self.__get_mac(self.iface)

    def __get_mac(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(
            s.fileno(),
            0x8927,
            struct.pack(
                '256s',
                ifname[
                    :15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
