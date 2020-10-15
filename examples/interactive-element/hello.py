import idom


@idom.element
def Main():
    hi_count, set_hi_count = idom.hooks.use_state(1)
    plural = 's' if hi_count > 1 else ''
    return idom.html.button(
        {"onClick": lambda event: set_hi_count(hi_count + 1)},
        f"IDOM said hi {hi_count} time{plural}",
    )
