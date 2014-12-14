import pytest
import sys
import os
import socket
import SocketServer
import threading
import time
import requests

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.controller import Controller

TEST_ARG1 = 'aloha:kikoo:lala'
TEST_STRING = 'hello|ola:alo|%s\\r%s' % (TEST_ARG1, TEST_ARG1)
HOST = '127.0.0.1'
PORT = 8080

class Model_light(object):
    def __init__(self):
        self.slaves = [("voname", "vo_host", 1234)]
        self.config = "configgoeshere"

    def sendRemote(self, dst, msg):
        if msg == "list_slaves|":
            fstr = repr(self.slaves)
        else:
            fstr = repr([ "%s :: %s" % (dst, msg) ])
        return fstr

    def destroy(self):
        pass

@pytest.fixture(scope='module')
def controller_instance():
    s = Controller(Model_light(), None, testmode=True)
    t = threading.Thread(target=s.start)
    t.start()
    time.sleep(0.1)
    return s

@pytest.fixture(scope='function')
def get_socket(request):
    s = socket.socket()
    s.connect(("127.0.0.1", 8080))
    def fin():
        s.close()
    request.addfinalizer(fin)
    return s

def test_controller_server_handler(controller_instance):
    r = requests.get("http://%s:%s/archi" % (HOST,PORT))
    assert r.content == \
           '{"host": "vo_host", "children": [{"host": "vo_host", "children":'\
           ' [{"host": "vo_host", "children": [], '\
           '"name": "voname", "port": 1234}], '\
           '"name": "voname", "port": 1234}], "name": "voname", "port": 1234}'

def test_controller_default_handler(controller_instance):
    r = requests.get("http://%s:%s/nothinghere" % (HOST,PORT))
    assert r.content == '"/nothinghere"'

def test_controller_trans_bytes_handler(controller_instance):
    r = requests.get("http://%s:%s/trans_bytes" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_trans_bytes|"]'

def test_controller_recv_bytes_handler(controller_instance):
    r = requests.get("http://%s:%s/recv_bytes" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_recv_bytes|"]'

def test_controller_get_config(controller_instance):
    r = requests.get("http://%s:%s/get_configini" % (HOST,PORT))
    assert r.content == '"configgoeshere"'

def test_controller_get_alerts_handler(controller_instance):
    r = requests.get("http://%s:%s/get_alerts" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_alerts|"]'

def test_controller_connect_handler(controller_instance):
    r = requests.get("http://%s:%s/connect" % (HOST,PORT))
    assert r.content == '"Ok"'

def test_controller_next_recv_bytes_handler(controller_instance):
    r = requests.get("http://%s:%s/next_recv_bytes" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_next_recv_bytes|"]'

def test_controller_next_trans_bytes_handler(controller_instance):
    r = requests.get("http://%s:%s/next_trans_bytes" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_next_trans_bytes|"]'

def test_controller_get_ip_connections_handler(controller_instance):
    r = requests.get("http://%s:%s/get_ip_connections" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_ip_connections|"]'

def test_controller_get_topology_handler(controller_instance):
    r = requests.get("http://%s:%s/get_topology" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_topology|"]'

def test_controller_get_link_stats_handler(controller_instance):
    r = requests.get("http://%s:%s/get_link_stats" % (HOST,PORT))
    assert r.content == \
           '["(\'voname\', \'vo_host\', 1234) :: get_link_stats|"]'

def test_controller_destroy(controller_instance):
    controller_instance._shutdown()
