from textual.app import App, ComposeResult
from textual_englyph import EnGlyphText, EnGlyphImage
from PIL import Image, ImageDraw, ImageFont


class Test(App):
    CSS = """
    EnGlyphImage {
        height: 9;
    }
    .Hi2 {
        height: 2;
    }
    .Hi3 {
        height: 3;
    }
    #II {
        height: 2;
        position: relative;
        offset: 0 -2;
    }
    #III {
        height: 2;
    }
    #IIII {
        height: 3;
    }
    EnGlyphText {
        background: white 20%;
        padding: 0;
        position: relative;
        offset: 3 0;
    }
    """
    #unicode_text = "\U0001f602"
    unicode_text = "👶"
    im = Image.new("RGB", (140, 128), "blue")
    draw = ImageDraw.Draw(im)
    draw.font = ImageFont.truetype("/tmp/NotoColorEmoji.ttf", 109)
    draw.text((0, 0), unicode_text, embedded_color=True)

    def compose(self) -> ComposeResult:
        yield EnGlyphImage("testing/hopper.jpg", id="I")
        yield EnGlyphText(":baby: 'Grace' x-small")
        yield EnGlyphText(":baby: 'Grace' [black]small", id="T", text_size="small")
        yield EnGlyphImage( self.im, id="II")
        yield EnGlyphText(":baby: 'Grace' medium", id="TT", text_size="medium")
        yield EnGlyphImage( self.im, id="III")
        yield EnGlyphText(":baby: 'Grace' large", id="TTT", text_size="large")
        yield EnGlyphImage( self.im, id="IIII")

if __name__ == "__main__":
    Test().run()
    #Test().run(inline=True, inline_no_clear=True)
