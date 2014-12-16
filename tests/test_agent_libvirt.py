import pytest
import unittest
import sys
import os
import SocketServer
import threading
import time
import libvirt

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.node import Node
from vespa.agent import Agent
from vespa.agent_libvirt import Agent_Libvirt

TEST_STRING = "hello"
PORT = 18089
PORT_AGENT = 1367


class SimpleRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("%s" % TEST_STRING)
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

def serve_data():
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', PORT), SimpleRequestHandler)
    http_server_thread = threading.Thread(target=server.handle_request)
    http_server_thread.setDaemon(True)
    http_server_thread.start()
    return server

@pytest.fixture(scope='function')
def serve_http(request):
    s = serve_data()
    def fin():
        s.server_close()
    request.addfinalizer(fin)
    return s

@pytest.fixture(scope='module')
def agent_instance():
    a = Agent_Libvirt('testnode', "127.0.0.1", PORT_AGENT, None, run=False)
    a.libvirt_port = PORT 
    a.backend = ("libvirt", a.libvirt_host, PORT, "usertest")
    return a


def test_agent_libvirt(agent_instance):
    assert isinstance(agent_instance, Agent)

def test_agent_libvirt_send(agent_instance):
    assert agent_instance.send("msg_test") == ['help#']

def test_agent_libvirt__get_dom_name(agent_instance):
    with pytest.raises(Exception):
        agent_instance._get_dom_name("nodename", agent_instance)

"""
def test_agent_libvirt_cut_link(agent_instance, serve_http):
    with pytest.raises(libvirt.libvirtError):
        agent_instance.cut_link()

def test_agent_libvirt_connect_link(agent_instance, serve_http):
    with pytest.raises(libvirt.libvirtError):
        agent_instance.connect_link()

def test_agent_libvirt_migrate(agent_instance, serve_http):
    with pytest.raises(libvirt.libvirtError):
        agent_instance.migrate("nodename", "test", "test")

def test_agent_libvirt_contains_vm(agent_instance, serve_http):
    vm = True
    assert agent_instance.contains_vm(vm) == False

def test_agent_libvirt_send_key(agent_instance, serve_http):
    vm = True
    key = True
    with pytest.raises(libvirt.libvirtError):
        agent_instance.send_key(vm, key)

def test_agent_libvirt_restart(agent_instance, serve_http):
    vm = True
    with pytest.raises(libvirt.libvirtError):
        agent_instance.restart(vm)

def test_agent_libvirt_restart_hard(agent_instance, serve_http):
    vm = True
    with pytest.raises(libvirt.libvirtError):
        agent_instance.restart_hard(vm)
"""
