# MTProxy
A fully [OOP](https://en.wikipedia.org/wiki/Object-oriented_programming)
[Asynchronous](https://docs.python.org/3/library/asyncio.html) **Python
3** MT-Proto proxy



## Features
* **Easy to use:** you can easily use it
* **Lightweight** less resources as possible but not by losing
  maintainability.
* **Fully-asynchronous:** it runs asynchronously
* **High-performance:** processes a lot of connections
* **Block-Mode** Protection from
  [replay attacks](https://habr.com/ru/post/452144/) used to detect
  proxies in some countries

## Installation
To install last stable release from pypi:
```
$ pip3 install mtproxy
```
or with [uvloop](https://uvloop.readthedocs.io/) as extra requirement
(recommended):
```
$ pip3 install mtproxy[fast]
```
uvloop makes asyncio fast.

## Usage
#### To launch with custom config
```.buildoutcfg
# config.ini

#proxy settings
[mtproxy]

# port = 8585
## The Port that Proxy listening to. 8585 by default

# fast_mode = ture
# true by deaultif True, disables telegram to client traffic re-encryption, faster but less secure.

# prefer_ipv6 = ture
# if IPv6 available, use it by default.

# secure_only = false
# Don't allow to connect in not-secure mode. false by default

# listen_addr_ipv4 = 0.0.0.0
# Listen address for IPv4. '0.0.0.0' by default

# listen_addr_ipv6 = ::
# Listen address for IPv6 by default

# client_handshake_timeout = 10
# Drop client after this timeout if the handshake fail, 10 by default

# client_keepalive = 600
# Keep alive period for clients in secs, 600 by default.

# client_ack_timeout = 300
# if client doesn't confirm data for this number of seconds, it is dropped, 300 by default.

# server_connect_timeout = 10
# Telegram servers connect timeout in seconds, 10 by default/.

# to_client_buffer_size = 131072
# Max socket buffer size to the client direction, the more the faster, but more RAM hungry, 131072 by default.

# to_server_buffer_size = 65536
# Max socket buffer size to the telegram servers direction, 65536 by default.

# block_mode = true
# Drop client if first packet is bad, true by default.

# reply_check_length = 
# Length of used handshake randoms for active fingerprinting protection, 32768 by default.

# ipv4 = 
# IPv4 address to show data, if Ignored, will be Obtained.

# ipv6 = 
# IPv6 address to show data, if Ignored, will be Obtained.


# proxy users section.
[mtproxy:users]
# name_of_user = proxy_secret_key
HemMm = 7e7ee7be6b40378e593c36433294b03c
```
launch proxy: 
```bash
mtproxy config.ini

# mtproxy CONFIG_FILE_NAME
```


### Special Thanks to [alexbers](https://github.com/alexbers) for his grate [project](https://github.com/alexbers/mtprotoproxy) 

## License
[MIT](https://choosealicense.com/licenses/mit/)