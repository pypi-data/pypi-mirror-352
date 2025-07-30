import argparse
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path

PARSER = argparse.ArgumentParser(description='Place several files on the clipboard')
PARSER.add_argument('file', nargs="*")

def path_to_url(path):
    url = urllib.parse.quote(str(path.absolute()))
    url = urllib.parse.urljoin('file:', url)
    return url

def main():
    args = PARSER.parse_args()
    list_string = "\n".join([path_to_url(Path(f)) for f in args.file])

    if sys.platform != "linux":
        raise Exception('Only implemented for linux. Patches for other systems will quickly be merged.')

    if os.getenv("DISPLAY"):
        p = subprocess.Popen(["xclip", "-t", "text/uri-list", "-selection", "CLIPBOARD"], stdin=subprocess.PIPE)
        p.communicate(list_string.encode('utf8'))
    elif os.getenv("WAYLAND_DISPLAY"):
        p = subprocess.Popen(["wl-copy", "-t", "text/uri-list"], stdin=subprocess.PIPE)
        p.communicate(list_string.encode('utf8'))
    if p.wait() != 0:
        raise Exception('Command failed')
