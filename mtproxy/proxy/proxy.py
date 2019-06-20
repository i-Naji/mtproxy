from functools import partial
import asyncio
import socket
import urllib.parse
from configparser import ConfigParser
from .connection_handler import ConnectionHandler
from ..utils import IPInfo, AsyncTools, User
from ..config import Config


class MTProxy:
    """MtProto Proxy Class.

    Args:
        loop (:class:`asyncio.DefaultEvent_loopPolicy`, *optional*)
            Event loop, can be ignored.
        port (``int``, *optional*)
            The Port that Proxy listening to.
        fast_mode (``bool``, *optional*)
            if True, disables telegram to client traffic re-encryption, faster but less secure.
        prefer_ipv6 (``bool``, *optional*)
            if IPv6 available, use it by default.
        secure_only (``bool``, *optional*)
            if True, Don't allow to connect in not-secure mode.
        listen_addr_ipv4 (``str``, *optional*)
            Listen address for IPv4.
        listen_addr_ipv6 (``str``, *optional*)
            Listen address for IPv6.
        client_handshake_timeout (``int``, *optional*)
            Drop client after this timeout if the handshake fail.
        client_keepalive (``int``, *optional*)
            Keep alive period for clients in secs.
        client_ack_timeout (``int``, *optional*)
            if client doesn't confirm data for this number of seconds, it is dropped
        server_connect_timeout (``int``, *optional*)
            Telegram servers connect timeout in seconds.
        to_client_buffer_size (``int``, *optional*)
            Max socket buffer size to the client direction, the more the faster, but more RAM hungry.
        to_server_buffer_size (``int``, *optional*)
            Max socket buffer size to the telegram servers direction.
        block_mode (``bool``, *optional*)
            if True, Drop client if first packet is bad.
        reply_check_length (``int``, *optional*)
            Length of used handshake randoms for active fingerprinting protection.
        ipv4 (``str``, *optional*)
            IPv4 address to show data. if Ignored, will be Obtained.
        ipv6 (``sre``, *optional*)
            IPv6 address to show data. if Ignored, will be Obtained.
    """

    __slots__ = {'config', '_loop', 'server_v4', 'server_v6', 'is_connected', '_disconnected'}

    def __init__(self,
                 loop=None,
                 port: int = 8585,
                 fast_mode: bool = True,
                 prefer_ipv6: bool = socket.has_ipv6,
                 secure_only: bool = False,
                 listen_addr_ipv4: str = '0.0.0.0',
                 listen_addr_ipv6: str = '::',
                 client_handshake_timeout: int = 10,
                 client_keepalive: int = 10 * 60,
                 client_ack_timeout: int = 5 * 60,
                 server_connect_timeout: int = 10,
                 to_client_buffer_size: int = 131072,
                 to_server_buffer_size: int = 65536,
                 block_mode: bool = True,
                 reply_check_length: int=32768,
                 ipv4: str = None,
                 ipv6: str = None,):

        ip_info = IPInfo()

        if ipv4 is None:
            ipv4 = ip_info.IPV4

        if ipv6 is None:
            ipv6 = ip_info.IPV6

        if ipv6 is None:
            prefer_ipv6 = False

        self.config = Config(port=port,
                             fast_mode=fast_mode,
                             prefer_ipv6=prefer_ipv6,
                             secure_only=secure_only,
                             listen_addr_ipv4=listen_addr_ipv4,
                             listen_addr_ipv6=listen_addr_ipv6,
                             client_keepalive=client_keepalive,
                             client_handshake_timeout=client_handshake_timeout,
                             client_ack_timeout=client_ack_timeout,
                             server_connect_timeout=server_connect_timeout,
                             to_client_buffer_size=to_client_buffer_size,
                             to_server_buffer_size=to_server_buffer_size,
                             block_mode=block_mode,
                             reply_check_length=reply_check_length,
                             ipv4=ipv4,
                             ipv6=ipv6)

        self.server_v4 = None
        self.server_v6 = None

        self._loop = loop if loop else AsyncTools.get_loop()
        self._loop.set_exception_handler(AsyncTools.loop_exception_handler)

        self.is_connected = False
        self._disconnected = None

    def start(self):
        """Start MTProto Proxy

        Raises:
            :class:`ConnectionError`: if Proxy is already is connected.
        """
        if self.is_connected:
            raise ConnectionError("Proxy has already been started")

        self.is_connected = True

        reuse_port = hasattr(socket, "SO_REUSEPORT")

        handle_client = partial(ConnectionHandler.create, config=self.config)

        c_v4 = asyncio.start_server(handle_client, self.config.listen_addr_ipv4, self.config.port,
                                    limit=self.config.to_server_buffer_size,
                                    reuse_port=reuse_port, loop=self._loop)

        self.server_v4 = self._loop.run_until_complete(c_v4)

        if socket.has_ipv6:
            c_v6 = asyncio.start_server(handle_client, self.config.listen_addr_ipv6, self.config.port,
                                        limit=self.config.to_server_buffer_size, reuse_port=reuse_port, loop=self._loop)
            self.server_v6 = self._loop.run_until_complete(c_v6)

        if self._disconnected is None or self._disconnected.done():
            self._disconnected = self._loop.create_future()

    def run_until_disconnected(self):
        if self._loop.is_running():
            return self.disconnected
        try:
            return self._loop.run_until_complete(self.disconnected)
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect()

    @property
    def disconnected(self):
        return asyncio.shield(self._disconnected, loop=self._loop)

    def disconnect(self):

        if not self.is_connected:
            raise ConnectionError('Proxy is already disconnected!')

        self.is_connected = False

        if self.server_v4:
            self.server_v4.close()

        if self.server_v6:
            self.server_v6.close()

        # if self._disconnected and not self._disconnected.done():
        #    self._disconnected.set_result(None)

    def load_from_file(self, config_file: str):
        """Load config data and users from file

        Args:
            config_file (``str``)
                config file path
        """
        parser = ConfigParser()
        parser.read(config_file)

        settings = {
            str: [
                "listen_addr_ipv4", "listen_addr_ipv6", "ipv4", "ipv6"
            ],
            int: [
                "port", "to_client_buffer_size", "to_server_buffer_size",
                "client_keepalive", "client_handshake_timeout", "client_ack_timeout", "server_connect_timeout"
            ],
            bool: [
                "prefer_ipv6", "fast_mode", "secure_only", "block_mode"
            ],
        }
        if parser.has_section("mtproxy"):
            for order, options in settings.items():
                for option in options:
                    value = parser.get("mtproxy", option)
                    if value is not None:
                        setattr(self.config, option, order(value))

        if parser.has_section("mtproxy:users"):
            self.config.users.extend(
                [User(name, key) for name, key in parser._sections["mtproxy:users"].items() if name != "__name__"]
            )

    def show_data(self):
        """Print Proxy information"""
        ip_addrs = [ip for ip in [self.config.ipv4, self.config.ipv6] if ip]
        if not ip_addrs:
            ip_addrs = ["YOUR_IP"]
        for user in self.config.users:
            name, secret = user.name, user.secret
            for ip in ip_addrs:
                params = {"server": ip, "port": self.config.port, "secret": secret}
                if not self.config.secure_only:
                    params_encodeded = urllib.parse.urlencode(params, safe=':')
                    print("{}: tg://proxy?{}".format(name, params_encodeded))
                params['secret'] = 'dd' + secret
                params_encodeded = urllib.parse.urlencode(params, safe=':')
                print("{}: tg://proxy?{}".format(name, params_encodeded))

            if secret in ["00000000000000000000000000000000", "0123456789abcdef0123456789abcdef"]:
                msg = "The default secret {} is used, this is not recommended".format(secret)
                print(msg)
