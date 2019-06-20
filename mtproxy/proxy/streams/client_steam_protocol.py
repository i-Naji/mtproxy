from .base_stream_protocol import BaseStreamProtocol
from .wappers import (CryptoWrappedStreamReader, CryptoWrappedStreamWriter)
from ...mtproto import Keys, DataCenter


class ClientSteamProtocol(BaseStreamProtocol):

    __slots__ = {'dc_idx'}
    EMPTY_READ_BUF_SIZE = 4096

    def __init__(self, config, reader, writer):
        super().__init__(
            config, reader, writer
        )
        self.dc_idx = None

    async def handle_handshake(self):

        sample = await self.reader.readexactly(Keys.SAMPLE_LEN)
        sample = Keys(sample)
        if sample.is_new_key:
            for user in self.config.users:
                secret = bytes.fromhex(user.secret)
                decryptor = sample.generate_decryptor(secret)
                decrypted = decryptor.decrypt(sample.buffer)
                encryptor = sample.generate_encryptor(secret)

                self.key = sample.enc_key_and_iv
                self.proto_tag = sample.valid_proto_tag(decrypted, secure=self.config.secure_only)
                if not self.proto_tag:
                    continue

                self.dc_idx = sample.get_dc_id(decrypted)

                self._stream_reader = CryptoWrappedStreamReader(self._stream_reader, decryptor)
                self._stream_writer = CryptoWrappedStreamWriter(self._stream_writer, encryptor)
                self.handshaked = True
                await sample.add_key(self.config.reply_check_length)
                return
            # return self.create_sender(dc_ip, DataCenter.PORT, proto_tag, enc_key_and_iv)
        else:
            print("Active fingerprinting detected from %s, freezing it" % self.ip)

        while await self.reader.read(ClientSteamProtocol.EMPTY_READ_BUF_SIZE):
            # just consume all the data
            pass

        return

    async def get_telegram_dc(self):
        dc_idx = abs(self.dc_idx) - 1

        if self.config.prefer_ipv6:
            if not 0 <= dc_idx < len(DataCenter.IPV6):
                return False
            dc_ip = DataCenter.IPV6[dc_idx]
        else:
            if not 0 <= dc_idx < len(DataCenter.IPV4):
                return False
            dc_ip = DataCenter.IPV4[dc_idx]

        return dc_ip, DataCenter.PORT

    def release_writer(self):
        self._stream_writer.encryptor.encrypt = lambda data: data
