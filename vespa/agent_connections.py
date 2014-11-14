# -*- coding: utf-8 -*-
#
# Module name: agent_connections.py
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
Counting connections as suggested into:
    http://www.linuxjournal.com/content/back-dead-simple-bash-complex-ddos

SynFlood
https://raw.github.com/arthurnn/SynFlood/master/synflood
"""

import socket
from .log_pipe import *
from threading import Thread
import subprocess
from .node import Node
from .agent import Agent
import Queue
import os
import psutil

# End Flag
EOT_FLAG = "EndOfTransmission"
LIST_ITEM_SEPARATOR = ':'
LIST_SEPARATOR = '\r'


class Agent_Connections(Agent):

    def __init__(self, name, host, port, master, run=True):
        # self.proc = None
        super(Agent_Connections, self,).__init__(name, host, port, master, run)
        self.backend = self.desc()
        self.daemonname = "vlc"

    def launch(self):
        import time

        while not self.quitting:
            infos = self.__get_conns()
            addresses = {}
            intruders = []

            for conn in infos:
                if conn.remote_address:
                    addresses[
                        conn.remote_address[0].replace(
                            ":",
                            "").replace(
                            "f",
                            "")] = 0

            for conn in infos:
                if conn.remote_address:
                    addresses[
                        conn.remote_address[0].replace(
                            ":",
                            "").replace(
                            "f",
                            "")] += 1

            for item in addresses:
                intruders.append({'ip': item, 'value': addresses[item]})

            self.sendAlert("ip_connections#%s" % intruders)
            # debug_info("Intruders: %s" % intruders)

            time.sleep(1)

    def _get_conns(self):
        res = []
        for p in psutil.process_iter():
            try:
                res += p.get_connections(kind='inet')
            except:
                continue
        return res

    def _get_conns_lsof(self):
        lines = os.popen('lsof -ni').readlines()

        from subprocess import Popen, PIPE
        p1 = Popen(['lsof', '-ni'], stdout=PIPE)
        p2 = Popen(["grep", "LISTEN"], stdin=p1.stdout, stdout=PIPE)
        output = p2.communicate()[0]
        cols = ("COMMAND     PID USER   FD   TYPE DEVICE SIZE/OFF"
                "NODE NAME").split()
        res = {}

        for l in output.split("\n"):
            d = dict(zip(cols, l.split()))
            if not d:
                continue
            if d['COMMAND'] not in res:
                res[d['COMMAND']] = []
            res[d['COMMAND']].append(d)

        return res
