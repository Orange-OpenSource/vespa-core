import pytest
import sys
import os

DOSSIER_COURRANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURRANT)
sys.path.append(DOSSIER_PARENT)

from vespa.vo import VO
from vespa.node import Node

@pytest.fixture(scope='module')
def vo_instance():
    v = VO('testnode', "127.0.0.1", 1337, None, run=False)
    return v

def test_vo_instance(vo_instance):
    assert isinstance(vo_instance, Node)

def test_vo_alert_handler(vo_instance):
    assert vo_instance.alert in vo_instance.alert_handlers

def test_vo_get_next_trans_bytes_empty(vo_instance):
    assert vo_instance.get_next_trans_bytes() == 0

def test_vo_get_trans_bytes(vo_instance):
    vo_instance.trans_bytes = \
            [ {'time': 1, 'bytes': 10},
              {'time': 2, 'bytes': 20},
              {'time': 3, 'bytes': 40},
              {'time': 4, 'bytes': 80} ]
    assert vo_instance.get_trans_bytes() == [10, 20, 40]

def test_vo_get_next_recv_bytes_empty(vo_instance):
    assert vo_instance.get_next_recv_bytes() == 0

def test_vo_get_recv_bytes(vo_instance):
    vo_instance.recv_bytes = \
            [ {'time': 1, 'bytes': 10},
              {'time': 2, 'bytes': 20},
              {'time': 3, 'bytes': 40},
              {'time': 4, 'bytes': 80} ]
    assert vo_instance.get_recv_bytes() == [10, 20, 40]

def test_vo_get_next_recv_bytes(vo_instance):
    assert vo_instance.get_next_recv_bytes() == 40

def test_vo_get_next_trans_bytes(vo_instance):
    assert vo_instance.get_next_trans_bytes() == 40

def test_vo_get_ip_connections_bytes(vo_instance):
    assert vo_instance.get_ip_connections() == []

def test_vo_get_alerts(vo_instance):
    assert vo_instance.get_alerts() == []

def test_vo_get_topology(vo_instance):
    assert vo_instance.get_topology() == []

def test_vo_get_link_stats(vo_instance):
    assert vo_instance.get_link_stats() == []

def test_vo_alert_recv_bytes(vo_instance):
    vo_instance.alert("alert|%s>%s" % ("Agent_Bandwidth", "recv_bytes#5#160"))
    assert vo_instance.get_next_recv_bytes() == 80.0

def test_vo_alert_trans_bytes(vo_instance):
    vo_instance.alert("alert|%s>%s" % ("Agent_Bandwidth", "trans_bytes#5#160"))
    assert vo_instance.get_next_trans_bytes() == 80.0

def test_vo_alert_recv_bytes_max(vo_instance):
    for m in range(0,100):
        vo_instance.alert("alert|%s>%s" % ("Agent_Bandwidth", "recv_bytes#5#160"))
        assert len(vo_instance.get_recv_bytes()) <= 50

def test_vo_alert_trans_bytes_max(vo_instance):
    for m in range(0,100):
        vo_instance.alert("alert|%s>%s" % ("Agent_Bandwidth", "trans_bytes#5#160"))
        assert len(vo_instance.get_trans_bytes()) <= 50
