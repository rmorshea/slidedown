"""Slidedown

Make slideshows with markdown.

Usage:
  slidoml <filepath> [ --ip=<ip> ] [ --port=<port> ] [ --markdown-style=<style> ] [ --code-style=<style> ]
"""

from idom.server.sanic import PerClientState
from docopt import docopt
from typing import Dict, Any, Callable

from .slides import Slidedeck

DEFAULTS: Dict[str, Any] = {
    "--ip": "127.0.0.1",
    "--port": 5678,
    "--markdown-style": "github",
    "--code-style": "default",
}

REMAP: Dict[str, str] = {
    "<filepath>": "filepath",
    "--markdown-style": "markdown_style",
    "--code-style": "code_style",
    "--ip": "ip",
    "--port": "port",
}

CAST: Dict[str, Callable[[str], Any]] = {"--port": int}


def run() -> None:
    arguments = docopt(__doc__, version="0.1.0")

    for k, v in DEFAULTS.items():
        if arguments[k] is None:
            arguments[k] = v

    for k, v in CAST.items():
        arguments[k] = v(arguments[k])

    for old_k, new_k in REMAP.items():
        arguments[new_k] = arguments.pop(old_k)

    server = PerClientState(
        Slidedeck,
        arguments["filepath"],
        arguments["markdown_style"],
        arguments["code_style"],
    )
    server.run(arguments["ip"], arguments["port"])
