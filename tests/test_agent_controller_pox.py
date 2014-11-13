import pytest
import unittest
import sys
import os
import SocketServer
import threading
import time
import json

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.node import Node
from vespa.agent_controller import Agent_Controller
from vespa.agent_controller_pox import Agent_Controller_Pox

EX_JSON = '{"key": "value"}'


class SimpleRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("%s" % EX_JSON)
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

def serve_data():
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', 18082), SimpleRequestHandler)
    http_server_thread = threading.Thread(target=server.handle_request)
    #http_server_thread.setDaemon(True)
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
    a = Agent_Controller_Pox('testnode', "127.0.0.1", 1341, None,
                                    run=False)
    a.controller_ip = "127.0.0.1"
    a.controller_port = 18082
    return a


def test_agent_controller_instance(agent_instance):
    assert isinstance(agent_instance, Agent_Controller)

def test_alert_ip(agent_instance, serve_http):
    assert agent_instance.alert_ip('10.0.0.4', '11:22:33:44:55:66') == "Ok"

def test_status_hackers(agent_instance, serve_http):
    assert agent_instance.status_hackers() == "Ok"

def test_release_hackers(agent_instance, serve_http):
    assert agent_instance.release_hackers() == "Ok"

def test_block_hackers(agent_instance, serve_http):
    assert agent_instance.block_hackers() == "Ok"

def test_get_topology(agent_instance, serve_http):
    assert agent_instance.get_topology() == eval(EX_JSON)

def test_link_stats(agent_instance, serve_http):
    assert agent_instance.get_link_stats() == eval(EX_JSON)

if __name__ == '__main__':
    unittest.main()
