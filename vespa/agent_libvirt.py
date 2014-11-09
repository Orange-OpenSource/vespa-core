# -*- coding: utf-8 -*-
#
# Module name: agent_libvirt.py
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
#
# Available for domains:
# 
# d.ID                  d.injectNMI                  d.resume
# d.OSType              d.interfaceParameters        d.revertToSnapshot
# d.UUID                d.interfaceStats             d.save
# d.UUIDString          d.isActive                   d.saveFlags
# d.XMLDesc             d.isPersistent               d.schedulerParameters
# d.abortJob            d.isUpdated                  d.schedulerParametersFlags
# d.attachDevice        d.jobInfo                    d.schedulerType
# d.attachDeviceFlags   d.jobStats                   d.screenshot
# d.autostart           d.listAllSnapshots           d.sendKey
# d.blkioParameters     d.managedSave                d.sendProcessSignal
# d.blockCommit         d.managedSaveRemove          d.setAutostart
# d.blockInfo           d.maxMemory                  d.setBlkioParameters
# d.blockIoTune         d.maxVcpus                   d.setBlockIoTune
# d.blockJobAbort       d.memoryParameters           d.setInterfaceParameters
# d.blockJobInfo        d.memoryPeek                 d.setMaxMemory
# d.blockJobSetSpeed    d.memoryStats                d.setMemory
# d.blockPeek           d.metadata                   d.setMemoryFlags
# d.blockPull           d.migrate                    d.setMemoryParameters
# d.blockRebase         d.migrate2                   d.setMemoryStatsPeriod
# d.blockResize         d.migrate3                   d.setMetadata
# d.blockStats          d.migrateGetCompressionCache d.setNumaParameters
# d.blockStatsFlags     d.migrateGetMaxSpeed         d.setSchedulerParameters
# d.connect            d.migrateSetCompressionCache d.setSchedulerParametersFlags
# d.controlInfo         d.migrateSetMaxDowntime      d.setVcpus
# d.coreDump            d.migrateSetMaxSpeed         d.setVcpusFlags
# d.create              d.migrateToURI               d.shutdown
# d.createWithFiles     d.migrateToURI2              d.shutdownFlags
# d.createWithFlags     d.migrateToURI3              d.snapshotCreateXML
# d.destroy             d.name                       d.snapshotCurrent
# d.destroyFlags        d.numaParameters             d.snapshotListNames
# d.detachDevice        d.openChannel                d.snapshotLookupByName
# d.detachDeviceFlags   d.openConsole                d.snapshotNum
# d.diskErrors          d.openGraphics               d.state
# d.emulatorPinInfo     d.pMSuspendForDuration       d.suspend
# d.fSTrim              d.pMWakeup                   d.undefine
# d.getCPUStats         d.pinEmulator                d.undefineFlags
# d.hasCurrentSnapshot  d.pinVcpu                    d.updateDeviceFlags
# d.hasManagedSaveImage d.pinVcpuFlags               d.vcpuPinInfo
# d.hostname            d.reboot                     d.vcpus
# d.info                d.reset                      d.vcpusFlags

import socket
from .log_pipe import debug1
from .agent import Agent

# End Flag
EOT_FLAG = "EndOfTransmission"
LIST_ITEM_SEPARATOR = ':'
LIST_SEPARATOR = '\r'


