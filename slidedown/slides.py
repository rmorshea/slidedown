import idom
import os
from typing import Dict, List, Any

from .load import markdown_to_slidedeck

HERE = os.path.dirname(__file__)


@idom.element
async def Slidedeck(self, filepath, markdown_style, code_style):
    slides, markdown_style, code_style = _load_slides_and_styles(
        filepath, markdown_style, code_style
    )

    index = idom.Var(0)
    slide_view = SlideView(slides, index)

    events = idom.Events()

    @events.on("KeyDown")
    async def shift_slide(key):
        if key == "ArrowLeft":
            index.set((index.get() - 1) % len(slides))
        elif key in (" ", "ArrowRight"):
            index.set((index.get() + 1) % len(slides))
        slide_view.update()

    return idom.html.div(
        idom.html.style(code_style),
        idom.html.style(markdown_style),
        slide_view,
        eventHandlers=events,
        tabIndex=-1,
        style={"outline": "none", "height": "100%", "width": "100%"},
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
