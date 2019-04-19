"""Slidedown

Make slideshows with markdown.

Usage:
  slidoml <filepath> [ --ip=<ip> ] [ --port=<port> ] [ --markdown-style=<style> ] [ --code-style=<style> ]
"""
import idom
from docopt import docopt
import os

from .parse import markdown_to_slidedeck


HERE = os.path.dirname(__file__)

defaults = {
    "--ip": "127.0.0.1",
    "--port": 5678,
    "--markdown-style": "github",
    "--code-style": "default",
}

cast = {"--port": int}


def run():
    arguments = docopt(__doc__, version="0.1.0")

    for k, v in defaults.items():
        if arguments[k] is None:
            arguments[k] = v

    for k, v in cast.items():
        arguments[k] = v(arguments[k])

    with open(arguments["<filepath>"], "r") as f:
        slides = markdown_to_slidedeck(f.read())

    markdown_style_path = arguments["--markdown-style"]
    if not markdown_style_path.endswith(".css"):
        markdown_style_path = os.path.join(
            HERE, "styles", "markdown", markdown_style_path + ".css"
        )
    with open(markdown_style_path, "r") as f:
        markdown_style = f.read()

    code_style_path = arguments["--code-style"]
    if not code_style_path.endswith(".css"):
        code_style_path = os.path.join(
            HERE, "styles", "pygments", code_style_path + ".css"
        )
    with open(code_style_path, "r") as f:
        code_style = f.read()

    server = idom.SimpleServer(Slidedeck, slides, markdown_style, code_style)
    server.run(arguments["--ip"], arguments["--port"])


@idom.element(state="slides, markdown_style, code_style")
def Slidedeck(self, slides, markdown_style, code_style, index=0):
    events = idom.Events()

    @events.on("KeyDown")
    def shift_slide(key):
        if key == "ArrowLeft":
            new_index = index - 1
        else:
            new_index = index + 1
        self.update(index=new_index % len(slides))

    return idom.nodes.div(
        idom.nodes.style(code_style),
        idom.nodes.style(markdown_style),
        idom.nodes.div(
            slides[index],
            id="slide",
        ),
        eventHandlers=events,
        tabIndex=0,
        style={"outline": "none", "height": "100%", "width": "100%"},
    )
