import unittest
import pytest
import sys
import os

DOSSIER_COURRANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURRANT)
sys.path.append(DOSSIER_PARENT)

from vespa.node import Node

@pytest.fixture(scope='module')
def node_instance():
    n = Node('testnode', "127.0.0.1", 1337, None, run=False)
    return n

def test_encrypt(node_instance):
    iv = "%16i" % 0
    m = "hello"
    c = node_instance._encrypt(m, iv)
    assert c ==  ('Y\xc8\x83V\xe4',
                         '2dc4d9ee2b2f519dae0d9e55e1a3e512f30f2738')

def test_decrypt(node_instance):
    iv = "%16i" % 0
    m = "hello"
    c = node_instance._decrypt(m, iv, node_instance._checksum(m))
    assert c == 'Y\xf4\x14>\x1d'

def test_decrypt_bad_checksum(node_instance):
    iv = "%16i" % 0
    m = "hello"
    with pytest.raises(Exception):
        c = node_instance._decrypt(m, iv, node_instance._checksum("bad_hello"))

def test_checksum(node_instance):
    c = node_instance._checksum("hello")
    assert c == 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'

def test_encrypt_decrypt(node_instance):
    iv = "%16i" % 0
    m = "hello"
    c = node_instance._encrypt(m, iv)
    m_d = c[0]
    d = node_instance._decrypt(m_d, iv, node_instance._checksum(m_d))
    assert d == m

def test_register_handler(node_instance):
    def test_handler():
        return "OK"

    node_instance.register_alert_handler(test_handler)
    assert test_handler in node_instance.alert_handlers

def test_get_backend(node_instance):
    with pytest.raises(AttributeError):
        node_instance.get_backend()

def test_find_node_empty(node_instance):
    assert node_instance.findNode("test_slave") == 'None'

def test_register(node_instance):
    node_instance.register("test_slave", "127.0.0.1", "31337")
    assert ("test_slave", "127.0.0.1", 31337) in node_instance.list_slaves()

def test_find_node(node_instance):
    node_instance.register("test_find", "127.0.0.1", "31333")
    assert (("test_slave", "127.0.0.1", 31337) == 
            node_instance.findNode("test_slave"))

def test_send_unknow(node_instance):
    assert node_instance.send("hello") == ["help#"]

def test_send_help(node_instance):
    assert (node_instance.send("help|") ==
            ['help#desc#destroy#findNode#get_backend#launch#list_slaves#'
            'listen_interface#register#register_alert_handler#sendAlert'
            '#sendRemote#sendRemotef#sendSocket#wait_backend#worker#'])


if __name__ == '__main__':
    unittest.main()
