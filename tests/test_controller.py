import pytest
import sys
import os
import SocketServer
import threading
import time

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.controller import Controller

TEST_ARG1 = 'aloha:kikoo:lala'
TEST_STRING = 'hello|ola:alo|%s\\r%s' % (TEST_ARG1, TEST_ARG1)


@pytest.fixture(scope='module')
def controller_instance():
    vm = ("test_vm", "127.0.0.1", 18081)
    a = Agent_AV('testnode', "127.0.0.1", 1348, None, vm)
    return a

@pytest.fixture(scope='function')
def serve_http(request):
    s = Controller(model, None)
    def fin():
        s.server_close()
    request.addfinalizer(fin)
    return s


