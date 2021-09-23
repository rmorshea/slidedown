import sys
from importlib import import_module, reload as reload_module
from pathlib import Path
from typing import Any, Dict, List, Callable, Tuple, TypeVar
from idom.core.proto import VdomDict

import markdown
import idom
from idom.utils import html_to_vdom


HERE = Path(__file__).parent


_T = TypeVar("_T")


def use_const(func: Callable[..., _T], *args: Any, **kwargs: Any) -> _T:
    return idom.hooks.use_state(lambda: func(*args, **kwargs))[0]


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
    abs_project_path = str(project_path.absolute())
    if abs_project_path not in sys.path:
        sys.path.insert(0, abs_project_path)

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
        slide_element = idom.html.div(
            {"style": {"display": "block"}}, header, *nodes[start:stop]
        )
        slides.append(slide_element)

    return slides


def _embedded_idom_script(node):
    node_attrs = node.get("attributes", {})
    if "data-idom" in node_attrs:
        module_name = node["attributes"]["data-idom"]

        if module_name in sys.modules:
            reload_module(sys.modules[module_name])
        module = import_module(module_name)

        Main = getattr(module, "Main", None) or getattr(module, "main", None)

        if not callable(Main):
            raise ValueError(
                f"Module {module_name!r} does not contain callable 'Main' or 'main' attribute"
            )

        params = {
            k.split("-", 1)[1].replace("-", "_"): v
            for k, v in node_attrs.items()
            if k.startswith("data-") and k != "data-idom"
        }

        result = Main(**params)

        non_data_attrs = {
            k: v for k, v in node_attrs.items() if not k.startswith("data-")
        }

        return idom.html.div(non_data_attrs, result)

    return node
