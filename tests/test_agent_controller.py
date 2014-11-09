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
from vespa.agent_controller import Agent_Controller

class SimpleRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("hello")
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

def serve_data():
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', 18080), SimpleRequestHandler)
    http_server_thread = threading.Thread(target=server.handle_request)
    http_server_thread.setDaemon(True)
    http_server_thread.start()
    return server

@pytest.fixture(scope='module')
def agent_instance():
    a = Agent_Controller('testnode', "127.0.0.1", 1337, None, run=False)
    s = serve_data()
    return a

def test_agent_controller_instance(agent_instance):
    assert isinstance(agent_instance, Agent)

def test_alert_ip(agent_instance):
    agent_instance.controller_ip = "127.0.0.1"
    agent_instance.controller_port = 18080
    assert agent_instance.alert_ip('10.0.0.4', '11:22:33:44:55:66') == "Ok"

if __name__ == '__main__':
    unittest.main()
