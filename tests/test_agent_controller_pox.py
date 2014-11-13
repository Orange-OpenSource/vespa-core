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
from vespa.agent_controller_floodlight import Agent_Controller_Pox


EX_JSON = '{"key": "welcome"}'

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
    a = Agent_Controller_Pox('testnode', "127.0.0.1", 1341, None,
                                    run=False)
    a.controller_ip = "127.0.0.1:18080"
    return a


def test_agent_controller_instance(agent_instance):
    assert isinstance(agent_instance, Agent_Controller)

def test_alert_ip(agent_instance, serve_http):
    assert agent_instance.alert_ip('10.0.0.4', '11:22:33:44:55:66') == EX_JSON

def test_status_hackers(agent_instance, serve_http):
    assert agent_instance.status_hackers() == EX_JSON

def test_release_hackers(agent_instance, serve_http):
    assert agent_instance.release_hackers() == EX_JSON

def test_block_hackers(agent_instance, serve_http):
    assert agent_instance.block_hackers('11:22:33:44:55:66') == EX_JSON

def test_get_topology(agent_instance, serve_http):
    expected = {'nodes': [{'id': u'00:00:00:1c:73:19:bd:d0'},
                          {'id': u'00:00:00:1a:1e:15:97:00'},
                          {'id': u'00:00:00:1c:73:19:bd:d0'},
                          {'id': u'00:00:00:1a:1e:0d:47:80'},
                          {'id': u'00:00:00:1c:73:19:bd:d0'},
                          {'id': u'00:00:00:1a:1e:0d:91:c0'}],
                'links': [{'source': 0, 'target': 1, 'value': 177},
                          {'source': 0, 'target': 3, 'value': 78},
                          {'source': 0, 'target': 5, 'value': 196}]}
    gt = agent_instance.get_topology()
    s1 = [ s["source"] for s in [ i for i in gt['links']]]
    s2 = [ s["source"] for s in [ i for i in expected['links']]]
    assert s1 == s2

    t1 = [ s["target"] for s in [ i for i in gt['links']]]
    t2 = [ s["target"] for s in [ i for i in expected['links']]]
    assert t1 == t2

def test_link_stats(agent_instance, serve_http):
    assert agent_instance.get_link_stats() == EX_JSON 

if __name__ == '__main__':
    unittest.main()
