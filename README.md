# Slidedown

- Do you ✍️ Slides?
- Do you 😠 PowerPoint?
- Do you ❤️ Markdown?

---

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
directory that `slidedown` was invoked and must contains a function `Main()` or `main()`
that returns an IDOM element or a VDOM dict. All other `data-` attributes will be
interpreted as parameters to pass to that function.

# IDOM in Slidedown Example

The following markup:

```markdown
# Hello IDOM!

<span data-idom="hello" data-greeting="hello" />
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

# Config File

Slidedown supports a `slidedown.json` config file that can be placed adjacent to your
Markdown in order to configure the options used when running. The available options
match those seen in the help message (`slidedown --help`) except with all usages of `-`
replaced with `_`. For example:

```json
{
  "host": "127.0.0.1",
  "no_browser": true,
  "no_reload": false,
  "port": 5678,
  "reload_delay": 3.0,
  "reload_ignore": ["ignore-dir/*"],
  "reload_watch": ["watch-dir/*"],
  "show_options": false,
  "start_slide": 0
}
```
