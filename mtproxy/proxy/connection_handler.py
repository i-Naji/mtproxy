import asyncio
from .streams import ClientSteamProtocol, ServerStreamProtocol
from ..config import Config


class ConnectionHandler:

    __slots__ = {'config', 'client', 'server'}

    def __init__(self, config: Config, client: ClientSteamProtocol=None, server: ServerStreamProtocol=None):
        self.config = config
        self.client = client
        self.server = server

    @classmethod
    async def create(cls, reader, writer, *, config: Config=None):
        self = cls(config, ClientSteamProtocol(config, reader, writer))
        try:
            await self.handle_initial_handshake()
        except (asyncio.IncompleteReadError, ConnectionResetError, TimeoutError):
            pass
        finally:
            writer.transport.abort()

    async def handle_initial_handshake(self):
        self.client.init_socket(True)
        try:
            await asyncio.wait_for(
                self.client.handle_handshake(), timeout=self.config.client_handshake_timeout
            )
        except asyncio.TimeoutError:
            return

        if not self.client.handshaked:
            return

        (dc_ip, dc_port) = await self.client.get_telegram_dc()
        try:
            await self.open_telegram_connection(dc_ip, dc_port)
        except ConnectionRefusedError:
            print("Got connection refused while trying to connect to", dc_ip, dc_port)
            return
        except (OSError, asyncio.TimeoutError):
            print("Unable to connect to", dc_ip, dc_port)
            return

        if self.server is None:
            return

        self.server.init_socket()

        await self.server.handle_handshake()

        if not self.server.handshaked:
            return

        if self.config.fast_mode:
            self.client.release_writer()
            self.server.release_reader()
        self.config.n += 1
        n = self.config.n
        telegram_to_client = self.server.reply_stream(n,
            self.client.writer,
            self.config.to_client_buffer_size,
            self.config.block_mode
        )
        client_to_telegram = self.client.reply_stream(n,self.server.writer, self.config.to_server_buffer_size)

        task_tg_to_clt = asyncio.ensure_future(telegram_to_client)
        task_clt_to_tg = asyncio.ensure_future(client_to_telegram)

        await asyncio.wait([task_tg_to_clt, task_clt_to_tg], return_when=asyncio.FIRST_COMPLETED)

        task_tg_to_clt.cancel()
        task_clt_to_tg.cancel()

        self.server.writer.close()

    async def open_telegram_connection(self, address: str, port: int, max_attempts: int=3):

        for _ in range(max_attempts):
            try:
                task = asyncio.open_connection(address, port, limit=self.config.to_client_buffer_size)
                reader, writer = await asyncio.wait_for(task, timeout=self.config.server_connect_timeout)
                self.server = ServerStreamProtocol(
                    self.config, reader, writer, self.client.proto_tag, self.client.key
                )
            except (OSError, asyncio.TimeoutError) as E:
                if _ >= max_attempts:
                    raise E
