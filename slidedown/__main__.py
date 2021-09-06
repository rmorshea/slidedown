"""Slidedown

Make slideshows with markdown.

Usage:
  slidedown <filepath> [ <start-at-slide-number> ] [ --no-auto-open ] [ --host=<host> ] [ --port=<port> ]
"""

import webbrowser
from pathlib import Path
from typing import Dict, Any, Callable

import idom
from idom.server.sanic import PerClientStateServer
from sanic import Sanic
from docopt import docopt


from .slides import Slidedeck

HERE = Path(__file__).parent

DEFAULTS: Dict[str, Any] = {
    "--host": "127.0.0.1",
    "--port": 5678,
    "<start-at-slide-number>": 1,
}

REMAP: Dict[str, str] = {
    "<filepath>": "filepath",
    "<start-at-slide-number>": "start_at_slide_number",
    "--host": "host",
    "--port": "port",
    "--no-auto-open": "no_auto_open",
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

    app = Sanic()

    app.static("_static", str(HERE / "static"))

    idom_server = PerClientStateServer(
        lambda: Slidedeck(
            int(arguments["start_at_slide_number"]), arguments["filepath"]
        ),
        app=app,
    )

    run_options = {"host": arguments["host"], "port": arguments["port"]}

    if not arguments["no_auto_open"]:
        thread = idom_server.run_in_thread(**run_options)
        webbrowser.open(f"http://{run_options['host']}:{run_options['port']}")
        thread.join()
    else:
        idom_server.run(**run_options)
