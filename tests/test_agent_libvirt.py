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


EX_JSON = '''[{"src-switch":"00:00:00:1c:73:19:bd:d0","src-port":5,
"src-port-state":0,"dst-switch":"00:00:00:1a:1e:15:97:00",
"dst-port":49,"dst-port-state":0,"type":"internal"},
{"src-switch":"00:00:00:1c:73:19:bd:d0","src-port":11,
"src-port-state":0,"dst-switch":"00:00:00:1a:1e:0d:47:80",
"dst-port":26,"dst-port-state":0,"type":"internal"},
{"src-switch":"00:00:00:1c:73:19:bd:d0","src-port":9,
"src-port-state":0,"dst-switch":"00:00:00:1a:1e:0d:91:c0",
"dst-port":26,"dst-port-state":0,"type":"internal"}]'''

class SimpleRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("%s" % EX_JSON)
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

def serve_data():
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', 18080), SimpleRequestHandler)
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
    a = Agent_Libvirt('testnode', "127.0.0.1", 1341, None,
                                    run=False)
    a.libvirt_port = 18080
    a.backend = ("libvirt", a.libvirt_host, 18080, "usertest")
    return a


def test_agent_libvirt(agent_instance):
    assert isinstance(agent_instance, Agent)

def test_agent_libvirt_send(agent_instance):
    assert agent_instance.send("msg_test") == ['help#']

def test_agent_libvirt__get_dom_name(agent_instance):
    with pytest.raises(Exception):
        agent_instance._get_dom_name("nodename", agent_instance)

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


if __name__ == '__main__':
    unittest.main()
