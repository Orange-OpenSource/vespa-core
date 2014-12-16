import pytest
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

TEST_ARG1 = 'aloha:kikoo:lala'
TEST_STRING = 'hello|ola:alo|%s\\r%s' % (TEST_ARG1, TEST_ARG1)


class SimpleRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("'%s'EndOfTransmission" % TEST_STRING)
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

class NoListRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        self.request.send("'%s'EndOfTransmission" % TEST_STRING.split("\\")[0])
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

class NoColonRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(102400) # token receive
        sstr = TEST_STRING.split("|")
        new_string = sstr[0:2] + [sstr[2].replace(":", "")]
        new_string = "|".join(new_string)
        self.request.send("'%s'EndOfTransmission" % new_string)
        time.sleep(0.1) # make sure it finishes receiving request before closing
        self.request.close()

def serve_data(request_handler):
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('127.0.0.1', 18081), request_handler)
    http_server_thread = threading.Thread(target=server.handle_request)
    #http_server_thread.setDaemon(True)
    http_server_thread.start()
    return server

@pytest.fixture(scope='module')
def agent_instance():
    vm = ("test_vm", "127.0.0.1", 18081)
    a = Agent_AV('testnode', "127.0.0.1", 1348, None, vm)
    return a

@pytest.fixture(scope='function')
def serve_http(request):
    s = serve_data(SimpleRequestHandler)
    def fin():
        s.server_close()
    request.addfinalizer(fin)
    return s

@pytest.fixture(scope='function')
def serve_http_no_list(request):
    s = serve_data(NoListRequestHandler)
    def fin():
        s.server_close()
    request.addfinalizer(fin)
    return s

@pytest.fixture(scope='function')
def serve_http_no_colon(request):
    s = serve_data(NoColonRequestHandler)
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
    assert TEST_STRING.replace('\\r', '\r') == agent_instance.send(msg)

def test_agent_av_send_register(agent_instance, serve_http):
    agent_instance.connect_warning()
    msg = "register_handler|coucou#coucou2"
    assert TEST_STRING.replace('\\r', '\r') == agent_instance.send(msg)

def test_agent_av_send_clean(agent_instance, serve_http):
    vm = '("test_vm", "127.0.0.1", 18081)'
    agent_instance.isolate_warning(vm)
    msg = "clean_image|"
    assert "'%s'" % TEST_STRING == agent_instance.send(msg)

def test_agent_av_send_no_backend(agent_instance):
    vm = '("test_vm", "127.0.0.1", 18081)'
    agent_instance.isolate_warning(vm)
    msg = "import_list|coucou#coucou2"
    assert ['help#'] == agent_instance.send(msg)

def test_agent_av_dump(agent_instance, serve_http):
    agent_instance.connect_warning()
    assert ([('ola', 'alo'), ('aloha:kikoo', 'lala'), ('aloha:kikoo', 'lala')]
            == agent_instance.dump_analyzed_file_list())

def test_agent_av_dump_no_list_separator(agent_instance, serve_http_no_list):
    agent_instance.connect_warning()
    assert (['aloha:kikoo:lala']
            == agent_instance.dump_analyzed_file_list())

def test_agent_av_dump_no_colon(agent_instance, serve_http_no_colon):
    agent_instance.connect_warning()
    assert ([('ola', 'alo')]
            == agent_instance.dump_analyzed_file_list())
