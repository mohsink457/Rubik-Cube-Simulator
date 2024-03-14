from ursina import Slider


class MakeSlider(Slider):

    def __init__(self, lower_limit, upper_limit, function, step, initial, position):
        super().__init__(lower_limit, upper_limit, on_value_changed=function, step=step, default=initial,
                         position=position)

    def get_value(self):
        return self.value

