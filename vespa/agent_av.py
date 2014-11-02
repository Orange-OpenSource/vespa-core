# -*- coding: utf-8 -*-
# 
# Module name: agent_av.py
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
Agent representation
"""
import socket
from log_pipe import debug1
from agent import Agent

class Agent_AV(Agent):
    def __init__(self, name, host, port, master, vm):
        super(Agent_AV, self).__init__(name, host, port, master)
        self.have_backend = True
        self.is_backend_reachable = True
        self.backend = vm

    def send(self, msg):
        command = msg.split("|")[0]
        # Preprocessing
        if command == 'import_list':
            predefined_list = []
            for item, status in predefined_list:
                msg += item + "#"
        elif command == 'register_handler':
            msg += '%s#%s#' % ( self.host, self.port )
        # Normal socket connection
        if self.is_backend_reachable:
            data = super(Agent_AV, self).send(msg)
        # Hypervisor sysrq
        else:
            if command == 'clean_image':
                # conn_local = libvirt.open("qemu+ssh://" + self.agent_hy.host + "/system")
                # dom = self.agent_hy.__get_dom_name(self.vm, conn_local)
                # dom.sendKey(8, 10, [ 0x12, 0x42 ], 2, 0)
                args = (8, 10, [ 0x12, 0x42 ], 2, 0)
                data = self.sendRemote(self.agent_hy, "send_key|%s#%s" % (self.backend, args) )
            else:
                data = super(Agent_AV, self).send(msg)
                # data = [ "Unsupported sysrq method" ]
        # self.sendRemote(master, data)
        return data

    def dump_analyzed_file_list(self):
        try:
            agent_vm = self # self.findAgent('agent_av')
            raw_msg = agent_vm.send("dump_list|")[0]
            command = raw_msg.split('|')[0]
            title_list = raw_msg.split('|')[1]
            file_list_raw = raw_msg.split('|')[2]
            file_list = []
            file_list.append( (title_list.split(LIST_ITEM_SEPARATOR)[0], title_list.split(LIST_ITEM_SEPARATOR)[1]) )
            # It can be an error
            if LIST_SEPARATOR not in file_list_raw:
                return [ file_list_raw ]
            # Otherwise, it can be a list
            for scan_result in file_list_raw.split(LIST_SEPARATOR):
                # It can be an error, last line is messy
                if ':' not in scan_result:
                    continue
                name = ":".join(scan_result.split(LIST_ITEM_SEPARATOR)[0:2]).strip()
                status = scan_result.split(LIST_ITEM_SEPARATOR)[2].strip()
                file_list.append( (name, status) )
            return file_list
        except Exception as e:
            debug1("[-] Error: %s" % (e))

    def isolate_warning(self, vm):
        self.is_backend_reachable = False
        self.agent_hy = eval(vm)

    def connect_warning(self):
        self.is_backend_reachable = True
        self.agent_hy = False
