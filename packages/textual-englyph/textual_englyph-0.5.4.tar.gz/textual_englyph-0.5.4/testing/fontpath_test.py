"""Boilerplate code for testing purposes"""

from textual.app import App, ComposeResult
from textual_englyph import EnGlyphText


class Test(App):
    """Test console markup styling the englyph text use case"""

    def compose(self) -> ComposeResult:
        yield EnGlyphText(":warning: !", text_size="large" )
        yield EnGlyphText("Hello [red] :warning: Textual!", font_name="/tmp/BirchLeaf.ttf", font_size=32)
        yield EnGlyphText("Burger \u1F354", font_name="/tmp/NotoColorEmoji-Regular.ttf", font_size=12, basis=(2,4) )


if __name__ == "__main__":
    Test().run(inline=True, inline_no_clear=True)
