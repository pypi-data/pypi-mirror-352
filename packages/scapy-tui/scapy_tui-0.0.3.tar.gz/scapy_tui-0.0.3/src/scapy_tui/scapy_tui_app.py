#!/usr/bin/venv python
# Copyright 2025 - 2025, Antonio Vázquez Blanco and the swexml contributors
# SPDX-License-Identifier: GPL-3.0-only

from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.containers import HorizontalGroup
from scapy.utils import rdpcap
from .widgets.pkt_list import PktList
from .widgets.pkt_detail import PktDetail
from .screens.filter import FilterScreen


class ScapyApp(App):
    """A Textual app to inspect communications with scapy."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("f", "filter", "Filter")
    ]

    def __init__(self, path: Path, **kwargs):
        super().__init__(**kwargs)
        self.pcap_path = path

    def compose(self) -> ComposeResult:
        yield Header()
        yield HorizontalGroup(
            PktList(rdpcap(str(self.pcap_path))),
            PktDetail()
        )
        yield Footer()

    def on_list_view_selected(self, event: PktList.Selected):
        self.query_one(PktDetail).set_pkt(event.item.pkt)

    def action_filter(self) -> None:
        def check_filter(val: tuple[bool, str] | None) -> None:
            apply, filter = val
            if apply:
                self.query_one(PktList).filter(filter)
        self.push_screen(FilterScreen(), check_filter)
