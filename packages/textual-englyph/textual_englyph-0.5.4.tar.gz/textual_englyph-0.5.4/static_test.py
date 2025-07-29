from textual.app import App
from textual.widgets import Static


class TextualApp(App[None]):

    DEFAULT_CSS = """
    #S {
        height: 10; width: auto;
        background: red; border: solid blue;
    }
    """

    def compose(self):
        yield Static("Hello, Textual", id="S" )


TextualApp().run()
