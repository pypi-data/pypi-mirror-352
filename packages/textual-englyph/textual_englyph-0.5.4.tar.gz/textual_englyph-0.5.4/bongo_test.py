"""Boilerplate code for testing purposes"""

# import pyinstrument
from textual.app import App, ComposeResult
from textual.widgets import Footer
from textual_englyph import EnGlyphImage


class Test(App):
    """Test the basic englyph image use case"""

    DEFAULT_CSS = """
    #I {
        height: 32;
    }
    """

    def compose(self) -> ComposeResult:
        yield EnGlyphImage( "bongo-cat-typing.gif", id="I" )
        yield Footer()


# uv run testing/image_test.py
if __name__ == "__main__":
    # with pyinstrument.profile():
    #Test().run()
    Test().run(inline=True, inline_no_clear=True)
