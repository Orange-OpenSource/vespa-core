import unittest 
import sys
import os
 
DOSSIER_COURRANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURRANT)
sys.path.append(DOSSIER_PARENT)

from node import Node


class TestCrypto(unittest.TestCase):
    def test_encrypt(self):
        n = Node('testnode', "127.0.0.1", 1337, None, run=False)
        iv = 0
        msg = "hello"
        c = n.__encrypt(m, iv)
        self.assertEqual(c, 'pomme')

    def test_decrypt(self):
        n = Node('testnode', "127.0.0.1", 1337, None, run=False)
        iv = 0
        msg = "hello"
        c = n.__decrypt(m, iv, auth)
        self.assertEqual(c, 'pomme')
 
if __name__ == '__main__':
    unittest.main()
