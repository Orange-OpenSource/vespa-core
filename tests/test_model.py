import pytest
import unittest
import sys
import os
import socket
import time

DOSSIER_COURRANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURRANT)
sys.path.append(DOSSIER_PARENT)
sys.path.append("%s/vespa" % DOSSIER_PARENT)

from vespa import *
from vespa.model import Model


class TestInit(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
