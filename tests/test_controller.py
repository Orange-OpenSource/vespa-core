import pytest
import sys
import os
import socket
import SocketServer
import threading
import time

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.controller import Controller

TEST_ARG1 = 'aloha:kikoo:lala'
TEST_STRING = 'hello|ola:alo|%s\\r%s' % (TEST_ARG1, TEST_ARG1)


class Model_light(object):
    def __init__(self):
        self.a = "a"

@pytest.fixture(scope='module')
def controller_instance():
    s = Controller(Model_light(), None, testmode=True)
    t = threading.Thread(target=s.start)
    t.start()
    return t

@pytest.fixture(scope='function')
def get_socket(request):
    s = socket.socket()
    s.connect(("127.0.0.1", 8080))
    def fin():
        s.close()
    request.addfinalizer(fin)
    return s

def test_controller_server_handler(controller_instance, get_socket):
    get_socket.send("GET /archi HTTP1.1\n\n")
    assert get_socket.recv(1024) == "hello"

def test_controller_destroy(controller_instance, get_socket):
    get_socket.send("GET /destroy HTTP/1.1\n\n")
    assert get_socket.recv(1024) == "hello"
