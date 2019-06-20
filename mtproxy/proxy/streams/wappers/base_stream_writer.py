class LayeredStreamWriterBase:
    __slots__ = {'upstream'}

    def __init__(self, upstream):
        self.upstream = upstream

    def write(self, data, extra: dict=None):
        return self.upstream.write(data)

    def write_eof(self):
        return self.upstream.write_eof()

    async def drain(self):
        return await self.upstream.drain()

    def close(self):
        return self.upstream.close()

    def abort(self):
        return self.upstream.transport.abort()

    @property
    def transport(self):
        return self.upstream.transport
