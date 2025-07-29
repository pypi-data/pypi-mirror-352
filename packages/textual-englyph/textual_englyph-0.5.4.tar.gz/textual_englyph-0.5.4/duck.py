"""Boilerplate code for testing purposes"""

from textual.app import App, ComposeResult
from textual_englyph import EnGlyphText, EnGlyphImage


class Test(App):
    """Test console markup styling the englyph text use case"""
    DEFAULT_CSS = """
    #I {
        height: 32;
    }
    """

    def compose(self) -> ComposeResult:
        yield EnGlyphImage("rubber_duck.png", id="I")

if __name__ == "__main__":
    Test().run(inline=True, inline_no_clear=True)
