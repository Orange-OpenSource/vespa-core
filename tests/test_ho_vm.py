import pytest
import sys
import os

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.ho import HO
from vespa.ho_vm import HO_VM


@pytest.fixture(scope='module')
def ho_vm_instance():
    v = HO_VM('testnode', "127.0.0.1", 1337, None, run=False)
    return v

def test_instance_ho_vm(ho_vm_instance):
    assert isinstance(ho_vm_instance, HO)

def test_ho_vm_attributes(ho_vm_instance):
    assert ho_vm_instance.have_backend == False

def test_ho_vm_send(ho_vm_instance):
    assert ho_vm_instance.send("test") == ['help#']

def test_ninja_method(ho_vm_instance):
    ho_vm_instance.ninjaMethod()
