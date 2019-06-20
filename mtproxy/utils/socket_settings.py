import socket


def try_setsockopt(sock, level, option, value):
    try:
        sock.setsockopt(level, option, value)
    except OSError:
        pass


def set_keepalive(sock, interval=40, attempts=5):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    if hasattr(socket, "TCP_KEEPIDLE"):
        try_setsockopt(sock, socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, interval)
    if hasattr(socket, "TCP_KEEPINTVL"):
        try_setsockopt(sock, socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval)
    if hasattr(socket, "TCP_KEEPCNT"):
        try_setsockopt(sock, socket.IPPROTO_TCP, socket.TCP_KEEPCNT, attempts)


def set_ack_timeout(sock, timeout):
    if hasattr(socket, "TCP_USER_TIMEOUT"):
        try_setsockopt(sock, socket.IPPROTO_TCP, socket.TCP_USER_TIMEOUT, timeout*1000)


def set_bufsizes(sock, recv_buf, send_buf):
    try_setsockopt(sock, socket.SOL_SOCKET, socket.SO_RCVBUF, recv_buf)
    try_setsockopt(sock, socket.SOL_SOCKET, socket.SO_SNDBUF, send_buf)
