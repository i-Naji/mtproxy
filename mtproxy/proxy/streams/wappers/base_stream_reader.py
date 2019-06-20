class LayeredStreamReaderBase:
    __slots__ = {'upstream'}

    def __init__(self, upstream):
        self.upstream = upstream

    async def read(self, n):
        return await self.upstream.read(n)

    async def readexactly(self, n):
        return await self.upstream.readexactly(n)
