#!/usr/bin/venv python
# Copyright 2025 - 2025, Antonio Vázquez Blanco and the swexml contributors
# SPDX-License-Identifier: GPL-3.0-only

from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem
from scapy.packet import Packet, ConditionalField


class PktListEntry(ListItem):
    def __init__(self, pkt: Packet) -> None:
        super().__init__()
        self.pkt = pkt

    def _last_layer_fields(self) -> str:
        layer = self.pkt.lastlayer()
        fields = []
        for f in layer.fields_desc:
            if isinstance(f, ConditionalField) and not f._evalcond(layer):
                continue
            fields.append("%s=%s" % (f.name, f.i2repr(
                layer, layer.getfieldval(f.name))))
        return " [" + ", ".join(fields) + "]"

    def compose(self) -> ComposeResult:
        yield Label(self.pkt.summary() + self._last_layer_fields(), markup=False)


class PktList(ListView):
    def __init__(self, pkts: list[Packet]):
        super().__init__()
        self.pkts = pkts
        self._filter = None

    def on_mount(self) -> None:
        self._refresh()

    def filter(self, filter: str) -> None:
        self._filter = filter
        self._refresh()

    def _filter_match(self, pkt: Packet):
        if self._filter is None:
            return True
        if self._filter == "":
            return True
        if pkt.haslayer(self._filter):
            return True
        return False

    def _refresh(self) -> None:
        self.clear()
        for pkt in self.pkts:
            if self._filter_match(pkt):
                self.append(PktListEntry(pkt))
