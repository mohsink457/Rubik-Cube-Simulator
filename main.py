from ursina import *
from Cube import Cube
from MakeButton import MakeButton
from MakeSlider import MakeSlider
from MakeText import MakeText


class Window(Ursina):
    def __init__(self):
        super().__init__()

        # Settings
        window.fullscreen = True
        window.fps_counter.enabled = True
        self.animation_time = 0.1
        self.time_limit = 0.1

        # Controls
        self.controls = {
            'left': 'l',
            'bottom': 'd',
            'right': 'r',
            'front': 'f',
            'back': 'b',
            'top': 'u'
        }

        # Cube
        self.cube = Cube()
        self.rotation_direction = 1
        self.rotation_made = False

        # Scene
        Entity(model='quad', scale=60, texture='white_cube', texture_scale=(60, 60), rotation_x=90, y=-5,
               color=color.dark_gray)  # renders the floor on screen
        Entity(model='sphere', scale=150, texture='textures/walls', double_sided=True)  # renders the 'walls' on screen

        # Camera
        EditorCamera()

        # Move count variable
        self.move_count = 0
        self.hint_count = 0

        # Optimal path
        self.optimal_moves = []

        # Labels
        self.move_count_label = MakeText(f'Move count: {self.move_count}', (-0.65, 0))
        self.hint_count_label = MakeText(f'Hint count: {self.hint_count}', (-0.65, -0.15))
        self.optimal_move_label = MakeText('Next move/s:', (-0.65, 0.35))

        # Hint button variables
        self.hint_button_pressed = False

        # Buttons
        self.scramble_button = MakeButton('Scramble', (0, 0, 0), (0.65, 0.15), self.scramble_cube, 0.2, False)
        self.hint_button = MakeButton('Hint', (0, 0, 0), (0.65, -0.1), self.hint, 0.2, False)
        self.solve_button = MakeButton('Solve', (0, 0, 0), (0.65, -0.35), self.solve, 0.2, False)

        # Slider
        self.animation_time_slider = MakeSlider(0.1, 1, self.change_animation_time, 0.05, self.animation_time,
                                                (-0.65, -0.3))
        self.time_limit_slider = MakeSlider(0.1, 3, self.change_time_limit, 0.1, self.time_limit, (-0.65, -0.4))
        # Slider labels
        self.animation_time_slider_label = MakeText('Animation time:', (-0.65, -0.22))
        self.time_limit_slider_label = MakeText('Solve Time Limit:', (-0.65, -0.32))

    def change_time_limit(self):
        self.time_limit = self.time_limit_slider.get_value()

    def change_animation_time(self):
        self.animation_time = self.animation_time_slider.get_value()

    def scramble_cube(self):
        self.cube.scramble(30)
        self.move_count = 0  # Reset move count
        self.move_count_label.set_text(f'Move count: {self.move_count}')  # Update move count on the screen
        self.hint_count = 0  # Reset hint count
        self.hint_count_label.set_text(f'Hint count: {self.hint_count}')  # Update hint count on the screen

    def hint(self):
        if not self.cube.check_if_solved():
            # Increment the hint count and show it on the screen
            self.hint_count += 1
            self.hint_count_label.set_text(f'Hint count: {self.hint_count}')
            # Find the next optimal move
            solution = self.cube.solve(self.time_limit)  # Entire optimal solution
            optimal_move = solution[0]  # Take the first move, and it's count
            optimal_move_count = solution[1]
            if optimal_move_count == '3':  # Simplifies the solution, as the library does not return reverse moves
                optimal_move = optimal_move + 'I'
            self.optimal_moves = [optimal_move]
            self.update_optimal_moves()

    def update_optimal_moves(self):
        string = 'Next move/s: '
        for move in self.optimal_moves:
            string += move + ' '
        self.optimal_move_label.set_text(string)

    def solve(self):
        if not self.cube.check_if_solved():
            solution = self.cube.solve(self.time_limit)  # Entire optimal solution
            # Putting solution into the correct format
            open_bracket_index = solution.find('(')
            solution = solution[:open_bracket_index]
            solution = solution.replace(' ', '')
            # Populating self.optimal_moves with the optimal moves in order
            self.optimal_moves = []
            for i in range(0, len(solution), 2):  # Iterate through the solution string
                move = solution[i]
                count = int(solution[i + 1])
                if count == 3:  # Simplifying the solution as, as library does not give reverse moves.
                    move = move + 'I'
                    count = 1
                for j in range(count):  # Add the move onto the list the correct amount of times
                    self.optimal_moves.append(move)
            # updates the content on the screen
            self.update_optimal_moves()

    def increment_move_count(self):
        if self.cube.get_move_allowed():
            self.move_count += 1
            self.move_count_label.set_text(f'Move count: {self.move_count}')

    def check_if_done(self):
        if self.cube.check_if_solved():
            self.move_count = 0  # Reset move count
            self.move_count_label.set_text(f'Move count: {self.move_count}')  # Update move count on the screen
            self.hint_count = 0  # Reset hint count
            self.hint_count_label.set_text(f'Hint count: {self.hint_count}')  # Update hint count on the screen

    def input(self, key, active=False):
        if key == 'shift':  # updates direction of rotation depending on if shift is being held or not
            self.rotation_direction = -1
        elif key == 'shift up':
            self.rotation_direction = 1
        if active:
            if not self.cube.check_if_solved():  # Sides can only be rotated when cube is not solved
                if key == self.controls['left']:
                    self.increment_move_count()
                    self.cube.rotate_side('left', self.rotation_direction,
                                          self.animation_time)  # Rotates the left side etc..
                    self.check_if_done()  # Checks if the cube is solved and does the required actions
                elif key == self.controls['bottom']:
                    self.increment_move_count()
                    self.cube.rotate_side('bottom', self.rotation_direction, self.animation_time)
                    self.check_if_done()
                elif key == self.controls['right']:
                    self.increment_move_count()
                    self.cube.rotate_side('right', -1 * self.rotation_direction, self.animation_time)
                    self.check_if_done()
                elif key == self.controls['front']:
                    self.increment_move_count()
                    self.cube.rotate_side('front', -1 * self.rotation_direction, self.animation_time)
                    self.check_if_done()
                elif key == self.controls['back']:
                    self.increment_move_count()
                    self.cube.rotate_side('back', self.rotation_direction, self.animation_time)
                    self.check_if_done()
                elif key == self.controls['top']:
                    self.increment_move_count()
                    self.cube.rotate_side('top', -1 * self.rotation_direction, self.animation_time)
                    self.check_if_done()
        super().input(key)


if __name__ == '__main__':
    window = Window()
    window.run()
