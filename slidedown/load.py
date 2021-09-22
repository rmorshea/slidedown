import os
from pathlib import Path
from typing import Any, Dict, List, Callable, Tuple
from idom.core.proto import VdomDict

import markdown
import idom
from idom.utils import html_to_vdom


HERE = Path(__file__).parent


def use_slides(
    path_to_markdown_slides, initial_slide_index: int
) -> Tuple[List[VdomDict], Callable[[int], None]]:
    slides_path = Path(path_to_markdown_slides)
    project_path = Path(path_to_markdown_slides).parent

    all_slides = idom.hooks.use_memo(
        lambda: load_slides(project_path, slides_path),
        args=[project_path, slides_path],
    )

    visible_slide_index, set_visible_slide_index = idom.hooks.use_state(
        initial_slide_index
    )

    for index, slide in enumerate(all_slides):
        slide_attrs = slide["attributes"]
        if index == visible_slide_index:
            slide_attrs["id"] = "slide"
        else:
            slide_attrs.pop("id", None)
            slide_attrs["style"]["display"] = "none"

    return all_slides, visible_slide_index, set_visible_slide_index


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
        slide_element = idom.html.div(
            {"style": {"display": "block"}}, header, *nodes[start:stop]
        )
        slides.append(slide_element)

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
