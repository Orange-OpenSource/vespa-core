# -*- coding: utf-8 -*-
#
# Module name: agent_controller_floodlight.py
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
Agent to wrap Gandalf's controller. Based on floodlight, it can be a nice
start for a full API against floodlight.
"""

from logging import *
from agent_controller import Agent_Controller
import Queue
import urllib2
import json
import random


class Agent_Controller_Floodlight(Agent_Controller):
    """Flag a mac address as suspicious and gather statistics for local
    links

    :return: The wrapper to the OMN controller
    :rtype: Node
    """

    def __init__(self, name, host, port, master, run=False):
        self.controller_ip = "12.0.0.20:9999"
        # self.floodlight = "12.0.0.10:8080"
        self.floodlight = "10.193.163.27:8080"
        super(
            Agent_Controller_Floodlight,
            self,
        ).__init__(
            name,
            host,
            port,
            master,
            run)
        self.backend = self.desc()

    def _send_controller(self, msg):
        return self._send_url(self.controller_ip, msg)

    def _send_floodlight(self, msg):
        return self._send_url(self.floodlight, msg)

    def _send_url(self, urlmsg, msg):
        url = 'http://%s/%s' % (urlmsg, msg)
        response = urllib2.urlopen(url)
        the_page = response.read()
        return the_page

    def alert_ip(self, ip, mac):
        """Block a tuple (ip,mac) with SDN

        :param str IP: The IP to block (for future)
        :param str mac: The associated MAC address (needed)
        :return: The controller response
        :rtype: str
        """
        return self.block_hackers(mac)

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

    def block_hackers(self, mac):
        """Block a MAC address with SDN

        :param str mac: The associated MAC address
        :return: The controller response
        :rtype: str
        """
        return self._send_controller('?mac=%s' % mac)

    def get_topology(self, cmd='wm/topology/switchclusters/json'):
        """Get the current topology of the SDN network

        :param str cmd: The floodlight URL to grab the topology
        :return: The list of nodes and links detected
        :rtype: dict
        """
        topo = self._send_controller(cmd)
        jt = json.loads(topo)

        nodes = []
        for link in jt:
            if link["src-switch"] not in nodes:
                nodes.append({'id': link["src-switch"]})
            if link["dst-switch"] not in nodes:
                nodes.append({'id': link["dst-switch"]})

        edges = []
        for e in jt:
            no = [f['id'] for f in nodes]
            id1 = [i for i, x in enumerate(no) if x == e["src-switch"]][0]
            id2 = [i for i, x in enumerate(no) if x == e["dst-switch"]][0]
            edges.append({"source": id1,
                          "target": id2,
                          "value": random.randint(0, 200)})
        # print self.switches,switches
        # print self.links,edges

        return {'links': edges, 'nodes': nodes}

    def get_link_stats(self, cmd='wm/topology/links/json'):
        """Get links statistics over the floodlight controller

        :param str cmd: The floodlight URL to grab the links statistics
        :return: The controller response
        :rtype: str
        """
        links = self._send_controller(cmd)
        return links
