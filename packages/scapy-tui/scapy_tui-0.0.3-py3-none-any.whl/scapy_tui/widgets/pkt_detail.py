#!/usr/bin/venv python
# Copyright 2025 - 2025, Antonio Vázquez Blanco and the swexml contributors
# SPDX-License-Identifier: GPL-3.0-only

from scapy.packet import Packet
from textual.widgets import TextArea


class PktDetail(TextArea):
    def __init__(self):
        super().__init__(read_only=True)

    def set_pkt(self, pkt: Packet):
        self.text = pkt.show(dump=True)
