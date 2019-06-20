
class DataCenter:
    """Telegram Data centers information

    Attributes:
        PORT (``int``)
            Data centers General Port
        IPV4 (``list``)
            List of IPv4 Data Center addresses.
        IPV6 (``list``)
            List of IPv6 Data Center addresses.
    """
    PORT = 443

    IPV4 = [
        "149.154.175.50",
        "149.154.167.51",
        "149.154.175.100",
        "149.154.167.91",
        "149.154.171.5"
    ]

    IPV6 = [
        "2001:b28:f23d:f001::a",
        "2001:67c:04e8:f002::a",
        "2001:b28:f23d:f003::a",
        "2001:67c:04e8:f004::a",
        "2001:b28:f23f:f005::a"
    ]
