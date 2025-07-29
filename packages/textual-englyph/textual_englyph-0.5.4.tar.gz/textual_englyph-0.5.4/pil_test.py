from PIL import Image, ImageDraw, ImageFont

if __name__ == "__main__":
    back_ground_color = (128,0,0)
    unicode_text = "\U0001f602"
    im = Image.new("RGB", (64, 64), back_ground_color)
    #draw = ImageDraw.Draw(im)
    #unicode_font = ImageFont.truetype("/tmp/NotoColorEmoji.ttf", 109)
    #draw.text((80, 80), unicode_text, font=unicode_font, embedded_color=True)
    im.show()
