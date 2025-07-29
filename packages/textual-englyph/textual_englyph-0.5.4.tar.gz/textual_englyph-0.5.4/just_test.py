"""Boilerplate code for testing purposes"""

from textual.app import App, ComposeResult
from textual.widgets import Label
from textual_englyph import EnGlyphText


class Test(App):
    """Test CSS and console markup styling the basic englyph use case"""

    DEFAULT_CSS = """
    EnGlyph {
        color: green;
        text-style: underline;
        }
    """

    def compose(self) -> ComposeResult:
        yield Label("Hello [blue]Textual!")
        yield EnGlyphText("Hello [blue]Textual!")


if __name__ == "__main__":
    Test().run(inline=True, inline_no_clear=True)
