import pytest
import sys
import os

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.ho import HO
from vespa.ho_hy import HO_HY


@pytest.fixture(scope='module')
def ho_hy_instance():
    v = HO_HY('testnode', "127.0.0.1", 1337, None, run=False)
    return v

def test_instance_ho_hy(ho_hy_instance):
    assert isinstance(ho_hy_instance, HO)

def test_ho_hy_attributes(ho_hy_instance):
    assert ho_hy_instance.have_backend == False

def test_ho_hy_send(ho_hy_instance):
    assert ho_hy_instance.send("test") == ['help#']

def test_ninja_method(ho_hy_instance):
    ho_hy_instance.ninjaMethod()
