import py
import pytest
import unittest
import sys
import os
import socket
import time
import tempfile

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)
sys.path.append("%s/vespa" % DOSSIER_PARENT)

from vespa import *
from vespa.model import Model


class TestInitModel(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()
        p = tmpdir.join("config.ini")
        conf = ('[%s]\nType= Machine\nInterfaces= 127.0.0.1\n\n'
                '[VO]\nLocation= %s\nMaster=\nPort=1337\n'
                % (socket.gethostname(), socket.gethostname()))
        p.write(conf)

    def test_init_model(self):
        m = Model()
        self.assertEquals(m.name, "model")
        m.destroy()
        time.sleep(1)


class TestFindNodeModel(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()
        p = tmpdir.join("config.ini")
        conf = ('[%s]\nType= Machine\nInterfaces= 127.0.0.1\n\n'
                '[VO]\nLocation= %s\nMaster=\nPort=1337\n'
                '[HO]\nLocation= %s\nMaster=VO\nPort=1333\n'
                % (socket.gethostname(), socket.gethostname(),
                   socket.gethostname()))
        p.write(conf)

    def test_no_node(self):
        m = Model()
        self.assertEquals(m.name, "model")
        with pytest.raises(Exception):
            m.findNode("XXX")
        m.destroy()
        time.sleep(1)


@pytest.fixture(scope='module')
def moduledir(request):
    dir = py.path.local(tempfile.mkdtemp())
    request.addfinalizer(lambda: dir.remove(rec=1))
    return dir


@pytest.fixture(scope="module")
def model_instance(request, moduledir):
    moduledir.chdir()
    p = moduledir.join("config.ini")
    conf = ('[%s]\nType= Machine\nInterfaces= 127.0.0.1\n\n'
            '[VO]\nLocation= %s\nMaster=\nPort=1337\n'
            '[HO]\nLocation= %s\nMaster=VO\nPort=1333\n'
            '[Agent]\nLocation= %s\nMaster=HO\nPort=1330\n'
            % (socket.gethostname(), socket.gethostname(),
               socket.gethostname(), socket.gethostname()))
    p.write(conf)
    m = Model()
    def fin():
        m.destroy()
        time.sleep(1)
    request.addfinalizer(fin)
    return m


def test_findnode_no_node(model_instance):
    with pytest.raises(Exception):
        model_instance.findNode("XXX")


def test_findnode_node_vo(model_instance):
    assert model_instance.findNode("VO") == ("VO",
                                             "127.0.0.1",
                                             1337)


def test_findnode_node_ho(model_instance):
    assert model_instance.findNode("HO") == ("HO",
                                             "127.0.0.1",
                                             1333)


def test_findnode_node_agent(model_instance):
    assert model_instance.findNode("Agent") == ("Agent",
                                             "127.0.0.1",
                                             1330)


class TestInitModelExceptionNoKey(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()
        p = tmpdir.join("config.ini")
        conf = ('[%s]\nType= Machine\nInterfaces= 127.0.0.1\n\n'
                '[VO]\nLocation= %s\nMaster=\nPort=1337\n'
                '[XXX]\nLocation= %s\nMaster=VO\nPort=1338\n'
                % (socket.gethostname(), socket.gethostname(),
                   socket.gethostname()))
        p.write(conf)

    def test_init_model_no_master(self):
        with pytest.raises(ImportError):
            m = Model()


class TestInitModelExceptionNoVO(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()
        p = tmpdir.join("config.ini")
        conf = ('[%s]\nType= Machine\nInterfaces= 127.0.0.1\n\n'
                '[HO]\nLocation= %s\nMaster=\nPort=1337\n'
                % (socket.gethostname(), socket.gethostname()))
        p.write(conf)

    def test_init_model_no_vo(self):
        with pytest.raises(KeyError):
            m = Model()


if __name__ == '__main__':
    unittest.main()
