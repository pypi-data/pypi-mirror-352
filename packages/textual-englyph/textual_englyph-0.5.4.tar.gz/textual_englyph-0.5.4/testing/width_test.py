"""Boilerplate code for width testing purposes"""

from textual.app import App, ComposeResult
from textual_englyph import EnGlyph


class Test(App):
    """Test CSS and console markup styling the basic englyph use case"""

    DEFAULT_CSS = """
        #uno {
         color: green;
         max-width: 27;
         }
         #dos {
         color: red;
         }
    """

    second = EnGlyph("Hello [blue]Textual!", basis=(2, 4), id="dos")
    second.styles.width = 15

    def compose(self) -> ComposeResult:
        yield EnGlyph("Hello [blue]Textual!", basis=(2, 4), id="uno")
        yield self.second


if __name__ == "__main__":
    Test().run(inline=True, inline_no_clear=True)
