import sys
from .utils import setup_files_limit
from .proxy import MTProxy


def main(args: list=sys.argv[1:]):
    """The main routine."""
    setup_files_limit()

    proxy = MTProxy()

    if args is not None and len(args) >= 1:
        config_file = args[0]
        proxy.load_from_file(config_file)

    proxy.show_data()
    proxy.start()
    proxy.run_until_disconnected()


if __name__ == "__main__":
    main(sys.argv[1:])
