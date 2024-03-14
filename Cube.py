from ursina import *
from random import randint
import copy

import twophase.solver as sv  # Several tables that must be created on only first run, which would take some time. Though, I have already created them - they are in the folder twophase.


def rotate_cube_side(side, direction):
    """Side in format of: [[1, 2, 3],
                            [4, 5, 6],
                            [7, 8, 9]]"""

    # In all rotations, the middle value will stay the same
    top_row = side[0]
    bottom_row = side[2]
    left_column = [top_row[0], side[1][0], bottom_row[0]]
    right_column = [top_row[2], side[1][2], bottom_row[2]]
    if direction == 1:  # Anticlockwise rotation
        side[1][0] = top_row[1]
        side[1][2] = bottom_row[1]
        for i in range(0, 3):
            side[0][i] = right_column[i]
            side[2][i] = left_column[i]
    else:  # Clockwise rotation
        side[1][0] = bottom_row[1]
        side[1][2] = top_row[1]
        for i in range(0, 3):
            side[0][i] = left_column[2 - i]
            side[2][i] = right_column[2 - i]
    return side


def convert_to_string(cube_state):
    u_current = ''
    l_current = ''
    f_current = ''
    r_current = ''
    b_current = ''
    d_current = ''
    for i in range(0, 3):  # Every row in the face
        for j in range(0, 3):  # Every cubie in a row:
            u_current += cube_state[0][i][j]
            l_current += cube_state[1][i][j]
            f_current += cube_state[2][i][j]
            r_current += cube_state[3][i][j]
            b_current += cube_state[4][i][j]
            d_current += cube_state[5][i][j]
    cube_string = u_current + r_current + f_current + d_current + l_current + b_current
    return cube_string


