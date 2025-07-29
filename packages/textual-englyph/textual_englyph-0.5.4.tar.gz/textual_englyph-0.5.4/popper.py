from textual.app import App, ComposeResult
from textual_englyph import EnGlyphText, EnGlyphImage


class Test(App):
    """Test the basic englyph image use case"""

    CSS = """
    EnGlyphImage {
        height: 10;
        position: relative;
        offset: 0 0;
    }
    #T {
        background: white 20%;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield EnGlyphImage("cats/cat_right_paw.png", id="I")
        yield EnGlyphImage("cats/cat_right_paw_keyboard.png", id="II")
        yield EnGlyphImage("cats/cat_left_paw.png", id="III")
        yield EnGlyphImage("cats/cat_left_paw_keyboard.png", id="IV")
        yield EnGlyphImage("cats/cat_idle.png", id="V")
        yield EnGlyphImage("cats/cat_idle_keyboard.png", id="VI")
        #yield EnGlyphImage( "testing/twirl.gif", id="I" )
        #yield EnGlyphText( " Coup de Grâce ", id="T", text_size="medium" )


# uv run testing/image_test.py
if __name__ == "__main__":
    # with pyinstrument.profile():
    Test().run()
    #Test().run(inline=True, inline_no_clear=True)
