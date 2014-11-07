# -*- coding: utf-8 -*-
#
# Module name: controller.py
# Version:     1.0
# Created:     29/04/2014 by AurÃ©lien Wailly <aurelien.wailly@orange.com>
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
Controller
"""
from .log_pipe import *
import signal
import time
import json
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import urlparse


class HttpServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # content_length = int(self.headers.getheader("Content-Length"))
        # request = self.rfile.read(content_length)
        # BaseHTTPRequestHandler has a property called server and because
        # we create MyHTTPServer, it has a handler property
        request = urlparse.urlparse(self.path)
        c = self.server.controller
        response = self.server.handler(c, request.path)
        debug_controller(request)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response))

    def log_message(self, format, *args):
        return


class MyHTTPServer(HTTPServer):

    """this class is necessary to allow passing custom request handler into
       the RequestHandlerClass"""

    def __init__(self, server_address, RequestHandlerClass, handler, control):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.handler = handler
        self.controller = control


class HttpServer:

    def __init__(self, name, host, port, handler, c):
        self.name = name
        self.host = host
        self.port = port
        self.handler = handler
        self.server = None
        self.controller = c

    def start(self):
        # we need use MyHttpServer here
        self.server = MyHTTPServer((self.host, self.port), HttpServerHandler,
                                   self.handler, self.controller)
        self.server.serve_forever()

    def stop(self):
        if self.server:
            self.server.shutdown()


def server_handler(c, request):
    if request == "/archi":
        vo = c.model.slaves[0]
        vo_name, vo_host, vo_port = vo
        a = {'name': vo_name, 'host': vo_host, 'port': vo_port, 'children': []}
        vo_slaves_raw = c.model.sendRemote(vo, "list_slaves|")
        vo_slaves = eval(vo_slaves_raw)
        for ho in vo_slaves:
            ho_name, ho_host, ho_port = ho
            b = {'name': ho_name, 'host': ho_host, 'port': ho_port,
                 'children': []}
            a['children'].append(b)
            ho_slaves_raw = c.model.sendRemote(ho, "list_slaves|")
            try:
                ho_slaves = eval(ho_slaves_raw)
            except SyntaxError:
                ho_slaves = []
            for agent_name, agent_host, agent_port in ho_slaves:
                d = {'name': agent_name, 'host': agent_host,
                     'port': agent_port, 'children': []}
                b['children'].append(d)
        return a
    elif request == "/trans_bytes":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_trans_bytes|"))
    elif request == "/recv_bytes":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_recv_bytes|"))
    elif request == "/get_configini":
        return c.model.config
    elif request == "/get_alerts":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_alerts|"))
    elif request == "/connect":
        return "Ok"
    elif request == "/next_recv_bytes":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_next_recv_bytes|"))
    elif request == "/next_trans_bytes":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_next_trans_bytes|"))
    elif request == "/get_ip_connections":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_ip_connections|"))
    elif request == "/get_topology":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_topology|"))
    elif request == "/get_link_stats":
        vo = c.model.slaves[0]
        return eval(c.model.sendRemote(vo, "get_link_stats|"))
    else:
        return request


class Controller(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def handler(self, signum, false):
        if signum == 2:
            debug_init("Controller received shutting down")
            self.model.destroy()
            exit(0)

    def start(self):
        debug5("Started Controller")

        signal.signal(signal.SIGINT, self.handler)
        server = HttpServer("test server", "0.0.0.0", 8080, server_handler,
                            self)
        server.start()
