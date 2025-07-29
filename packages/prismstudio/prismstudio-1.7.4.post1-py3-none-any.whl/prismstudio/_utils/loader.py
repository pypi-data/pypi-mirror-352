import time
import logging
import requests
import itertools
import sys
from itertools import cycle
from threading import Thread
from IPython import get_ipython
try:
    ipython = get_ipython()
    if 'ipykernel' in str(ipython):
        from tqdm.auto import tqdm
    else:
        from tqdm import tqdm
except ImportError:
    from tqdm import tqdm
from shutil import get_terminal_size

from .._common.config import ModeSetting

logger = logging.getLogger()


class Loader:
    def __init__(self, desc="Loading...", end="Done!", timeout=0.1):
        """
        A loader-like context manager

        Args:
            desc (str, optional): The loader's description. Defaults to "Loading...".
            end (str, optional): Final print. Defaults to "Done!".
            timeout (float, optional): Sleep time between prints. Defaults to 0.1.
        """
        ms = ModeSetting()
        self.quiet_mode = ms.QUIET_MODE
        self.desc = desc
        self.end = end
        self.timeout = timeout
        self._thread = None
        self._running = False
        self.frames = itertools.cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"])

    def start(self):
        self._running = True
        while self._running:
            frame = next(self.frames)
            sys.stdout.write(f"\r{self.desc} {frame}")
            sys.stdout.flush()
            time.sleep(self.timeout)

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join()

    def __enter__(self):
        self._running = True
        import threading
        self._thread = threading.Thread(target=self.start)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._running = False
        self._thread.join()
        sys.stdout.write(f"\r{self.end}\n")
        sys.stdout.flush()


def download(links):
    ms = ModeSetting()
    r = requests.get(url=links, stream=(not ms.QUIET_MODE))
    if ms.QUIET_MODE:
        result = r.content
    else:
        #print("Downloading")
        r.raise_for_status()
        result = []
        with tqdm(desc="Downloading", total=int(r.headers["content-length"]), unit="B", unit_scale=True, unit_divisor=1024) as pbar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk is not None:  # filter out keep-alive new chunks
                    result.append(chunk)
                    pbar.update(len(chunk))
                    sys.stdout.flush()  # Ensure the output is flushed
        result = b"".join(result)

    return result
