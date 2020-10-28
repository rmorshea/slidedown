from pathlib import Path
from typing import Any, Dict, List

import cmarkgfm
import idom
from idom.utils import html_to_vdom
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name


HERE = Path(__file__).parent


def use_slides_and_styles(slides_path, markdown_style_path, code_style_path):
    return idom.hooks.use_memo(
        lambda: load_slides_and_styles(
            slides_path, markdown_style_path, code_style_path
        ),
        args=[slides_path, markdown_style_path, code_style_path],
    )


def load_slides_and_styles(slides_path, markdown_style_path, code_style_path):
    with open(slides_path, "r") as f:
        slides = markdown_to_slidedeck(f.read())

    if not markdown_style_path.endswith(".css"):
        markdown_style_path = HERE.joinpath(
            "styles", "markdown", markdown_style_path + ".css"
        )
    with open(markdown_style_path, "r") as f:
        markdown_style = f.read()

    if not code_style_path.endswith(".css"):
        code_style_path = HERE.joinpath("styles", "pygments", code_style_path + ".css")
    with open(code_style_path, "r") as f:
        code_style = f.read()

    return slides, markdown_style, code_style


def markdown_to_slidedeck(md: str) -> List[Dict[str, Any]]:
    nodes = html_to_vdom(
        cmarkgfm.github_flavored_markdown_to_html(md),
        _highlight_code,
        _idom_alternative,
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


def _highlight_code(node):
    if node["tagName"] == "pre":
        new_children = []
        new_node = {"tagName": "div", "children": new_children}
        for child in node["children"]:
            if isinstance(child, dict):
                if child["tagName"] == "code":
                    child["attributes"].setdefault("class", "language-text")
                    child = HiglightedCode(child)
            new_children.append(child)
        return new_node
    return node


def _idom_alternative(node):
    if "data-idom" in node.get("attributes", {}):
        with open(node["attributes"]["data-idom"], "r") as f:
            script = f.read()
        return ExecPythonScript(script)
    return node


@idom.element
def HiglightedCode(node):
    lang = node["attributes"]["class"].split("-", 1)[1]
    try:
        lexer = get_lexer_by_name(lang, stripall=True)
    except ClassNotFound:
        lexer = None
    if lexer:
        formatter = HtmlFormatter()
        text = "\n" + "\n".join(node["children"]).strip()
        result = html_to_vdom(
            highlight(text, lexer, formatter), _remove_extra_span_from_highlighted_code
        )
        return result
    return node


@idom.element
def ExecPythonScript(script: str):
    env = {}
    exec(script, env)
    Main = env.get("Main")
    if not callable(Main):
        raise ValueError("Python script must have a 'Main' element")
    return Main()


def _remove_extra_span_from_highlighted_code(vdom):
    # for some reason pygments adds an empty span at the start of the code block
    if vdom["tagName"] == "pre":
        if vdom["children"]:
            first_child = vdom["children"][0]
            if not (first_child.get("children") or first_child.get("attributes")):
                del vdom["children"][0]
    return vdom
