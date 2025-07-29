from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Label


class Test(App):
    DEFAULT_CSS = """
    Grid {
        grid-size: 2 1;
    }
    Label {
        text-align: right;
    }
    """

    def compose(self) -> ComposeResult:
        yield Grid(Label("Hello"), Label("World!"))


if __name__ == "__main__":
    Test().run()
