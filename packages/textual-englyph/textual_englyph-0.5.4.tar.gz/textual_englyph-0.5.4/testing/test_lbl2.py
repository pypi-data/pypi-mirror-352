from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label
from textual_englyph import EnGlyph


class Test(App):
    DEFAULT_CSS = """
    EnGlyph {
        color: red;
        border: heavy;
    }
    Label {
        color: red;
        border: heavy;
    }
    Grid {
        grid-size: 3 1;
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("Hello[blue] Textual[/]!")
            yield EnGlyph("Hello[blue] Textual[/]!")


if __name__ == "__main__":
    Test().run()
