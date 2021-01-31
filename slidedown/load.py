import os
from pathlib import Path
from typing import Any, Dict, List

import markdown
import idom
from idom.utils import html_to_vdom
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name


HERE = Path(__file__).parent


def use_slides(path_to_markdown_slides):
    slides_path = Path(path_to_markdown_slides)
    project_path = Path(path_to_markdown_slides).parent
    return idom.hooks.use_memo(
        lambda: load_slides(project_path, slides_path), args=[project_path, slides_path]
    )


def load_slides(project_path, slides_path):
    with open(slides_path, "r") as f:
        return markdown_to_slidedeck(project_path, f.read())


def markdown_to_slidedeck(project_path: Path, md: str) -> List[Dict[str, Any]]:
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
        lambda node: _embedded_idom_script(project_path, node),
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


def _embedded_idom_script(project_path, node):
    if "data-idom" in node.get("attributes", {}):
        script_path = Path(node["attributes"]["data-idom"].replace("/", os.path.sep))
        if not os.path.isabs(script_path):
            script_path = project_path / script_path
        return ExecPythonScript(script_path.read_text(encoding="utf-8"))
    return node


@idom.component
def ExecPythonScript(script: str):
    env = {}
    exec(script, env)
    Main = env.get("Main")
    if not callable(Main):
        raise ValueError("Python script must have a 'Main' element")
    return Main()
