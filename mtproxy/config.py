

class Config:
    """MTProto Proxy Config.
    """
    users = []
    n = 0
    def __init__(self,
                 port=None,
                 fast_mode=None,
                 prefer_ipv6=None,
                 secure_only=None,
                 listen_addr_ipv4=None,
                 listen_addr_ipv6=None,
                 client_handshake_timeout=None,
                 client_keepalive=None,
                 client_ack_timeout=None,
                 server_connect_timeout=None,
                 to_client_buffer_size=None,
                 to_server_buffer_size=None,
                 block_mode=None,
                 reply_check_length=None,
                 ipv4=None,
                 ipv6=None):
        self.port = port
        self.fast_mode = fast_mode
        self.prefer_ipv6 = prefer_ipv6
        self.secure_only = secure_only
        self.listen_addr_ipv4 = listen_addr_ipv4
        self.listen_addr_ipv6 = listen_addr_ipv6
        self.client_handshake_timeout = client_handshake_timeout
        self.client_keepalive = client_keepalive
        self.client_ack_timeout = client_ack_timeout
        self.server_connect_timeout = server_connect_timeout
        self.to_client_buffer_size = to_client_buffer_size
        self.to_server_buffer_size = to_server_buffer_size
        self.block_mode = block_mode
        self.reply_check_length = reply_check_length
        self.ipv4 = ipv4
        self.ipv6 = ipv6