class Cube:

    def __init__(self):
        # Creating the parent cube
        self.parent_cube = Entity(position=(0, 0, 0), rotation=0)

        # Render cubies
        self.cubies = []
        self.set_cubies()

        # solved state in a list
        self.solved_state = self.set_solved_state()
        # Initially, the current cube state is solved
        self.cube_state = self.set_solved_state()

        # Stores some needed information for rotations
        self.rotation_axis = {'left': 'x', 'right': 'x', 'top': 'y', 'bottom': 'y', 'front': 'z', 'back': 'z'}
        self.cubie_side_positions = {'left': self.left, 'bottom': self.bottom, 'right': self.right, 'front': self.front,
                                     'back': self.back, 'top': self.top}
        self.side_names = ['left', 'right', 'top', 'bottom', 'front', 'back']
        self.move_allowed = True
        self.corresponding_move = {'left': 'l',
                                   'bottom': 'd',
                                   'right': 'r',
                                   'front': 'f',
                                   'back': 'b',
                                   'top': 'u'}

    def set_cubies(self):
        model = 'models/cube_model'
        texture = 'textures/rubik_texture'

        # Position of the cubies in each face
        self.left = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.bottom = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}
        self.front = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        self.back = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        self.right = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.top = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}
        # Puts all the sides together in a set (which is faster to access than a list)
        cubies_pos = self.left | self.bottom | self.front | self.back | self.right | self.top
        # Rendering all the cubes
        self.cubies = [Entity(model=model, texture=texture, position=cubie_pos) for cubie_pos in cubies_pos]
        # Putting cube in the correct initial orientation on the screen
        for cube in self.cubies:
            cube.parent = self.parent_cube
            # Rotation of each cubie in the side
            self.parent_cube.rotation_y = -90

    def get_move_allowed(self):
        return self.move_allowed

    def reset_parent(self):
        for cube in self.cubies:
            if cube.parent == self.parent_cube:
                scene_position = round(cube.world_position, 1)  # Get their scene cords
                scene_rotation = cube.world_rotation
                cube.parent = scene  # Changes parent to the scene
                cube.position = scene_position  # Change position of the cubie to the scene cords
                cube.rotation = scene_rotation
        self.parent_cube.rotation = 0  # Resets the rotation of the parent cube

    def rotate_side(self, side, direction, animation_time):
        if self.move_allowed:
            self.move_allowed = False
            cube_positions = self.cubie_side_positions[side]  # Gets the cords of the cubies within this side
            rotation_axis = self.rotation_axis[side]  # Gets the axis about which the cube is rotated
            self.reset_parent()  # Changes parent back to the scene
            for cube in self.cubies:
                if cube.position in cube_positions:
                    cube.parent = self.parent_cube
                    # Rotation of each cubie in the side
                    eval(
                        f'self.parent_cube.animate_rotation_{rotation_axis}(-90*{direction}, duration={animation_time})')
            invoke(self.set_move_allowed_true, delay=1.2 * animation_time)  # set self.move_allowed = true
            # Change cube state
            exec(f'self.move_{self.corresponding_move[side]}({direction})')

    def set_move_allowed_true(self):
        self.move_allowed = True

    def scramble(self, moves):
        for i in range(moves):
            direction = int(-1 ** (randint(1, 2)))  # Chooses random direction
            side_name_index = randint(0, 5)
            side_name = self.side_names[side_name_index]
            cube_positions = self.cubie_side_positions[side_name]  # Gets the cords of the cubies within this side
            rotation_axis = self.rotation_axis[side_name]  # Gets the axis about which the cube is rotated
            self.reset_parent()  # Changes parent back to the scene
            for cube in self.cubies:
                if cube.position in cube_positions:
                    cube.parent = self.parent_cube
                    # Rotation of each cubie in the side
                    exec(f'self.parent_cube.rotation_{rotation_axis} = 90*{direction}')
                    # Update state of the cube
                    exec(f'self.move_{self.corresponding_move[side_name]}({-1 * direction})')

    def solve(self, time_limit):
        cube_string = convert_to_string(self.cube_state)  # Get state in correct format
        solution = sv.solve(cube_string, 0, time_limit)  # Find simplest solution
        return solution

    def move_l(self, direction):  # left face
        current = copy.deepcopy(self.cube_state)
        # Faces in order = ['U', 'L', 'F', 'R', 'B', 'D']
        # Anticlockwise rotation
        if direction == -1:
            for i in range(0, 3):
                # Changes in U
                current[0][i][0] = self.cube_state[2][i][0]
                # Changes in F§
                current[2][i][0] = self.cube_state[5][i][0]
                # Changes in D:
                current[5][i][0] = self.cube_state[4][2 - i][2]
                # Changes in B
                current[4][2 - i][2] = self.cube_state[0][i][0]
        else:  # Clockwise rotation
            for i in range(0, 3):
                # Changes in F
                current[2][i][0] = self.cube_state[0][i][0]
                # Changes in D
                current[5][i][0] = self.cube_state[2][i][0]
                # Changes in B:
                current[4][2 - i][2] = self.cube_state[5][i][0]
                # Changes in U
                current[0][i][0] = self.cube_state[4][2 - i][2]
        # Changes in L
        current[1] = rotate_cube_side(current[1], -1 * direction)
        # Update the cube:
        self.cube_state = copy.deepcopy(current)

    def move_r(self, direction):  # right face
        current = copy.deepcopy(self.cube_state)
        # Faces in order = ['U', 'L', 'F', 'R', 'B', 'D']
        # Anticlockwise rotation
        if direction == -1:
            for i in range(0, 3):
                # Changes in U
                current[0][i][2] = self.cube_state[2][i][2]
                # Changes in F
                current[2][i][2] = self.cube_state[5][i][2]
                # Changes in D:
                current[5][i][2] = self.cube_state[4][2 - i][0]
                # Changes in B
                current[4][i][0] = self.cube_state[0][2 - i][2]
        else:  # Clockwise rotation
            for i in range(0, 3):
                # Opposite of clockwise rotation
                current[2][i][2] = self.cube_state[0][i][2]
                current[5][i][2] = self.cube_state[2][i][2]
                current[4][2 - i][0] = self.cube_state[5][i][2]
                current[0][i][2] = self.cube_state[4][2 - i][0]
        # Changes in R
        current[3] = rotate_cube_side(current[3], direction)
        # Update the cube:
        self.cube_state = copy.deepcopy(current)

    def move_f(self, direction):  # front face
        current = copy.deepcopy(self.cube_state)
        # Faces in order = ['U', 'L', 'F', 'R', 'B', 'D']
        # Anticlockwise rotation
        if direction == -1:
            for i in range(0, 3):
                # Changes in U
                current[0][2][i] = self.cube_state[1][2 - i][2]
                # Changes in L
                current[1][i][2] = self.cube_state[5][0][i]
                # Changes in D:
                current[5][0][i] = self.cube_state[3][2 - i][0]
                # Changes in R:
                current[3][i][0] = self.cube_state[0][2][i]
        else:  # Clockwise rotation
            for i in range(0, 3):
                # Opposite of anti-clockwise rotation
                current[1][2 - i][2] = self.cube_state[0][2][i]
                current[5][0][i] = self.cube_state[1][i][2]
                current[3][2 - i][0] = self.cube_state[5][0][i]
                current[0][2][i] = self.cube_state[3][i][0]
        # Changes in F
        current[2] = rotate_cube_side(current[2], direction)
        # Update the cube:
        self.cube_state = copy.deepcopy(current)

    def move_d(self, direction):  # down/bottom face
        current = copy.deepcopy(self.cube_state)
        # Faces in order = ['U', 'L', 'F', 'R', 'B', 'D']
        # Anticlockwise rotation
        if direction == -1:
            # Changes in L
            current[1][2] = self.cube_state[2][2]
            # Changes in F
            current[2][2] = self.cube_state[3][2]
            # Changes in R:
            current[3][2] = self.cube_state[4][2]
            # Changes in B
            current[4][2] = self.cube_state[1][2]
        else:  # Clockwise rotation
            # Opposite of anti-clockwise rotation
            current[2][2] = self.cube_state[1][2]
            current[3][2] = self.cube_state[2][2]
            current[4][2] = self.cube_state[3][2]
            current[1][2] = self.cube_state[4][2]
        # Changes in D
        current[5] = rotate_cube_side(current[5], -1 * direction)
        # Update the cube:
        self.cube_state = copy.deepcopy(current)

    def move_u(self, direction):  # up/top face
        current = copy.deepcopy(self.cube_state)
        # Faces in order = ['U', 'L', 'F', 'R', 'B', 'D']
        # Anticlockwise rotation
        if direction == -1:
            # Changes in L
            current[1][0] = self.cube_state[2][0]
            # Changes in F
            current[2][0] = self.cube_state[3][0]
            # Changes in R:
            current[3][0] = self.cube_state[4][0]
            # Changes in B
            current[4][0] = self.cube_state[1][0]
        else:  # Clockwise rotation
            # Opposite of anti-clockwise rotation
            current[2][0] = self.cube_state[1][0]
            current[3][0] = self.cube_state[2][0]
            current[4][0] = self.cube_state[3][0]
            current[1][0] = self.cube_state[4][0]
        # Changes in U
        current[0] = rotate_cube_side(current[0], direction)
        # Update the cube:
        self.cube_state = copy.deepcopy(current)

    def move_b(self, direction):  # back face
        current = copy.deepcopy(self.cube_state)
        # Faces in order = ['U', 'L', 'F', 'R', 'B', 'D']
        # Anticlockwise rotation
        if direction == -1:
            for i in range(0, 3):
                # Changes in U
                current[0][0][i] = self.cube_state[1][2 - i][0]
                # Changes in L
                current[1][i][0] = self.cube_state[5][2][i]
                # Changes in D:
                current[5][2][i] = self.cube_state[3][2 - i][2]
                # Changes in R:
                current[3][i][2] = self.cube_state[0][0][i]
        else:  # Clockwise rotation
            for i in range(0, 3):
                # Opposite of anti-clockwise rotation
                current[1][2 - i][0] = self.cube_state[0][0][i]
                current[5][2][i] = self.cube_state[1][i][0]
                current[3][2 - i][2] = self.cube_state[5][2][i]
                current[0][0][i] = self.cube_state[3][i][2]
        # Changes in B
        current[4] = rotate_cube_side(current[4], -1 * direction)
        # Update the cube:
        self.cube_state = copy.deepcopy(current)

    def set_solved_state(self):
        state = []
        faces = ['U', 'L', 'F', 'R', 'B', 'D']
        for face in range(0, 6):
            state.append([['', '', ''], ['', '', ''], ['', '', '']])
            for row in range(0, 3):
                for column in range(0, 3):
                    state[face][row][column] = faces[face]
        return state

    def check_if_solved(self):
        return self.cube_state == self.solved_state
