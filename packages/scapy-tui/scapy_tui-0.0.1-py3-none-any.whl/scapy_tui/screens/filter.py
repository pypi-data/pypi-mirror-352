#!/usr/bin/venv python
# Copyright 2025 - 2025, Antonio Vázquez Blanco and the swexml contributors
# SPDX-License-Identifier: GPL-3.0-only

from textual.app import ComposeResult
from textual.widgets import Input, Button, Label
from textual.containers import VerticalGroup, HorizontalGroup
from textual.screen import ModalScreen


class FilterScreen(ModalScreen[tuple[bool, str]]):
    DEFAULT_CSS = """
    FilterScreen {
        align: center middle;
    }
    FilterScreen > VerticalGroup {
        width: 50%;
    }
    FilterScreen > VerticalGroup > Label {
        padding: 1;
    }
    FilterScreen > VerticalGroup > HorizontalGroup {
        align: center middle;
    }
    FilterScreen > VerticalGroup > HorizontalGroup > Button {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        self.input_filter = Input(placeholder="Filter:")
        yield VerticalGroup(
            Label("Enter a packet layer name for filtering."),
            self.input_filter,
            HorizontalGroup(
                Button("Cancel", variant="error", id="cancel"),
                Button("Filter", variant="primary", id="filter"),
            )
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        apply = event.button.id == "filter"
        self.dismiss((apply, self.input_filter.value))

    def key_enter(self):
        self.dismiss((True, self.input_filter.value))

    def key_escape(self):
        self.dismiss((False, self.input_filter.value))
