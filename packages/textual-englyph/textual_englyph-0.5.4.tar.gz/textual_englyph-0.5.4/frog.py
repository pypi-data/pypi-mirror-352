"""Boilerplate code for testing purposes"""

from textual.app import App, ComposeResult
from textual_englyph import EnGlyphText, EnGlyphImage


class Test(App):
    """Test console markup styling the englyph text use case"""
    DEFAULT_CSS = """
    #I {
        height: 24;
    }
    """

    def compose(self) -> ComposeResult:
        yield EnGlyphImage("frog_sensei.png", id="I")
        yield EnGlyphText("I", text_size="x-small")
        yield EnGlyphText("Know", text_size="small")
        yield EnGlyphText("Just", text_size="medium")
        yield EnGlyphText("The", text_size="large")
        yield EnGlyphText("Thing", text_size="x-large")
        yield EnGlyphText("You", text_size="xx-large")
        yield EnGlyphText("Need!", text_size="xxx-large")

if __name__ == "__main__":
    Test().run()
