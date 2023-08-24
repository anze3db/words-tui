
![Screenshot 2023-08-24 at 08 13 47](https://github.com/anze3db/words-tui/assets/513444/021d5cd8-da5d-43b6-8747-ff1c1cb31d6e)

# words-tui

`words-tui` is an app for daily writing in your terminal, built with [Textual](https://github.com/Textualize/textual).

[![PyPI - Version](https://img.shields.io/pypi/v/words-tui.svg)](https://pypi.org/project/words-tui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/words-tui.svg)](https://pypi.org/project/words-tui)
[![Build and Test](https://github.com/anze3db/words-tui/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/anze3db/words-tui/actions/workflows/build-and-test.yml)

-----

**Table of Contents**

- [Demo](#demo)
- [Installation](#installation)
- [Running](#running)
- [License](#license)

## 🎬 Demo

https://github.com/anze3db/words-tui/assets/513444/5f064606-384f-471d-8990-f4681dfff29c

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
