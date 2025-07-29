from textual.app import App, ComposeResult
from textual.widgets import Button
from textual.containers import VerticalScroll

class APP_CLASS(App):

    DEFAULT_CSS = """
    .is_flat {
        border:none;
        min-height: 3;
    }
    """
    def compose(self) -> ComposeResult:
        with VerticalScroll(id = "verticalscroll_test"):
            yield Button("button1", classes="is_flat" )
            yield Button("button2", classes="is_flat" )


if __name__ == "__main__":
    App = APP_CLASS()
    App.run()
