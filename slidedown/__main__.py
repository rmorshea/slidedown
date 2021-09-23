"""Slidedown

Make slideshows with markdown.

Usage:
    slidedown <filepath>
        [ <start-at-slide-number> ]
        [ --host=<host> ]
        [ --port=<port> ]
        [ --no-reload ]
        [ --no-auto-open ]
        [ --reload-delay=<delay> ]
        [ --reload-watch=<pattern> ... ]
        [ --reload-ignore=<pattern> ... ]

Options:

--host=<host>
        The host where the slides will be served

--port=<port>
        The host port to server from

--no-reload
        Whether or not to reload when files change

--no-auto-open
        Whether to automatically open the browser

--reload-delay=<delay>
        How long to wait to check for file changes (default: 1s)

--reload-watch=<pattern>
        One or more glob patterns matching files that should be tracked
        for changes. When changes occur then the server will reload.
        Patterns should match paths in the same directory as <filepath>.

--reload-ignore=<pattern>
        One or more globa patterns matching files to ignore when
        tracking changes and determining whether to reload. Patterns
        should match paths in the same directory as <filepath>.
"""

import os
import re
import time
import webbrowser
from pathlib import Path
from typing import Dict, Any, Callable, NamedTuple, Optional, List

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
    "--reload-delay": ArgSpec("reload_delay", 2, float),
    "--reload-watch": ArgSpec("reload_watch"),
    "--reload-ignore": ArgSpec("reload_ignore"),
}


class Arguments(NamedTuple):
    filepath: str
    start_at_slide_number: int
    host: str
    port: int
    no_auto_open: bool
    no_reload: bool
    reload_delay: float
    reload_watch: List[re.Pattern]
    reload_ignore: List[re.Pattern]


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

    files_did_change = _make_file_did_change_callback(
        Path(arguments.filepath),
        arguments.reload_watch,
        arguments.reload_ignore,
    )

    _run_server(
        idom_server,
        {"host": arguments.host, "port": arguments.port},
        not arguments.no_auto_open,
        None if arguments.no_reload else files_did_change,
        arguments.reload_delay,
    )


def _make_file_did_change_callback(
    markdown_file: Path,
    watch_patterns: List[re.Pattern],
    ignore_patterns: List[re.Pattern],
) -> Callable[[], bool]:
    project_dir = markdown_file.parent

    def get_files_to_watch():
        files_to_watch = set()
        for watch_pat in watch_patterns:
            files_to_watch |= set(project_dir.glob(watch_pat))
        for ignore_pat in ignore_patterns:
            files_to_watch -= set(project_dir.glob(ignore_pat))
        files_to_watch.add(markdown_file)
        return files_to_watch

    def get_last_modified(should_print=False, latest_mtime: float = 0) -> float:
        changed_files = []

        for file in get_files_to_watch():
            file_mtime = os.path.getmtime(file)
            if file_mtime > latest_mtime:
                if should_print:
                    changed_files.append(file)
                latest_mtime = file_mtime

        if changed_files:
            print(f"File changed: {changed_files[0]}")
            if len(changed_files) > 1:
                print(f"{len(changed_files - 1)} more files also changed.")

        return latest_mtime

    last_modified = get_last_modified()

    def did_change() -> bool:
        nonlocal last_modified
        new_last_modified = get_last_modified(
            should_print=True, latest_mtime=last_modified
        )
        if new_last_modified != last_modified:
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
            print("Reloading...")
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
