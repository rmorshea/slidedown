import idom

from .load import use_slides


def use_const(func, *args, **kwargs):
    return idom.hooks.use_state(lambda: func(*args, **kwargs))[0]


@idom.component
def Slidedeck(initial_slide_number, filepath):
    slides = use_slides(filepath)

    is_focused = use_const(idom.Ref, False)
    set_focused = use_const(idom.Ref, lambda is_focused: None)

    focus_indicator = FocusIndicator(is_focused, set_focused)

    index, set_index = idom.hooks.use_state(initial_slide_number - 1)
    slide_view = idom.html.div({"id": "slide"}, slides[index])

    def set_initial_focus(event):
        set_focused.current(True)

    def shift_slide(event):
        if event["key"] == "Escape":
            # toggle focus state
            set_focused.current(not is_focused.current)
        if is_focused.current:
            if event["key"] == "ArrowLeft":
                set_index((index - 1) % len(slides))
            elif event["key"] in (" ", "ArrowRight"):
                set_index((index + 1) % len(slides))

    style = {"outline": "none", "height": "100%", "width": "100%"}

    return idom.html.div(
        {
            "onKeyDown": shift_slide,
            "onClick": set_initial_focus,
            "tabIndex": -1,
            "style": style,
        },
        idom.html.link({"href": "/_static/markdown.css", "rel": "stylesheet"}),
        _center_content(slide_view),
        focus_indicator,
    )


@idom.component
def FocusIndicator(is_focused, set_focused):
    is_focused.current, set_focused.current = idom.hooks.use_state(is_focused.current)

    if not is_focused.current:
        return idom.html.div(
            {
                "style": {"position": "absolute", "bottom": "4px", "right": "16px"},
            },
            idom.html.pre({"fontSize": "16px"}, "escaped"),
        )
    else:
        return idom.html.div()


def _center_content(content):
    return idom.html.div(
        {"style": {"display": "table", "height": "100%", "width": "100%"}},
        idom.html.div(
            {"style": {"display": "table-cell", "verticalAlign": "middle"}},
            idom.html.div(
                {
                    "style": {
                        "width": "fit-content",
                        "maxWidth": "50%",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    }
                },
                content,
            ),
        ),
    )
