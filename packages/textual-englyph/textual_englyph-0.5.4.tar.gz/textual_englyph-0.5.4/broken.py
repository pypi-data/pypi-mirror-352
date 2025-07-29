"""Boilerplate code for testing purposes"""

from textual.app import App, ComposeResult
from textual.widgets import Button


class Test(App):
    def compose(self) -> ComposeResult:
        yield Button("tic", id="toc")

    def on_button_pressed(self):
        self.app.exit()

if __name__ == "__main__":
    Test().run(inline=True, inline_no_clear=True)
