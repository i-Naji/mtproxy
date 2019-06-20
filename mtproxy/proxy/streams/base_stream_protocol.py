import asyncio
from ...config import Config
from ...utils import set_keepalive, set_ack_timeout, set_bufsizes


class BaseStreamProtocol:

    ERROR_PACKET_DATA = b'l\xfe\xff\xff'
    __slots__ = {'config', 'proto_tag', 'key', '_stream_reader', '_stream_writer', 'ip', 'port',
                 'handshaked'}

    def __init__(self, config: Config, reader, writer, proto_tag=None, dec_key=None):
        self.config = config
        self._stream_reader = reader
        self._stream_writer = writer
        self.ip, self.port = writer.transport.get_extra_info('peername')[:2]
        self.proto_tag = proto_tag
        self.key = dec_key
        self.handshaked = False

    @property
    def reader(self) -> asyncio.StreamReader:
        return self._stream_reader

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._stream_writer

    def init_socket(self, ack: bool=False):
        socket = self.writer.get_extra_info("socket")
        set_keepalive(socket, self.config.client_keepalive, attempts=3)
        if ack:
            set_ack_timeout(socket, self.config.client_ack_timeout)
        set_bufsizes(socket, self.config.to_server_buffer_size, self.config.to_client_buffer_size)

    async def handle_handshake(self, *args, **kwargs):
        raise NotImplementedError

    async def reply_stream(self,n,  writer, read_buffer_size, block_if_first_pkt_bad=False):
        is_first_pkt = True
        try:
            while True:
                data = await self.reader.read(read_buffer_size)
                # protection against replay-based fingerprinting
                if is_first_pkt:
                    is_first_pkt = False
                    if block_if_first_pkt_bad and data == BaseStreamProtocol.ERROR_PACKET_DATA:
                        print("Active fingerprinting detected from %s, dropping it" % self.ip)
                        break
                if data:
                    writer.write(data)
                    await writer.drain()
                else:
                    print("Finished %s" % n)
                    break
            writer.write_eof()
            await writer.drain()

        except (OSError, asyncio.streams.IncompleteReadError) as e:
            print(e, n)
            pass
