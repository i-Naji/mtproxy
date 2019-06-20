from .base_stream_writer import LayeredStreamWriterBase


class CryptoWrappedStreamWriter(LayeredStreamWriterBase):

    __slots__ = {'upstream', 'encryptor', 'block_size'}

    def __init__(self, upstream, encryptor, block_size=1):
        self.upstream = upstream
        self.encryptor = encryptor
        self.block_size = block_size

    def write(self, data, extra: dict=None):
        if len(data) % self.block_size != 0:
            print("BUG: writing %d bytes not aligned to block size %d" % (
                      len(data), self.block_size))
            return 0
        q = self.encryptor.encrypt(data)
        return self.upstream.write(q)
