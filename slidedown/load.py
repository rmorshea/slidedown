from pathlib import Path
from typing import Any, Dict, List

import markdown
import idom
from idom.utils import html_to_vdom
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name


HERE = Path(__file__).parent


def use_slides(slides_path):
    return idom.hooks.use_memo(lambda: load_slides(slides_path), args=[slides_path])


def load_slides(slides_path):
    with open(slides_path, "r") as f:
        return markdown_to_slidedeck(f.read())


def markdown_to_slidedeck(md: str) -> List[Dict[str, Any]]:
    nodes = html_to_vdom(
        markdown.markdown(
            md,
            extensions=["fenced_code", "codehilite"],
            extension_configs={
                "codehilite": {
                    "use_pygments": True,
                    "noclasses": True,
                    "guess_lang": False,
                }
            },
        ),
        _embedded_idom_script,
    )["children"]

    slide_boundaries = []
    for i, n in enumerate(nodes):
        if isinstance(n, dict):
            if n.get("tagName") == "h1":
                slide_boundaries.append(i)
    slide_boundaries.append(len(nodes))

    header = idom.html.div({"id": "slide-header"}, *nodes[0 : slide_boundaries[0]])

    slides = []
    for j in range(len(slide_boundaries) - 1):
        start, stop = slide_boundaries[j : j + 2]
        slides.append((header, *nodes[start:stop]))

    return slides


def _embedded_idom_script(node):
    if "data-idom" in node.get("attributes", {}):
        with open(node["attributes"]["data-idom"], "r") as f:
            script = f.read()
        return ExecPythonScript(script)
    return node


@idom.element
def ExecPythonScript(script: str):
    env = {}
    exec(script, env)
    Main = env.get("Main")
    if not callable(Main):
        raise ValueError("Python script must have a 'Main' element")
    return Main()
