import idom
import os
from typing import Dict, List, Any

from .load import markdown_to_slidedeck

HERE = os.path.dirname(__file__)


@idom.element(state="filepath, markdown_style, code_style")
async def Slidedeck(self, filepath, markdown_style, code_style, focus=True, index=0):
    slides, markdown_style, code_style = _load_slides_and_styles(
        filepath, markdown_style, code_style
    )

    index_var = idom.Var(index)
    slide_view = SlideView(slides, index_var)

    events = idom.Events()

    @events.on("KeyDown")
    async def shift_slide(event):
        if event["key"] == "Escape":
            self.update(index=index_var.get(), focus=(not focus))
        elif focus:
            if event["key"] == "ArrowLeft":
                index_var.set((index_var.get() - 1) % len(slides))
                slide_view.update()
            elif event["key"] in (" ", "ArrowRight"):
                index_var.set((index_var.get() + 1) % len(slides))
                slide_view.update()

    style = {"outline": "none", "height": "100%", "width": "100%"}
    if not focus:
        style["border"] = "3px solid grey"

    return idom.html.div(
        idom.html.style(code_style),
        idom.html.style(markdown_style),
        slide_view,
        eventHandlers=events,
        tabIndex=-1,
        style=style,
    )


@idom.element(state="slides, index")
async def SlideView(
    self: idom.Element, slides: List[Dict[str, Any]], index: idom.Var[int]
) -> Dict[str, Any]:
    return idom.html.div(slides[index.get()], id="slide")


def _load_slides_and_styles(filepath, markdown_style_path, code_style_path):
    with open(filepath, "r") as f:
        slides = markdown_to_slidedeck(f.read())

    if not markdown_style_path.endswith(".css"):
        markdown_style_path = os.path.join(
            HERE, "styles", "markdown", markdown_style_path + ".css"
        )
    with open(markdown_style_path, "r") as f:
        markdown_style = f.read()

    if not code_style_path.endswith(".css"):
        code_style_path = os.path.join(
            HERE, "styles", "pygments", code_style_path + ".css"
        )
    with open(code_style_path, "r") as f:
        code_style = f.read()

    return slides, markdown_style, code_style
