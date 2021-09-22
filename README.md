# Slidedown

- Do you ✍️ Slides?
- Do you 😠 PowerPoint?
- Do you ❤️ Markdown?

# You're in Luck!

Turn markdown like this:

```markdown
# Step 1

Create an awesome slide deck.

# Step 2

Present it to awesome people.

# Step 3

Profit?
```

Into slides like this:

<img
  style="outline: 1px solid black"
  src="https://github.com/rmorshea/slidedown/raw/master/docs/simple-slide-example.gif"
/>

# How?

1. Install `slidedown` with `pip`

```bash
pip install slidedown
```

2. Start presenting your markdown files

```bash
slidedown README.md
```

3. Open up your browser

```
http://localhost:5678/client/index.html
```

# Interactive Elements

You can embed interactive views into your slides using [IDOM](https://github.com/idom-team/idom),
by adding an HTML element into your markup with an attribute of the form
`data-idom="your_script.py"` where `your_script.py` should be placed in the same
directory that `slidedown` was invoked and must contains a function `Main()` that
returns an IDOM element or a VDOM dict. All other `data-` attributes will be interpreted
as parameters to pass to `Main()`.

# IDOM in Slidedown Example

The following markup:

```markdown
# Hello IDOM!

<span data-idom="hello.py" data-greeting="hello" />
```

and a script `hello.py` containing:

```python
import idom

@idom.component
def Main(greeting: str):
    hi_count, set_hi_count = idom.hooks.use_state(1)
    return idom.html.button(
        {"onClick": lambda event: set_hi_count(hi_count + 1)},
        f"IDOM said {greeting} {hi_count} time(s)",
    )
```

Should produce the following output:

<img
  style="width: 500px"
  src="https://github.com/rmorshea/slidedown/raw/master/docs/slidedown-hello-idom.gif"
/>
