import sys
import asyncio


class AsyncTools:
    """contents mtproto proxy async tools"""

    @classmethod
    def get_loop(cls):

        AsyncTools.try_setup_uvloop()

        if sys.platform == "win32":
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)

        loop = asyncio.get_event_loop()

        return loop

    @staticmethod
    def try_setup_uvloop():
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass

    @staticmethod
    def loop_exception_handler(loop, context):
        exception = context.get("exception")
        transport = context.get("transport")
        if exception:
            if isinstance(exception, TimeoutError):
                if transport:
                    transport.abort()
                    return
            if isinstance(exception, OSError):
                IGNORE_ERRNO = {
                    10038,  # operation on non-socket on Windows, likely because fd == -1
                    121,  # the semaphore timeout period has expired on Windows
                }

                FORCE_CLOSE_ERRNO = {
                    113,  # no route to host

                }
                if exception.errno in IGNORE_ERRNO:
                    return
                elif exception.errno in FORCE_CLOSE_ERRNO:
                    if transport:
                        transport.abort()
                        return

        loop.default_exception_handler(context)
