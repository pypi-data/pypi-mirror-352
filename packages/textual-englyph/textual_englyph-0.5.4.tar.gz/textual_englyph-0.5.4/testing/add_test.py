"""Boilerplate code for testing purposes"""

from textual.app import App, ComposeResult
from textual_englyph import EnGlyphText, EnGlyphImage


class Test(App):
    """Test console markup styling the englyph text use case"""
    DEFAULT_CSS = """
    #I {
        max-height: 16;
    }
    .T {
        background: white 50%;
        position: relative;
        offset: 3 -3;
    }
    """

    def compose(self) -> ComposeResult:
        yield EnGlyphImage( "/tmp/logo.jpg", id="I" )
        yield EnGlyphText( " Textual ", classes="T", text_size="medium" )
        #yield EnGlyphText( "Libraries", classes="T", text_size="medium" )


if __name__ == "__main__":
    Test().run(inline=True, inline_no_clear=True)
