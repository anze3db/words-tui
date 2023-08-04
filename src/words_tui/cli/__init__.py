# SPDX-FileCopyrightText: 2023-present Anže Pečar <anze@pecar.me>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

import click

from words_tui.__about__ import __version__
from words_tui.tui.app import WordsTui
from words_tui.tui.db import init_db


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="words-tui")
@click.option("--db", "-d", envvar="WORDS_TUI_DB", default=Path.home() / ".words-tui.db", help="Database file to use")
def words_tui(db: str):
    init_db(db)
    WordsTui().run()
