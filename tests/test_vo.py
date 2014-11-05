import unittest
import sys
import os

DOSSIER_COURRANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURRANT)
DOSSIER_PARENT = os.path.dirname(DOSSIER_PARENT)
sys.path.append(DOSSIER_PARENT)

from vespa.vo import VO
from vespa.node import Node


class TestInit(unittest.TestCase):
    def test_instance_node(self):
        v = VO('testnode', "127.0.0.1", 1337, None, run=False)
        self.assertIsInstance(v, Node)

    def test_alert_handler(self):
        v = VO('testnode', "127.0.0.1", 1337, None, run=False)
        self.assertIn(v.alert, v.alert_handlers)

if __name__ == '__main__':
    unittest.main()
