# -*- coding: utf-8 -*-
#
# Module name: node.py
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
Most basic inherited class for a simple Node

Default config without backend

Pthread is used as Profiler wrapper

If you do not need profiling you may replace the PThread class with:
    class Node(Thread):

INTERNALS:

"""

import socket
from log_pipe import *
from threading import Thread
import cProfile
import select
import subprocess
import time
import hashlib
import json
from Crypto.Cipher import AES
from Crypto import Random
import base64
import random
from aes_gcm import AES_GCM
import sys

# End Flag
EOT_FLAG = "EndOfTransmission"
LIST_ITEM_SEPARATOR = ':'
LIST_SEPARATOR = '\r'
RECV_LENGTH = 4096


class PThread(Thread):
    def __init__(self, name, host, port, master, run=True):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.method_list = [method for method in dir(self)
                            if callable(getattr(self, method))
                            and method not in dir(Thread)]
        self.slaves = []
        self.master = master
        self.alert_handlers = []
        self.have_backend = False
        self.is_backend_reachable = False
        self.quitting = False
        self.threads = []
        self.interface_threads = []
        # self.key = int("VESPAVESPAVESPA1".encode("hex"))
        self.key = "VESPA"*6 + "12"
        if run:
            self.start()
            t = ThreadWorker(target=self.launch)
            # self.launch()
            self.threads.append(t)
            t.start()
        self.name = name
        self.current_links = []
        self.socket_counter = {}
        self.wsocket_counter = {}

    def __str__(self):
        return "%s#%s#%s" % (self.name, self.host, self.port)

    def desc(self):
        """
        Return the tuple representing a node
        """
        return (self.name, self.host, self.port)

    def list_slaves(self):
        """
        Return self.slaves
        """
        return self.slaves

    def get_backend(self):
        """
        Return the backend registered on initialization (i.e. Resource)
        """
        return self.backend

    def register(self, name, host, port):
        debug5("[%s] Added slave %s" % (self.name, name))
        if (name, host, int(port)) not in self.slaves:
            self.slaves.append((name, host, int(port)))
        else:
            cl = []
            for r, s in self.current_links:
                if r == (name, host, int(port)):
                    s.close()
                else:
                    cl.append((r, s))
            self.current_links = cl
        if self.master:
            self.sendRemotef(self.master,
                             'alert|%s>archi=New slave' % self.name)

    def destroy(self):
        """
        Destroy all slaves
        """
        if self.quitting is False:
            self.quitting = True
            for r, s in self.current_links:
                # s.send("destroy|%s" % EOT_FLAG)
                self.socket_counter[r] += 1
                self.sendSocket(s, r, "destroy|")
            for slave in self.slaves:
                self.sendRemotef(slave, "destroy|")
            # WARNING, DESTROY ALL!
            if self.master:
                self.sendRemotef(self.master, "destroy|")

    def register_alert_handler(self, handler):
        debug5("[%s] Added alert handler %s" % (self.name, handler))
        self.alert_handlers.append(handler)

    def findNode(self, name):
        for slave in self.slaves:
            slave_name, slave_host, slave_port = slave
            if slave_name == name:
                return slave
            node_results = self.sendRemote(slave, "findNode|%s" % name)
            if node_results != 'None':
                return eval(node_results)
        return 'None'
        # raise Exception("Node %s not present in VO %s." % (name, self.name))

    def send(self, msg):
        """
        Provide an entry to current node functions.
        """
        # Handling overloaded methods
        for method in self.method_list:
            # if msg == method:
            #    debug1("BOUNGA")
            #    return self.__getattribute__(method)()
            if self.__get_method(msg) == method:
                arguments = self.__get_arguments_list(msg)
                if len(arguments) == 1 and len(arguments[0]) == 0:
                    return self.__getattribute__(method)()
                else:
                    return self.__getattribute__(method)(*arguments)
        data = ["help#"]
        if self.have_backend and self.is_backend_reachable:
            # Connection to backend
            # For C : data = [ self.sendRemote(self.backend, msg) ]
            data = eval(self.sendRemote(self.backend, msg))
            debug_comm('Received 1 %s' % repr(data))
        if msg == 'help|':
            for method in self.method_list:
                if (not method[0:1] == '_'
                        and method not in data[0]
                        and not method == "send"):
                    data[0] += method + '#'
        return data

    def sendAlert(self, msg):
        """
        Wrapper for sendRemote with alert formatting.

        See "sendRemote" for arguments description and returns
        """
        return self.sendRemotef(self.master, "alert|%s>%s" % (self.name, msg))

    def sendRemotef(self, remote, msg):
        """
        Wrapper for sendRemote with needack=False

        See "sendRemote" for arguments description and returns
        """
        return self.sendRemote(remote, msg, needack=False)

    def sendRemote(self, remote, msg, needack=True):
        """
        Send a message to a node (remote) using the node.desc() string.
        This function deals with sockets directly.

        Default behavior is to wait data as acknowledgement (needack).
        It is only modified for messages needing fast delivery and processing
        such as alerts.
        """
        name, host, port = remote
        while 1:
            try:
                debug_comm_len("[%s] Trying to send: %s -> %s" %
                               (self.name, remote, msg))
                # Trying to reuse socket (reducing socket number)
                if remote not in [r for r, _ in self.current_links]:
                    debug_comm("[%s] Creating socket" % self.name)
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.current_links.append((remote, s))
                    # print '%s:%s' % (host, port)
                    s.connect((host, port))
                    self.socket_counter[remote] = 0
                else:
                    debug_comm("[%s] Socket exist, reusing" % self.name)
                    s = [s for r, s in self.current_links if remote == r][0]
                    debug_comm("[%s] >> %s" % (self.name, str(s)))
                    self.socket_counter[remote] += 1
                """
                This part is in beta, we will move toward AES GCM/EAX
                """
                self.sendSocket(s, remote, msg)
                data = ""
                if needack:
                    debug_comm("[%s] Waiting for recv and EOT_FLAG" %
                               self.name)
                    while EOT_FLAG not in data:
                        data += s.recv(RECV_LENGTH)
                    data = data.replace(EOT_FLAG, "")
                    # s.shutdown(socket.SHUT_RDWR)
                    # s._sock.close()
                    # s.close()
                    debug_comm('[%s] Received %s' % (self.name, repr(data)))
                return data
            except socket.error, (errno, strerror):
                if errno in [32, 104, 111, 10057, 10061]:
                    debug_comm("[%s] Connection reset by peer, recreating" %
                               self.name)
                    # Handle double faults
                    if remote in [r for r, _ in self.current_links]:
                        self.current_links.remove((remote, s))
                    # FIXME
                    time.sleep(1)
                    # Needed to reset counters on node lost/creation
                    # self.wsocket_counter[uniqid] = 0
                elif errno in [113]:
                    self.sendRemotef(self.master, "alert|%s>down#%s" %
                                     (self.name, repr(remote)))
                    return 'None'
                else:
                    debug_comm("[-] [%s] Error %s [%s][%s]" %
                               (self.name, msg, errno, strerror))
                    raise
                    return []

    def sendSocket(self, s, remote, msg):
        """
        Handle the socket (s.send) message and encryption routines.
        """
        iv = "%016i" % self.socket_counter[remote]
        cmsg, hmsg = self.__encrypt(msg, iv)
        debug_crypto("[%s] b64ing msg" % self.name)
        cmsg = base64.b64encode(cmsg)
        debug_crypto("[%s] Encrypt msg :: %s :: %s :: %s" %
                     (self.name, remote, iv, cmsg))
        hmsg = base64.b64encode(hmsg)
        jsonmsg = {"cmsg": cmsg, "checksum": hmsg}
        debug_comm("[%s] Sending msg" % self.name)
        s.send("%s%s" % (json.dumps(jsonmsg), EOT_FLAG))

    def worker(self, conn):
        """
        Handle socket reception job.
        """
        data_recv = ""
        uniqid = random.randint(0, 200000)
        self.wsocket_counter[uniqid] = 0
        while not self.quitting:
            debug_comm("[%sW%s] Worker waiting datas (prev:%s)" %
                       (self.name, uniqid, data_recv))
            data_prev = ""
            while EOT_FLAG not in data_recv:
                data_recv += conn.recv(RECV_LENGTH)
                debug_comm_detail('[%sW%s] Daemon Received %s' %
                                  (self.name, uniqid, repr(data_recv)))
                # FIXME Weird behaviour when killing other side, loop with ''
                if data_recv == data_prev:
                    conn.close()
                    # self.quitting = True
                    return
                data_prev = data_recv
            # Fail if multiple messages into "data"
            # data = data.replace(EOT_FLAG, "")
            for data in data_recv.split(EOT_FLAG)[0:-1]:
                debug_comm_len('[%sW%s] Parsing data %s' %
                               (self.name, uniqid, repr(data)))
                # Checking integrity
                jsonmsg = json.loads(data)
                #    debug_comm('[%sW%s] Integrity error for json message,
                #               skipping data ' % (self.name, uniqid))
                #    continue
                # Parse message
                iv = "%016i" % self.wsocket_counter[uniqid]
                cmsg = base64.b64decode(jsonmsg['cmsg'])
                hmsg = base64.b64decode(jsonmsg['checksum'])
                data = self.__decrypt(cmsg, iv, hmsg)
                debug_crypto("[%sW%s] Counter :: %s" %
                             (self.name, uniqid, self.wsocket_counter[uniqid]))
                debug_crypto("[%sW%s] Data:: %s" % (self.name, uniqid, data))
                self.wsocket_counter[uniqid] += 1
                # The counter can be desynchronized
                try:
                    command = self.__get_method(data)
                    arguments = self.__get_arguments(data)
                except:
                    sys.stderr.write("[%sW%s] Error with %s" %
                                     (self.name, uniqid, data))
                    conn.close()
                    return
                result = ""
                if command == "alert":
                    # preventing dead lock FIXME
                    # conn.send("ack|" + EOT_FLAG)
                    # alert message is forwarded to the whole chain
                    if self.master:
                        self.sendRemotef(self.master, 'alert|%s>%s' %
                                         (self.name, arguments))
                    # registered alert handlers are called
                    for handler in self.alert_handlers:
                        handler(data)
                elif command == "ack":
                    pass
                else:
                    debug_comm("[-] %sW%s> Data not parsed, forwarding" %
                               (self.name, uniqid))
                    result = self.send(data)
                    if result != "":
                        conn.send(str(result) + EOT_FLAG)
                    else:
                        conn.send("ack|" + EOT_FLAG)
                debug_comm("[%sW%s] Done" % (self.name, uniqid))
                # conn.shutdown(socket.SHUT_RDWR)
                # conn._sock.close()
                # conn.close()
                if command == "destroy":
                    conn.close()
                    self.quitting = True
                    debug_thread("[%sW%s] Connection closed, destroying" %
                                 (self.name, uniqid))
                    return  # just to be sure :)
            # Last message is splitted
            data_recv = data_recv.split(EOT_FLAG)[-1]

    def run(self):
        """
        Thread listenning on node port.
        It creates a worker thread for each accepted socket.

        It SHOULD NOT accept multiple hosts, but ready for it.
        """
        debug_thread("[%s] Creating interface listeners" % self.name)
        # for host in self.host:
        t = ThreadWorker(target=self.listen_interface, args=(self.host,))
        self.interface_threads.append(t)
        t.start()
        debug_thread("[%s] Interface listener quitting, waiting workers" %
                     self.name)
        for t in self.interface_threads:
            t.join()
        debug_thread("[%s] Interface workers joined" % self.name)

    def listen_interface(self, host):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # WARNING !!
        # Works only if hostname is not mapped to 127.0.0.1 in /etc/hosts
        # WARNING !!
        # self.host = socket.gethostbyname(socket.gethostname())
        debug_comm("[%s] Binding on %s:%s" %
                   (self.name, repr(host), self.port))
        s.bind((host, self.port))
        # self.port = s.getsockname()[1]
        s.listen(1000)
        debug_comm("[%s] Listening on %s:%s" % (self.name, host, self.port))
        while not self.quitting:
            rr, rw, err = select.select([s], [], [], 1)
            debug_thread("[%s] Selected" % self.name)
            if rr:
                conn, addr = s.accept()
                debug_comm("[%s] Accepted connection" % self.name)
                t = ThreadWorker(target=self.worker, args=(conn,))
                self.threads.append(t)
                t.start()
        debug_thread("[%s] Quitting, waiting for workers: %s" %
                     (self.name, self.threads))
        for t in self.threads:
            t.join()
        debug_thread("[%s] Workers joined" % self.name)

    def wait_backend(self, max_tries=0):
        """
        Ping node backend and return when backend is up.

        WARNING: Does not timeout if max_tries = 0
        """
        tries = 0
        while max_tries == 0 or tries < max_tries:
            name, ip, port = self.backend
            ret = subprocess.call("ping -c 1 %s" % ip,
                                  shell=True,
                                  stdout=open('/dev/null', 'w'),
                                  stderr=subprocess.STDOUT)
            if ret == 0:
                return 'Ok'
            else:
                time.sleep(1)
                tries += 1
        return None

    def __get_method(self, msg):
        return msg.split("|")[0]

    def __get_arguments(self, msg):
        return msg.split("|")[1]

    def __get_arguments_list(self, msg):
        return self.__get_arguments(msg).split('#')

    def __encrypt(self, msg, iv):
        # iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        # return iv, cipher.encrypt(msg)
        ciph = cipher.encrypt(msg)
        hmsg = self.__checksum(ciph)
        return ciph, hmsg
        # gcm = AES_GCM(self.key)
        # return gcm.encrypt(iv, msg)

    def __decrypt(self, msg, iv, auth):
        if auth != self.__checksum(msg):
            debug_comm('[%sW] Integrity error for json message,'
                       'skipping data ' % self.name)
            debug_comm('%s :: %s' % (auth, self.__checksum(msg)))
            return
        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return cipher.decrypt(msg)
        # gcm = AES_GCM(self.key)
        # return gcm.decrypt(iv, msg, auth)

    def __checksum(self, msg):
        return hashlib.sha1(msg).hexdigest()

    def launch(self):
        pass


class Node(PThread):
    # Overrides threading.Thread.run()
    def run(self):
        profiler = cProfile.Profile()
        try:
            return profiler.runcall(PThread.run, self)
        finally:
            profiler.dump_stats('myprofile-%s.profile' % (self.name))


class ThreadWorker(Thread):
    # Overrides threading.Thread.run()
    def run(self):
        profiler = cProfile.Profile()
        try:
            return profiler.runcall(Thread.run, self)
        finally:
            profiler.dump_stats('myprofile-worker-%s.profile' % (self.name))
