# words-tui

`words-tui` is an app for daily writing in your terminal, built with [Textual](https://github.com/Textualize/textual).

[![PyPI - Version](https://img.shields.io/pypi/v/words-tui.svg)](https://pypi.org/project/words-tui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/words-tui.svg)](https://pypi.org/project/words-tui)

-----

**Table of Contents**

- [Demo](#demo)
- [Installation](#installation)
- [Running](#running)
- [License](#license)

## 🎬 Demo

https://github.com/anze3db/words-tui/assets/513444/a6a2d15c-f5ad-4e2a-a343-ffe7abfdb582

## Installation

The easiest way to install `words-tui` is with [pipx](https://pypa.github.io/pipx/).

```console
pipx install words-tui
```

Alternatively, you can install it with `pip`:

```console
pip install words-tui
```

## Running

To run `words-tui`, simply run the following command:

```console
words-tui
```

It stores all of your writing in ~/.words-tui.db by default, but you can override this with the `WORDS_TUI_DB` environment variable or the `--db` flag.

```console
words-tui --db /path/to/db
```

## License

`words-tui` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
