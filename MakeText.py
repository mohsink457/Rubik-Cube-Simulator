from ursina import Text


class MakeText(Text):

    def __init__(self, label_text, position):
        text_strip = label_text.strip()
        super().__init__(text=text_strip, wordwrap=30, position=position)

    def set_text(self, new_text):
        text_strip = new_text.strip()
        self.text = text_strip

    def get_text(self):
        return self.text
