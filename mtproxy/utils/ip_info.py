from .ext import get_ip_from_url


class IPInfo:

    PREFER_IPV6 = False
    IPV4 = None
    IPV6 = None

    IPV4_URL1 = "http://v4.ident.me/"
    IPV4_URL2 = "http://ipv4.icanhazip.com/"

    IPV6_URL1 = "http://v6.ident.me/"
    IPV6_URL2 = "http://ipv6.icanhazip.com/"

    def __new__(cls, prefer_ipv6: bool=PREFER_IPV6):
        ipv4 = get_ip_from_url(cls.IPV4_URL1) or get_ip_from_url(cls.IPV4_URL2)
        ipv6 = get_ip_from_url(cls.IPV6_URL1) or get_ip_from_url(cls.IPV6_URL2)

        if prefer_ipv6:
            if ipv6:
                print("IPv6 found, using it for external communication")
            else:
                prefer_ipv6 = False

        cls.PREFER_IPV6 = prefer_ipv6
        cls.IPV4 = ipv4
        cls.IPV6 = ipv6

        # instance = super(IP_Info, cls).__new__(cls)
        # return instance

        return cls
