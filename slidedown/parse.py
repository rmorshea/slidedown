import cmarkgfm
import html
from html.parser import HTMLParser
import idom
import json
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name
from typing import Any, Dict, List


def markdown_to_slidedeck(md: str) -> List[Dict[str, Any]]:
    dom = HtmlToVdom().feed(cmarkgfm.github_flavored_markdown_to_html(md))

    slide_boundaries = []
    for i, node in enumerate(dom.children):
        if isinstance(node, idom.bunch.StaticBunch):
            if node.tagName == "h1":
                slide_boundaries.append(i)
    slide_boundaries.append(len(dom.children))

    slides = []
    for j in range(len(slide_boundaries) - 1):
        start, stop = slide_boundaries[j : j + 2]
        slides.append(idom.nodes.div(*dom.children[start:stop]))

    return slides


class HtmlToVdom(HTMLParser):
    def feed(self, *args, **kwargs):
        self._node_stack = [self._make_node("div", [])]
        super().feed(*args, **kwargs)
        return self._node_stack[0]

    def handle_starttag(self, tag, attrs):
        new = self._make_node(tag, dict(attrs))
        current = self._node_stack[-1]
        current.children.append(new)
        self._node_stack.append(new)

    def handle_endtag(self, tag):
        del self._node_stack[-1]

    def handle_data(self, data):
        if self._node_stack[-1].tagName == "code" and "class" in self._node_stack[-1].attributes:
            lang = self._node_stack[-1].attributes["class"].split("-", 1)[1]

            try:
                lexer = get_lexer_by_name(lang, stripall=True)
            except ClassNotFound:
                lexer = None

            if lexer:
                formatter = HtmlFormatter()
                html = highlight(data, lexer, formatter)
                dom = HtmlToVdom().feed(html).children[0]
                self._node_stack[-3].children[-1] = dom
                self._node_stack[-1] = dom
                return
        self._node_stack[-1].children.append(data)

    @staticmethod
    def _make_node(tag, attrs):
        if "style" in attrs:
            style = attrs["style"]
            if isinstance(style, str):
                attrs["style"] = dict([
                    tuple(map(str.strip, part.split(":")))
                    for part in style.split(";")
                ])
        return idom.bunch.StaticBunch(
            {"tagName": tag, "attributes": attrs, "children": []}
        )
