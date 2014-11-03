# -*- coding: utf-8 -*-
# 
# Module name: vo.py
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
Vertical orchestrator
"""
from log_pipe import *
from node import *
import sys
import time

class VO(Node):
    def __init__(self, name, host, port, master, run=True):
        super(VO, self,).__init__(name, host, port, None, run)
        self.register_alert_handler(self.alert)
        self.model = master

    def alert(self, msg):
        debug_comm_len("[%s] Received alert : %s" % (self.name, msg))
        #print "repr:" + repr(msg)
        source = msg.split("|")[1].split(">")[-2]
        message = msg.split(">")[-1]
        #
        # New node registered
        #
        if "archi=" in message:
            self.sendRemotef(self.model, "alert|%s>%s" % (self.name, msg.split("|")[1]))

        if source == "Agent_Demo":
            if "new_line" in message:
                args = message.split('#')
                line = args[1]

		#agent_demo = self.findNode("Agent_Demo")
		#self.sendRemotef(agent_controller, "alert_ip|%s#%s" % (ipobj['value'], mac))
		debug_info("Alert received: %s" % line)
            else:
                self.sendRemotef(self.model, "alert|%s>Unexpected alert: %s" % (self.name, message))
