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
from vespa.agent_connections import Agent_Connections

TEST_STRING = "hello"


class SimpleRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("'%s'EndOfTransmission" % TEST_STRING)
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()


def serve_data():
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', 18081), SimpleRequestHandler)
    http_server_thread = threading.Thread(target=server.handle_request)
    #http_server_thread.setDaemon(True)
    http_server_thread.start()
    return server


@pytest.fixture(scope='module')
def agent_instance(request):
    a = Agent_Connections('testnode', "127.0.0.1", 1340, None, run=False)
    def fin():
        pass
        a.destroy()
    return a


@pytest.fixture(scope='function')
def serve_http(request):
    s = serve_data()
    def fin():
        s.server_close()
    request.addfinalizer(fin)
    return s


def test_agent_connections(agent_instance):
    assert isinstance(agent_instance, Agent)

def test_get_conns(agent_instance):
    assert isinstance(agent_instance._get_conns(), list)

def test_get_conns_lsof(agent_instance):
    assert isinstance(agent_instance._get_conns_lsof(), dict)

if __name__ == '__main__':
    unittest.main()
