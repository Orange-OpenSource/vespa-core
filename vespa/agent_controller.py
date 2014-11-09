# -*- coding: utf-8 -*-
#
# Module name: agent_controller.py
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
from .agent import Agent
import Queue
import json
import urllib
import urllib2


class Agent_Controller(Agent):
    """Create an Agent to send a mac address to an OpenFlow controller

    :return: The Agent instance to offer the OpenFlow alert_ip function
    """

    def __init__(self, name, host, port, master, run=False):
        self.controller_ip = "12.0.0.3"
        self.controller_port = 80
        super(Agent_Controller, self,).__init__(name, host, port, master, run)
        self.backend = self.desc()

    def alert_ip(self, ip, mac):
        """Block the mac address on the network

        :param str ip: The IP address or domain of the controller
        :param str mac: The mac address to block on the network
        """
        url = 'http://%s:%s/' % (self.controller_ip, self.controller_port)
        values = {'mac': mac}
        data = urllib.urlencode(values)
        print '!!!!!!!!!!!!!!!!!!!!! Sending mac %s to %s' % (mac, url)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        return "Ok"
