# -*- coding: utf-8 -*-
#
# Module name: model.py
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
Model
"""
from log_pipe import *
import socket
from node import Node
from configobj import ConfigObj
import time

localhost = socket.gethostbyname(socket.gethostname())
config_filename = "config.ini"


class Model(Node):
    def __init__(self):
        super(Node, self,).__init__("model", localhost, 4100, None)
        self.name = "model"

        config = ConfigObj("%s" % config_filename)
        self.config = config
        debug_init("Loaded configuration from %s" % config_filename)

        # Config file modifications
        for obj in config:
            if 'Type' not in obj:
                config[obj]['Type'] = obj

        # Looking for VO (mandatory)
        vo_object = self.find_vo(config)
        debug_init("Found VO")

        if vo_object is None:
            debug5("%s: Unable to find VO, exiting" % self.name)
            raise Exception("Model %s need a VO" % self.name)

        # Instanciating object
        self.create_object_instance(config, vo_object, self)

    def find_vo(self, config):
        """
        Return VO object from config file

        One and only one VO
        """
        vo_object = None

        debug_init("%s: Finding VO" % self.name)
        for obj in config:
            if config[obj]['Type'] == 'VO':
                debug_init("%s: Found VO" % self.name)
                vo_object = obj

        return config[vo_object]

    def create_object_instance(self, config, obj, master):
        debug_init("Creating object: %s" % obj['Type'])
        obj_location = config[obj['Location']]['Interfaces']

        # is_local =
        #    obj_location == config[config['VO']['Location']]['Interfaces']
        is_local = obj['Location'] == socket.gethostname()

        debug_init("Object is local: [%s == %s] %s" %
                   (obj['Location'], socket.gethostname(), is_local))

        try:
            obj_instance = eval(obj['Type'])(obj['Type'],
                                             obj_location, int(obj['Port']),
                                             master.desc(), is_local)
        except NameError:
            debug5("Agent into model.py ? Anyway, trying auto import!")
            a = __import__(obj['Type'].lower(), fromlist=[obj['Type']])
            b = getattr(a, obj['Type'])
            obj_instance = b(obj['Type'], obj_location, int(obj['Port']),
                             master.desc(), is_local)

        debug_init("Registering object")
        """
        if master == self:
            self.register(obj['Type'], obj_location, obj['Port'])
        else:
            """
        if is_local:
            self.sendRemoteWake(master.desc(), "register|%s" % obj_instance)

        debug_init("Adding slaves")
        # Adding slaves to object
        for slave in config:
            debug_init("-> %s [%s]" % (config[slave], obj['Type']))
            if 'Master' in config[slave]:
                debug_init("   %s" % config[slave]['Master'])
            if ('Master' in config[slave]
                    and config[slave]['Master'] == obj['Type']):
                self.create_object_instance(config, config[slave],
                                            obj_instance)

    def sendRemoteWake(self, remote, msg):
        """
        Force sending content to a remote host. Loop until it is done
        """
        while True:
            # self.sendRemote(remote, msg)
            # return
            try:
                debug_comm("Waiting for %s" % repr(remote))
                self.sendRemote(remote, msg)
                return
            except IOError:
                time.sleep(2)
                continue

    def findNode(self, name):
        """
        Return a tuple if the node "name" is found, raise an Exception
        otherwise.
        TODO: Refactor (3x)
        """
        for vo in self.slaves:
            vo_name, vo_host, vo_port = vo
            if vo_name == name:
                return vo
            vo_slaves_raw = self.sendRemote(vo, "list_slaves|")
            try:
                vo_slaves = eval(vo_slaves_raw)
            except SyntaxError:
                vo_slaves = []
            for ho in vo_slaves:
                ho_name, ho_host, ho_port = ho
                if ho_name == name:
                    return ho
                ho_slaves_raw = self.sendRemote(ho, "list_slaves|")
                try:
                    ho_slaves = eval(ho_slaves_raw)
                except SyntaxError:
                    ho_slaves = []
                for agent in ho_slaves:
                    agent_name, agent_host, agent_port = agent
                    if agent_name == name:
                        return agent
        raise Exception("Node %s not present in Model %s." % (name, self.name))
