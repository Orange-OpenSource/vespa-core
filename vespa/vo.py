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
        self.recv_bytes = []
        self.trans_bytes = []
        self.alerts = []
        self.ip_connections = []
        self.under_ddos = False
        self.time_last_attack = 0
        super(VO, self,).__init__(name, host, port, None, run)
        self.register_alert_handler(self.alert)
        self.model = master

    def get_trans_bytes(self):
        return [y['bytes'] - x['bytes']
                for x, y in zip(self.trans_bytes, self.trans_bytes[1:])][-40:]

    def get_recv_bytes(self):
        return [y['bytes'] - x['bytes']
                for x, y in zip(self.recv_bytes, self.recv_bytes[1:])][-40:]

    def get_next_recv_bytes(self):
        if len(self.recv_bytes) > 2:
            item = self.recv_bytes[-1]['bytes'] - self.recv_bytes[-2]['bytes']
        else:
            item = 0
        return item

    def get_next_trans_bytes(self):
        if len(self.trans_bytes) > 2:
            item = self.trans_bytes[-1]['bytes'] - \
                self.trans_bytes[-2]['bytes']
        else:
            item = 0
        return item

    def get_ip_connections(self):
        return self.ip_connections

    def get_alerts(self):
        return self.alerts[::-1]

    def get_topology(self):
        # agent_controller = self.findNode("Agent_Controller_Pox")
        # return self.sendRemote(agent_controller, "get_topology|")
        return []

    def get_link_stats(self):
        # agent_controller = self.findNode("Agent_Controller_Pox")
        # return self.sendRemote(agent_controller, "get_link_stats|")
        return []

    def alert(self, msg):
        debug_comm_len("[%s] Received alert : %s" % (self.name, msg))
        # debug2 = self.view_update
        # print "repr:" + repr(msg)
        source = msg.split("|")[1].split(">")[-2]
        message = msg.split(">")[-1]
        # Global logger
        self.alerts.append(msg)
        #
        # New node registered
        #
        if "archi=" in message:
            self.sendRemotef(
                self.model, "alert|%s>%s" %
                (self.name, msg.split("|")[1]))
        #
        # Source agent bandwidth
        #
        if source == "Agent_Bandwidth":
            if "recv_bytes" in message:
                args = message.split('#')
                tm = args[1]
                r = args[2]
                self.recv_bytes.append({'time': float(tm), 'bytes': float(r)})
                if len(self.recv_bytes) > 50:
                    self.recv_bytes.pop(0)

                # self.sendRemotef(self.model, "alert|%s>recv_bytes#%s#%s" %
                # (self.name, tm, r))
            elif "trans_bytes" in message:
                args = message.split('#')
                tm = args[1]
                t = args[2]
                self.trans_bytes.append({'time': float(tm), 'bytes': float(t)})
                if len(self.trans_bytes) > 50:
                    self.trans_bytes.pop(0)

                # self.sendRemotef(self.model, "alert|%s>trans_bytes#%s#%s" %
                # (self.name, tm, r))
            else:
                self.sendRemotef(
                    self.model, "alert|%s>Unexpected alert: %s" %
                    (self.name, message))
        elif source == "Agent_Connections":
            if "ip_connections" in message:
                # debug_info("Got %s" % message)
                args = message.split('#')
                a = eval(args[1])
                if len(self.ip_connections) > 0:
                    for sip in self.ip_connections:
                        sip['value'] = 0
                for ipobj in a:
                    if len(self.ip_connections) == 0 or ipobj['ip'] not in [
                            selfip['ip'] for selfip in self.ip_connections]:
                        self.ip_connections.append(ipobj)
                    else:
                        for sip in self.ip_connections:
                            if sip['ip'] == ipobj['ip']:
                                sip['value'] = ipobj['value']
                debug_info("Analyzing %s" % self.ip_connections)
                # Reaction
                new_ddos = False
                all_good = True
                for ipobj in self.ip_connections:
                    if ipobj['value'] > 100:
                        new_ddos = True
                        all_good = False
                    elif (ipobj['value'] > 20 and
                          (time.time() - self.time_last_attack) > 30):
                        all_good = False

                if new_ddos and not self.under_ddos:
                    debug_info("DDos detected, slow mode")
                    if (time.time() - self.time_last_attack) > 30:
                        self.time_last_attack = time.time()
                        self.under_ddos = True
                        agent_bp = self.findNode("Agent_Bandwidth")
                        # agent_controller = self.findNode(
                        # "Agent_Controller_Pox")
                        agent_controller = self.findNode(
                            "Agent_Controller_Floodlight")
                        mac = self.sendRemote(agent_bp, 'get_mac|')
                        self.sendRemotef(
                            agent_controller, "alert_ip|%s#%s" %
                            (ipobj['value'], mac))
                        debug_info(
                            "DDos detected for %s, forwarding %s" %
                            (ipobj['value'], mac))

                elif all_good and self.under_ddos:
                    debug_info("DDos stopped, slow mode")
                    if (time.time() - self.time_last_attack) > 120:
                        self.time_last_attack = time.time()
                        self.under_ddos = False
                        agent_bp = self.findNode("Agent_Bandwidth")
                        # agent_controller = self.findNode(
                        # "Agent_Controller_Pox")
                        agent_controller = self.findNode(
                            "Agent_Controller_Floodlight")
                        mac = self.sendRemote(agent_bp, 'get_mac|')
                        self.sendRemotef(
                            agent_controller, "alert_ip|%s#%s" %
                            (ipobj['value'], mac))
                        debug_info(
                            "DDos stopped for %s, normal traffic for %s" %
                            (ipobj['value'], mac))
            else:
                self.sendRemotef(
                    self.model, "alert|%s>Unexpected alert: %s" %
                    (self.name, message))
