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
        iv = "%16i" % 0
        m = "hello"
        c = n._encrypt(m, iv)
        self.assertEqual(c, ('Y\xc8\x83V\xe4',
                             '2dc4d9ee2b2f519dae0d9e55e1a3e512f30f2738'))

    def test_decrypt(self):
        n = Node('testnode', "127.0.0.1", 1337, None, run=False)
        iv = "%16i" % 0
        m = "hello"
        c = n._decrypt(m, iv, n._checksum(m))
        self.assertEqual(c, 'Y\xf4\x14>\x1d')

    def test_checksum(self):
        n = Node('testnode', "127.0.0.1", 1337, None, run=False)
        c = n._checksum("hello")
        self.assertEqual(c, 'aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d')

    def test_encrypt_decrypt(self):
        n = Node('testnode', "127.0.0.1", 1337, None, run=False)
        iv = "%16i" % 0
        m = "hello"
        c = n._encrypt(m, iv)
        m_d = c[0]
        d = n._decrypt(m_d, iv, n._checksum(m_d))
        self.assertEqual(d, m)

if __name__ == '__main__':
    unittest.main()
