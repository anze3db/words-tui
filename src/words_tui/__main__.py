# SPDX-FileCopyrightText: 2023-present Anže Pečar <anze@pecar.me>
#
# SPDX-License-Identifier: MIT
import sys

if __name__ == "__main__":
    from words_tui.cli import words_tui

    sys.exit(words_tui())