class Agent_Libvirt(Agent):
    # def __init__(self, name, host, port, master, libvirt_host, libvirt_port,
    # libvirt_user):

    def __init__(self, name, host, port, master, run=True):
        super(Agent_Libvirt, self).__init__(name, host, port, master, run)
        self.libvirt_host = host
        self.libvirt_port = 22
        self.libvirt_user = "root"
        self.backend = (
            "libvirt",
            self.libvirt_host,
            self.libvirt_port,
            self.libvirt_user)
        self.have_backend = False

    def launch(self):
        import libvirt
        import sys
        import os
        import time
        import xml.dom.minidom

    def send(self, msg):
        # Preprocessing
        # Default to upper agent
        data = super(Agent_Libvirt, self).send(msg)
        # Postprocessing
        # remote = (self.name, self.libvirt_host, self.libvirt_port)
        # self.sendRemote( remote, data )
        return data

    def __get_dom_name(self, nodeName, conn_local):
        # NEW LIBVIRT FUNCTION!!!
        try:
            return conn_local.lookupByName(nodeName)
        except:
            raise Exception("Cannot find node %s" % nodeName)
        # domains = conn_local.listDomainsID()
        #
        # for domainID in domains:
        #     domConnect = conn_local.lookupByID(domainID)
        #     if domConnect.name() == nodeName:
        #         domNode = domConnect
        #         return domNode
        #
        # raise Exception("Cannot find node %s" % nodeName)

    def cut_link(self, nodeName="arch-poc-win"):
        conn_local = libvirt.open(
            "qemu+ssh://" +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            "/system")
        domNode = self.__get_dom_name(nodeName, conn_local)

        parsed = xml.dom.minidom.parseString(domNode.XMLDesc(0))
        node_interface = parsed.getElementsByTagName("interface")[0]
        link_to_cut = node_interface.getElementsByTagName(
            "target")[0].getAttribute("dev")
        bridge = node_interface.getElementsByTagName(
            "source")[0].getAttribute("bridge")

        # Cutting link
        os.system(
            "ssh " +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            " \"brctl delif " +
            bridge +
            " " +
            link_to_cut +
            "\"")

        return ["Closed link " + link_to_cut +
                " from " + bridge + " for VM " + nodeName]

    def connect_link(self, nodeName="arch-poc-win"):
        conn_local = libvirt.open(
            "qemu+ssh://" +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            "/system")

        domNode = self.__get_dom_name(nodeName, conn_local)

        parsed = xml.dom.minidom.parseString(domNode.XMLDesc(0))

        node_interface = parsed.getElementsByTagName("interface")[0]
        link_to_cut = node_interface.getElementsByTagName(
            "target")[0].getAttribute("dev")
        bridge = node_interface.getElementsByTagName(
            "source")[0].getAttribute("bridge")

        os.system(
            "ssh " +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            " \"brctl addif " +
            bridge +
            " " +
            link_to_cut +
            "\"")

        return ["Connected link " + link_to_cut +
                " to " + bridge + " for VM " + nodeName]

    def migrate(self, nodeName, quarantine, quarantine_user):
        conn_local = libvirt.open(
            "qemu+ssh://" +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            "/system")
        conn_quarantine = libvirt.open(
            "qemu+ssh://" +
            quarantine_user +
            "@" +
            quarantine +
            "/system")
        domNode = self.__get_dom_name(nodeName, conn_local)
        domNode.migrate(
            conn_quarantine,
            libvirt.VIR_MIGRATE_LIVE,
            None,
            None,
            0)
        return ["Migrated VM " + nodeName + " to quarantine"]

    def contains_vm(self, vm):
        try:
            conn_local = libvirt.open(
                "qemu+ssh://" +
                self.libvirt_user +
                "@" +
                self.libvirt_host +
                "/system")
            self.__get_dom_name(vm, conn_local)
            return True
        except Exception:
            return False

    def send_key(self, vm, args):
        conn_local = libvirt.open(
            "qemu+ssh://" +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            "/system")
        wokeup = False
        debug1(
            self.name + ">Waiting for vm %s to wake up on %s" %
            (vm, self.libvirt_host))
        vm_name, vm_host, vm_port = eval(vm)
        while not wokeup:
            try:
                dom = self.__get_dom_name(vm_name, conn_local)
                wokeup = True
            except:
                debug1("Miss")
                continue
        print "sending '%s'" % args
        dom.sendKey(*eval(args))
        return ["Sent keys to the vm %s" % vm_name]

    def restart(self, vm):
        import libvirt
        import sys
        import os
        import time
        import xml.dom.minidom

        conn_local = libvirt.open(
            "qemu+ssh://" +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            "/system")
        vm_name, vm_host, vm_port = eval(vm)
        dom = self.__get_dom_name(vm_name, conn_local)
        dom.create()
        return ["VM %s restarted" % vm_name]

    def restart_hard(self, vm):
        import libvirt
        import sys
        import os
        import time
        import xml.dom.minidom

        conn_local = libvirt.open(
            "qemu+ssh://" +
            self.libvirt_user +
            "@" +
            self.libvirt_host +
            "/system")
        vm_name, vm_host, vm_port = eval(vm)
        dom = self.__get_dom_name(vm_name, conn_local)
        try:
            dom.destroy()
        except:
            pass
        dom.create()
        return ["VM %s restarted (hard)" % vm_name]
