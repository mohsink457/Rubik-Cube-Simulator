from ursina import Button


class MakeButton(Button):

    def __init__(self, text, colour, position, function, scale, disabled):
        super().__init__(text=text, color=colour, scale=scale, text_origin=(0, 0), position=position,
                         on_click=function)
        # not/show the button if it is disabled or not
        self.disabled = disabled

    def toggle(self):
        self.disabled = not self.disabled

    def get_disabled(self):
        return self.disabled
