from .base_stream_reader import LayeredStreamReaderBase


class CryptoWrappedStreamReader(LayeredStreamReaderBase):

    __slots__ = {'upstream', 'decryptor', 'block_size', 'buf'}

    def __init__(self, upstream, decryptor, block_size=1):
        self.upstream = upstream
        self.decryptor = decryptor
        self.block_size = block_size
        self.buf = bytearray()

    async def read(self, n):
        if self.buf:
            ret = bytes(self.buf)
            self.buf.clear()
            return ret
        else:
            data = await self.upstream.read(n)
            if not data:
                return b''

            needed_till_full_block = -len(data) % self.block_size
            if needed_till_full_block > 0:
                data += await self.upstream.readexactly(needed_till_full_block)
            return self.decryptor.decrypt(data)
