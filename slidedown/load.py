import cmarkgfm
import idom
from idom.tools import html_to_vdom, HtmlParser
import json
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name
from typing import Any, Dict, List


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

    header = idom.html.div(*nodes[0:slide_boundaries[0]], id="slide-header")

    slides = []
    for j in range(len(slide_boundaries) - 1):
        start, stop = slide_boundaries[j : j + 2]
        slides.append(
            idom.html.div(header, *nodes[start:stop], id="slide-content")
        )

    return slides


def _highlight_code(node):
    if node["tagName"] == "pre":
        new_children = []
        new_node = {
            "tagName": "div",
            "children": new_children
        }
        for child in node["children"]:
            if isinstance(child, dict):
                if child["tagName"] == "code":
                    child["attributes"].setdefault("class", "language-text")
                    child = HiglightedCode(child)
            new_children.append(child)
        return new_node
    return node


def _idom_alternative(node):
    if node.get("attributes", {}).get("alt", "").startswith("python:"):
        with open(node["attributes"]["alt"].split(":", 1)[1], "r") as f:
            script = f.read()
        return ExecPythonScript(script)
    return node


@idom.element
async def HiglightedCode(self, node):
    lang = node["attributes"]["class"].split("-", 1)[1]
    try:
        lexer = get_lexer_by_name(lang, stripall=True)
    except ClassNotFound:
        lexer = None
    if lexer:
        formatter = HtmlFormatter()
        text = "\n".join(node["children"])
        return html_to_vdom(highlight(text, lexer, formatter))
    return node


@idom.element
async def ExecPythonScript(self, script: str):
    env = {"idom": idom}
    exec(script, env)
    main = env.get("main")
    if not callable(main):
        raise ValueError("Python script must have a function called 'main'")
    result = main()
    if isinstance(result, str):
        return {"tagName": "div", "children": [result]}
    elif result is not None:
        return result
    else:
        return {"tagName": "div"}
