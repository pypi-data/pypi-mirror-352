"""Boilerplate code for testing purposes"""

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class MyWidget(Widget):
    def __init__(self):
        super().__init__()
        self.my_string = str(self.rich_style)

    def compose(self) -> ComposeResult:
        yield Label(self.my_string)
        yield Label(str(self.rich_style))


class Test(App):
    def compose(self) -> ComposeResult:
        yield MyWidget()


if __name__ == "__main__":
    Test().run(inline=True, inline_no_clear=True)
