from __future__ import print_function

from setuptools import setup, find_packages
import os
import sys
import subprocess

# the name of the project
name = "slidedown"

# basic paths used to gather files
here = os.path.abspath(os.path.dirname(__file__))
root = os.path.join(here, name)


# -----------------------------------------------------------------------------
# Package Definition
# -----------------------------------------------------------------------------


package = {
    "name": name,
    "python_requires": ">=3.6,<4.0",
    "packages": find_packages(exclude=["tests*"]),
    "description": "Simple slide decks with Markdown and Python",
    "author": "Ryan Morshead",
    "author_email": "ryan.morshead@gmail.com",
    "url": "https://github.com/rmorshea/slidedown",
    "license": "MIT",
    "platforms": "Linux, Mac OS X, Windows",
    "keywords": ["slideshow", "markdown", "idom"],
    "include_package_data": True,
}


# -----------------------------------------------------------------------------
# Entry Points
# -----------------------------------------------------------------------------


package["entry_points"] = {"console_scripts": ["slidedown = slidedown.__main__:run"]}


# -----------------------------------------------------------------------------
# requirements
# -----------------------------------------------------------------------------


requirements = []
with open(os.path.join(here, "requirements", "prod.txt"), "r") as f:
    for line in map(str.strip, f):
        if not line.startswith("#"):
            requirements.append(line)
package["install_requires"] = requirements


# -----------------------------------------------------------------------------
# Library Version
# -----------------------------------------------------------------------------


with open(os.path.join(root, "__init__.py")) as f:
    for line in f.read().split("\n"):
        if line.startswith('__version__ = "') and line.endswith('"'):
            package["version"] = (
                line
                # get assignment value
                .split("=", 1)[1]
                # clean up leading/trailing space
                .strip()
                # remove the quotes
                [1:-1]
            )
            break
    else:
        print("No version found in __init__.py")
        sys.exit(1)


# -----------------------------------------------------------------------------
# Library Description
# -----------------------------------------------------------------------------


with open(os.path.join(here, "README.md")) as f:
    long_description = f.read()

package["long_description"] = long_description
package["long_description_content_type"] = "text/markdown"


# -----------------------------------------------------------------------------
# Install It
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    setup(**package)
