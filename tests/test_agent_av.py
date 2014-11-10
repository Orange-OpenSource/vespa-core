import pytest
import unittest
import sys
import os
import SocketServer
import threading
import time

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.node import Node
from vespa.agent import Agent
from vespa.agent_av import Agent_AV

class SimpleRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("'hello'EndOfTransmission")
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

def serve_data():
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', 18081), SimpleRequestHandler)
    http_server_thread = threading.Thread(target=server.handle_request)
    http_server_thread.setDaemon(True)
    http_server_thread.start()
    return server

@pytest.fixture(scope='module')
def agent_instance():
    vm = ("test_vm", "127.0.0.1", 18081)
    a = Agent_AV('testnode', "127.0.0.1", 1348, None, vm)
    return a

@pytest.fixture(scope='function')
def serve_http(request):
    s = serve_data()
    def fin():
        s.server_close()
    request.addfinalizer(fin)
    return s

def test_agent_av_instance(agent_instance):
    assert isinstance(agent_instance, Agent)

def test_agent_av_isolate_warning(agent_instance):
    agent_instance.isolate_warning("'hello'")
    assert agent_instance.is_backend_reachable == False
    assert agent_instance.agent_hy == 'hello'

def test_agent_av_connect_warning(agent_instance):
    agent_instance.connect_warning()
    assert agent_instance.is_backend_reachable == True
    assert agent_instance.agent_hy == False

def test_agent_av_send_import(agent_instance, serve_http):
    agent_instance.connect_warning()
    msg = "import_list|coucou#coucou2"
    assert "hello" == agent_instance.send(msg)

def test_agent_av_send_register(agent_instance, serve_http):
    agent_instance.connect_warning()
    msg = "register_handler|coucou#coucou2"
    assert "hello" == agent_instance.send(msg)

def test_agent_av_send_clean(agent_instance, serve_http):
    vm = '("test_vm", "127.0.0.1", 18081)'
    agent_instance.isolate_warning(vm)
    msg = "clean_image|"
    assert "'hello'" == agent_instance.send(msg)

def test_agent_av_send_no_backend(agent_instance, serve_http):
    vm = '("test_vm", "127.0.0.1", 18081)'
    agent_instance.isolate_warning(vm)
    msg = "import_list|coucou#coucou2"
    assert ['help#'] == agent_instance.send(msg)

if __name__ == '__main__':
    unittest.main()
