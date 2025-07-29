#!/usr/bin/venv python
# Copyright 2025 - 2025, Antonio Vázquez Blanco and the swexml contributors
# SPDX-License-Identifier: GPL-3.0-only

import argparse
from pathlib import Path
from scapy.main import load_contrib
from .scapy_tui_app import ScapyApp


def load_layers():
    load_contrib("automotive.bmw.definitions")
    load_contrib("automotive.bmw.enumerator")
    load_contrib("automotive.bmw.hsfz")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=Path)
    args = parser.parse_args()
    load_layers()
    app = ScapyApp(args.filename)
    app.run()


if __name__ == "__main__":
    main()
