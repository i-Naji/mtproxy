import urllib.request
import sys
import signal


def setup_files_limit():
    try:
        import resource
        soft_fd_limit, hard_fd_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (hard_fd_limit, hard_fd_limit))
    except (ValueError, OSError):
        print("Failed to increase the limit of opened files", flush=True, file=sys.stderr)
    except ImportError:
        pass


def get_ip_from_url(url):
    TIMEOUT = 5
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as f:
            if f.status != 200:
                raise Exception("Invalid status code")
            return f.read().decode().strip()
    except Exception:
        return None


def setup_debug():
    if hasattr(signal, 'SIGUSR1'):
        def debug_signal(signum, frame):
            import pdb
            pdb.set_trace()

        signal.signal(signal.SIGUSR1, debug_signal)
