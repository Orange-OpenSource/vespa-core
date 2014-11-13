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
Agent to wrap the POX python SDN controller. It require some modification on
the other side too. You can follow the mac address blocking tutorial on the
POX website.
"""

from logging import *
from .node import Node
from .agent_controller import Agent_Controller
import Queue
import json
import urllib
import urllib2
import json
import sys
import socket
import argparse

mychannel = 'mac_redir'


class Agent_Controller_Pox(Agent_Controller):
    """Flag a mac address as suspicious and gather statistics for local
    links

    :return: The wrapper to the OMN controller
    :rtype: Node
    """

    def __init__(self, name, host, port, master, run=False):
        self.controller_ip = '10.193.163.27'
        self.controller_port = 7790
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
        port = self.controller_port  # 7790

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
        port = self.controller_port

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
        """Block a tuple (ip,mac) with SDN

        :param str IP: The IP to block (for future)
        :param str mac: The associated MAC address (needed)
        :return: The controller response
        :rtype: str
        """
        return self.block_hackers()

    def status_hackers(self):
        """Get the status of a tuple (ip,mac) with SDN

        :return: The controller response
        :rtype: str
        """
        return self._send_controller('status_hackers')

    def release_hackers(self):
        """Release all tuples (ip,mac) with SDN

        :return: The controller response
        :rtype: str
        """
        return self._send_controller('release_hackers')

    def block_hackers(self):
        """Block a MAC address with SDN

        :param str mac: The associated MAC address
        :return: The controller response
        :rtype: str
        """
        return self._send_controller('block_hackers')

    def get_topology(self, cmd='get_topology'):
        """Get the current topology of the SDN network

        :param str cmd: The POX URL to grab the topology
        :return: The list of nodes and links detected
        :rtype: dict
        """
        return self._send_controller_res(cmd)

    def get_link_stats(self, cmd='get_link_stats'):
        """Get links statistics over the pox controller

        :param str cmd: The POX URL to grab the links statistics
        :return: The controller response
        :rtype: str
        """
        return self._send_controller_res(cmd)
