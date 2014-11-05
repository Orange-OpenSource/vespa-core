import unittest
import sys
import os

DOSSIER_COURRANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURRANT)
sys.path.append(DOSSIER_PARENT)

from vespa.vo import VO
from vespa.node import Node


class TestInit(unittest.TestCase):
    def test_instance_vo(self):
        v = VO('testnode', "127.0.0.1", 1337, None, run=False)
        self.assertTrue(isinstance(v, Node))

    def test_alert_handler(self):
        v = VO('testnode', "127.0.0.1", 1337, None, run=False)
        self.assertTrue(v.alert in v.alert_handlers)

if __name__ == '__main__':
    unittest.main()
