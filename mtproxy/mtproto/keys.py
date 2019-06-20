import os
import hashlib
import collections
from . import AES


class Keys:
    """MTProto Handshake helper class

    Attributes:
        used_dec_keys (:class:`collections.OrderedDict`)
            collected handshakes.
        SAMPLE_LEN (``int``)
            Length of handshake message.
        KEY_LEN (``int``)
            Decryption/Encryption Key length.
        IV_LEN (``int``)
            Decryption/Encryption IV Key length.
        SKIP_LEN (``int``)
            Length of ignored charterers in handshake message.
        DC_IDX_LEN (``int``)
            Length of Data Center ID in handshake message.
        DC_IDX_POS (``int``)
            Position of Data Center ID in handshake message.
        PROTO_TAG_LEN:
            Length of TCP Protocol Tag in handshake message.
        PROTO_TAG_POS (``int``)
            Position of TCP Protocol Tag in handshake message.
        PROTO_TAG_ABRIDGED:
            TCP ABRIDGED Tag.
        PROTO_TAG_INTERMEDIATE:
            TCP INTERMEDIATE Tag.
        PROTO_TAG_SECURE:
            TCP SECURE INTERMEDIATE TAG.

    Parameters:
        data (``bytes``)
            64 or more charecters of a handshake message.
    """
    used_dec_keys = collections.OrderedDict()

    SAMPLE_LEN = 64
    KEY_LEN = 32
    IV_LEN = 16
    SKIP_LEN = 8
    DC_IDX_LEN = 2

    DC_IDX_POS = 60

    PROTO_TAG_LEN = 4
    PROTO_TAG_POS = 56
    PROTO_TAG_ABRIDGED = b'\xef\xef\xef\xef'
    PROTO_TAG_INTERMEDIATE = b'\xee\xee\xee\xee'
    PROTO_TAG_SECURE = b'\xdd\xdd\xdd\xdd'

    RESERVED_HANDSHAKE_FIRST_CHARS = b'\xef'
    RESERVED_HANDSHAKE_BEGININGS = (b'PVrG', b'GET ', b'POST', b'\xee\xee\xee\xee')
    RESERVED_HANDSHAKE_CONTINUES = b'\x00\x00\x00\x00'

    __slots__ = {'buffer', 'dec_key_and_iv', '_dec_key', '_enc_key', '_enc_key_and_iv'}

    def __init__(self, data: bytes):
        self.buffer = data[:Keys.SAMPLE_LEN]
        self.dec_key_and_iv = self.buffer[Keys.SKIP_LEN:Keys.SKIP_LEN + Keys.KEY_LEN + Keys.IV_LEN]
        self._dec_key = None
        self._enc_key = None
        self._enc_key_and_iv = None

    @property
    def is_new_key(self):
        return self.dec_key_and_iv not in Keys.used_dec_keys

    async def add_key(self, max_len):
        while len(Keys.used_dec_keys) >= max_len:
            Keys.used_dec_keys.popitem(last=False)
        Keys.used_dec_keys[self.dec_key_and_iv] = True

    @property
    def dec_key(self):
        if self._dec_key is None:
            return self.dec_key_and_iv[:Keys.KEY_LEN]
        else:
            return self._dec_key

    @property
    def dec_iv(self):
        return self.dec_key_and_iv[Keys.KEY_LEN:]

    @property
    def rev_buf(self):
        return self.buffer[::-1]

    @property
    def enc_key_and_iv(self):
        if self._enc_key_and_iv is None:
            self._enc_key_and_iv = self.dec_key_and_iv[::-1]
        return self._enc_key_and_iv

    @property
    def enc_key(self):
        if self._enc_key is None:
            return self.enc_key_and_iv[:Keys.KEY_LEN]
        else:
            return self._enc_key

    @property
    def enc_iv(self):
        return self.enc_key_and_iv[Keys.KEY_LEN:]

    def generate_decryptor(self, secret: bytes = None):
        if secret is not None:
            self._dec_key = hashlib.sha256(self.dec_key + secret).digest()
        return AES.create_aes_ctr(key=self.dec_key, iv=int.from_bytes(self.dec_iv, 'big'))

    def generate_encryptor(self, secret: bytes = None):
        if secret is not None:
            self._enc_key = hashlib.sha256(self.enc_key + secret).digest()
            self._enc_key_and_iv = self._enc_key + self.enc_iv

        return AES.create_aes_ctr(key=self.enc_key, iv=int.from_bytes(self.enc_iv, 'big'))

    @staticmethod
    def get_dc_id(data: bytes) -> int:
        return int.from_bytes(data[Keys.DC_IDX_POS:Keys.DC_IDX_POS + Keys.DC_IDX_LEN], 'little', signed=True)

    @staticmethod
    def valid_proto_tag(data: bytes, secure: bool = False):
        proto_tag = data[Keys.PROTO_TAG_POS:Keys.PROTO_TAG_POS + Keys.PROTO_TAG_LEN]
        if proto_tag not in (
                Keys.PROTO_TAG_ABRIDGED, Keys.PROTO_TAG_INTERMEDIATE, Keys.PROTO_TAG_SECURE
        ):
            print('unresolved tag %s' % proto_tag)
            return False

        if secure and proto_tag != Keys.PROTO_TAG_SECURE:
            return False

        return proto_tag

    @staticmethod
    def generator(proto_tag: bytes, dec_key_and_iv: bytes = None) -> 'Keys':

        while True:
            rnd = bytearray(os.urandom(Keys.SAMPLE_LEN))
            if (rnd[:1] != Keys.RESERVED_HANDSHAKE_FIRST_CHARS and
                    rnd[:4] not in Keys.RESERVED_HANDSHAKE_BEGININGS and
                    rnd[4:8] != Keys.RESERVED_HANDSHAKE_CONTINUES):
                break

        rnd[Keys.PROTO_TAG_POS:Keys.PROTO_TAG_POS + Keys.PROTO_TAG_LEN] = proto_tag
        if dec_key_and_iv:
            rnd[Keys.SKIP_LEN:Keys.SKIP_LEN + Keys.KEY_LEN + Keys.IV_LEN] = dec_key_and_iv[::-1]

        rnd = bytes(rnd)

        return Keys(rnd[::-1])
