from .base_stream_protocol import BaseStreamProtocol
from .wappers import (CryptoWrappedStreamReader, CryptoWrappedStreamWriter)
from ...mtproto import Keys


class ServerStreamProtocol(BaseStreamProtocol):

    async def handle_handshake(self):
        sample = Keys.generator(self.proto_tag, dec_key_and_iv=self.config.fast_mode and self.key or False)
        encryptor = sample.generate_encryptor()

        first_message = sample.rev_buf[:sample.PROTO_TAG_POS] + encryptor.encrypt(sample.rev_buf)[
                                                                  sample.PROTO_TAG_POS:]

        self.writer.write(first_message)
        await self.writer.drain()

        self._stream_reader = CryptoWrappedStreamReader(self._stream_reader, sample.generate_decryptor())
        self._stream_writer = CryptoWrappedStreamWriter(self._stream_writer, encryptor)

        self.handshaked = True

    def release_reader(self):
        """release reader decryption function"""
        self._stream_reader.decryptor.decrypt = lambda data: data
