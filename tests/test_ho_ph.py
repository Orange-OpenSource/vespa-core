import pytest
import sys
import os

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.ho import HO
from vespa.ho_ph import HO_PH


@pytest.fixture(scope='module')
def ho_ph_instance():
    v = HO_PH('testnode', "127.0.0.1", 1337, None, run=False)
    return v

def test_instance_ho_ph(ho_ph_instance):
    assert isinstance(ho_ph_instance, HO)

def test_ho_ph_attributes(ho_ph_instance):
    assert ho_ph_instance.have_backend == False

def test_ho_ph_send(ho_ph_instance):
    assert ho_ph_instance.send("test") == ['help#']

def test_ninja_method(ho_ph_instance):
    ho_ph_instance.ninjaMethod()
