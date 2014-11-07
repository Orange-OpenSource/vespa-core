# -*- coding: utf-8 -*-
#
# Module name: agent_controller_pox.py
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
Agent to wrap Gandalf's controller
"""

from logging import *
from .node import Node
import Queue
import json
import urllib
import urllib2
import json
import sys
import socket
import argparse

mychannel = 'mac_redir'


class Agent_Controller_Pox(Node):

    def __init__(self, name, host, port, master, run=False):
        self.controller_ip = '10.193.163.27'
        super(
            Agent_Controller_Pox,
            self,
        ).__init__(
            name,
            host,
            port,
            master,
            run)
        self.backend = self.desc()

    def _send_controller(self, cmd):
        host = self.controller_ip  # '10.193.163.27' # p-rambo
        port = 7790

        try:
            sock = socket.socket()
            sock.connect((host, port))
            msg = {
                'CHANNEL': '',
                'cmd': 'join_channel',
                'channel': mychannel,
                'json': True,
            }
            sock.send(json.dumps(msg))

            msg = {
                'CHANNEL': mychannel,
                'cmd': cmd,
            }
            sock.send(json.dumps(msg))
        except:
            pass

        try:
            sock.close()
        except:
            pass

        return "Ok"

    def _send_controller_res(self, cmd):
        host = self.controller_ip  # '10.193.163.27' # p-rambo
        port = 7790

        sock = socket.socket()
        sock.connect((host, port))
        msg = {
            'CHANNEL': '',
            'cmd': 'join_channel',
            'channel': mychannel,
            'json': True,
        }
        sock.send(json.dumps(msg))

        msg = {
            'CHANNEL': mychannel,
            'cmd': cmd,
        }
        sock.send(json.dumps(msg))

        cmd_welcome = True
        while cmd_welcome:
            d = sock.recv(4096)
            cmd_welcome = ("welcome" in d)

        try:
            sock.close()
        except:
            pass
        print repr(d)

        return json.loads(d)

    def alert_ip(self, ip, mac):
        self.block_hackers()

    def status_hackers(self):
        self._send_controller('status_hackers')

    def release_hackers(self):
        self._send_controller('release_hackers')

    def block_hackers(self):
        self._send_controller('block_hackers')

    def get_topology(self, cmd='get_topology'):
        return self._send_controller_res(cmd)

    def get_link_stats(self, cmd='get_link_stats'):
        return self._send_controller_res(cmd)
