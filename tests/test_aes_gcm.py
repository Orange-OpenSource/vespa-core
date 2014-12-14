import pytest
import sys
import os

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PARENT = os.path.dirname(DOSSIER_COURANT)
sys.path.append(DOSSIER_PARENT)

from vespa.aes_gcm import *

master_key = 0xfeffe9928665731c6d6a8f9467308308
plaintext = b'\xd9\x31\x32\x25\xf8\x84\x06\xe5' + \
            b'\xa5\x59\x09\xc5\xaf\xf5\x26\x9a' + \
            b'\x86\xa7\xa9\x53\x15\x34\xf7\xda' + \
            b'\x2e\x4c\x30\x3d\x8a\x31\x8a\x72' + \
            b'\x1c\x3c\x0c\x95\x95\x68\x09\x53' + \
            b'\x2f\xcf\x0e\x24\x49\xa6\xb5\x25' + \
            b'\xb1\x6a\xed\xf5\xaa\x0d\xe6\x57' + \
            b'\xba\x63\x7b\x39'
auth_data = b'\xfe\xed\xfa\xce\xde\xad\xbe\xef' + \
            b'\xfe\xed\xfa\xce\xde\xad\xbe\xef' + \
            b'\xab\xad\xda\xd2'
init_value = 0xcafebabefacedbaddecaf888
ciphertext = b'\x42\x83\x1e\xc2\x21\x77\x74\x24' + \
             b'\x4b\x72\x21\xb7\x84\xd0\xd4\x9c' + \
             b'\xe3\xaa\x21\x2f\x2c\x02\xa4\xe0' + \
             b'\x35\xc1\x7e\x23\x29\xac\xa1\x2e' + \
             b'\x21\xd5\x14\xb2\x54\x66\x93\x1c' + \
             b'\x7d\x8f\x6a\x5a\xac\x84\xaa\x05' + \
             b'\x1b\xa3\x0b\x39\x6a\x0a\xac\x97' + \
             b'\x3d\x58\xe0\x91'
auth_tag = 0x5bc94fbc3221a5db94fae95ae7121a47


@pytest.fixture(scope='function')
def gcm():
    return AES_GCM(master_key)

def test_aes_gcm_encrypt(gcm):
    encrypted, new_tag = gcm.encrypt(init_value, plaintext, auth_data)
    assert hex(bytes_to_long(encrypted)) == \
           "0x42831ec2217774244b7221b784d0d49ce3aa212f2c02a4e035c17e2329ac" \
           "a12e21d514b25466931c7d8f6a5aac84aa051ba30b396a0aac973d58e091L"
    assert hex(new_tag) == \
           "0x5bc94fbc3221a5db94fae95ae7121a47L"

def test_aes_gcm_bad_tag(gcm):
    encrypted, new_tag = gcm.encrypt(init_value, plaintext, auth_data)

    with pytest.raises(InvalidTagException):
        decrypted = gcm.decrypt(init_value, encrypted,
                                new_tag + 1, auth_data)
def test_aes_gcm_decrypt(gcm):
    encrypted, new_tag = gcm.encrypt(init_value, plaintext, auth_data)
    decrypted = gcm.decrypt(init_value, encrypted, new_tag, auth_data)
    assert decrypted == plaintext
