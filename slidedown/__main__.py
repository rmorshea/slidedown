"""Slidedown

Make slideshows with markdown.

Usage:
  slidedown <filepath> [ <start-at-slide-number> ] [ --no-auto-open ] [ --no-reload ]
                       [ --reload-delay=<delay> ] [ --host=<host> ] [ --port=<port> ]
"""

import os
import time
import webbrowser
from pathlib import Path
from typing import Dict, Any, Callable, NamedTuple, Optional

from idom.server.sanic import PerClientStateServer
from idom.server.proto import Server
from sanic import Sanic
from docopt import docopt


from .slides import Slidedeck

HERE = Path(__file__).parent
UNDEFINED = object()


class ArgSpec(NamedTuple):
    name: str
    default: Any = UNDEFINED
    cast: Optional[Callable[[str], Any]] = None


ARG_SPECS = {
    "<filepath>": ArgSpec("filepath"),
    "<start-at-slide-number>": ArgSpec("start_at_slide_number", 1, int),
    "--host": ArgSpec("host", "127.0.0.1"),
    "--port": ArgSpec("port", 5678, int),
    "--no-auto-open": ArgSpec("no_auto_open"),
    "--no-reload": ArgSpec("no_reload"),
    "--reload-delay": ArgSpec("reload_delay", 1, float),
}


class Arguments(NamedTuple):
    filepath: str
    start_at_slide_number: int
    host: str
    port: int
    no_auto_open: bool
    no_reload: bool
    reload_delay: float


def run() -> None:
    raw_arguments = docopt(__doc__, version="0.1.0")

    processes_arguments: Dict[str, Any] = {}
    for arg, spec in list(ARG_SPECS.items()):
        if raw_arguments[arg] is None:
            del raw_arguments[arg]
            value = spec.default
        else:
            value = raw_arguments.pop(arg, spec.default)

        if value is UNDEFINED:
            raise ValueError(f"Internal failure - {arg} requires a value")

        if spec.cast is not None:
            try:
                value = spec.cast(value)
            except Exception:
                print(f"Invalid value for {arg}")
                exit(1)

        processes_arguments[spec.name] = value

    if raw_arguments:
        raise RuntimeError(f"Internal failure - unconsumed arguments {raw_arguments}")

    arguments = Arguments(**processes_arguments)

    app = Sanic()

    app.static("_static", str(HERE / "static"))

    idom_server = PerClientStateServer(
        lambda: Slidedeck(arguments.start_at_slide_number, arguments.filepath),
        app=app,
    )

    _run_server(
        idom_server,
        {"host": arguments.host, "port": arguments.port},
        not arguments.no_auto_open,
        (
            None
            if arguments.no_reload
            else _make_file_did_change_callback(Path(arguments.filepath))
        ),
        arguments.reload_delay,
    )


def _make_file_did_change_callback(file: Path) -> Callable[[], bool]:
    last_modified = os.path.getmtime(file)

    def did_change() -> bool:
        nonlocal last_modified
        new_last_modified = os.path.getmtime(file)
        if new_last_modified != last_modified:
            print(f"File changed: {file}")
            last_modified = new_last_modified
            return True
        else:
            return False

    return did_change


def _run_server(
    server: Server,
    server_run_options: Dict[str, Any],
    open_browser: bool,
    should_reload: Optional[Callable[[], bool]],
    reload_delay: float,
) -> None:
    if not should_reload:
        _run_server_no_reload(server, server_run_options, open_browser)
        return None

    thread = server.run_in_thread(**server_run_options)

    if open_browser:
        _open_browser(server_run_options)

    while True:
        time.sleep(reload_delay)
        if should_reload():
            print("reloading...")
            server.stop(3)
            thread.join(3)
            thread = server.run_in_thread(**server_run_options)


def _run_server_no_reload(
    server: Server,
    server_run_options: Dict[str, Any],
    open_browser: bool,
) -> None:
    if open_browser:
        thread = server.run_in_thread(**server_run_options)
        _open_browser(server_run_options)
        thread.join()
    else:
        server.run(**server_run_options)


def _open_browser(server_run_options: Dict[str, Any]) -> None:
    webbrowser.open(f"http://{server_run_options['host']}:{server_run_options['port']}")
