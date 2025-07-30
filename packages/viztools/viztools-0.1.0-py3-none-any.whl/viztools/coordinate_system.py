from typing import Tuple
import numbers

import numpy as np
import pygame as pg

from viztools.utils import to_np_array


TARGET_NUM_POINTS = 12
TARGET_DIVIDENDS = [1, 2.5, 5, 10]
DEFAULT_SCREEN_SIZE = (1280, 720)


class CoordinateSystem:
    def __init__(self, screen_size: Tuple[int, int] | np.ndarray):
        screen_size = to_np_array(screen_size)
        coord = create_affine_transformation(screen_size/2, (100, -100))
        self.coord: np.ndarray = coord
        self.inverse_coord: np.ndarray = np.linalg.pinv(self.coord)

        # user control
        self.dragging: bool = False
        self.mouse_position = np.zeros(2, dtype=int)
        self.zoom_factor = 100

    def zoom_out(self, focus_point=None, scale=1.2):
        scale = 1 / scale
        self.zoom_factor *= scale
        scale_mat = create_affine_transformation(scale=scale)
        self.coord = self.coord @ scale_mat
        if focus_point is not None:
            translation = (focus_point - self.get_zero_screen_point().flatten()) * (1 - scale)
            self.translate(translation)
        self.update_inv()

    def zoom_in(self, focus_point=None, scale=1.2):
        self.zoom_factor *= scale
        scale_mat = create_affine_transformation(scale=scale)
        self.coord = self.coord @ scale_mat
        if focus_point is not None:
            translation = (focus_point - self.get_zero_screen_point().flatten()) * (1 - scale)
            self.translate(translation)
        self.update_inv()

    def translate(self, direction):
        direction *= np.array([1, -1])
        translation_mat = create_affine_transformation(translation=direction / self.coord[0, 0])
        self.coord = self.coord @ translation_mat
        self.update_inv()

    def get_zero_screen_point(self):
        """
        Get the zero point of the coordinate system in screen coordinates.
        """
        return self.space_to_screen(np.array([0.0, 0.0]))

    def space_to_screen(self, mat: np.ndarray) -> np.ndarray:
        """
        Transform the given matrix with the internal coordinates.

        :param mat: A list of column vectors with shape [2, N]. For vectors shape should be [2, 1].
        :return: A list of column vectors with shape [2, N].
        """
        mat = to_np_array(mat)
        if mat.shape == (2,):
            mat = mat.reshape(2, 1)
        return transform(self.coord, mat)

    def screen_to_space(self, mat: np.ndarray):
        mat = to_np_array(mat)
        if mat.shape == (2,):
            mat = mat.reshape(2, 1)
        return transform(self.inverse_coord, mat)

    def update_inv(self):
        self.inverse_coord = np.linalg.pinv(self.coord)

    def handle_event(self, event) -> bool:
        """

        :param event:
        :return:
        """
        render_needed = False
        if event.type == pg.MOUSEBUTTONDOWN:
            self.dragging = True
            render_needed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragging = False
            render_needed = True
        elif event.type == pg.MOUSEMOTION:
            self.mouse_position = np.array(event.pos, dtype=int)
            if self.dragging:
                self.translate(np.array(event.rel))
                render_needed = True
        elif event.type == pg.MOUSEWHEEL:
            if event.y < 0:
                self.zoom_out(focus_point=self.mouse_position)
                render_needed = True
            else:
                self.zoom_in(focus_point=self.mouse_position)
                render_needed = True
        return render_needed


def transform(transform_matrix: np.ndarray, mat: np.ndarray, perspective=False) -> np.ndarray:
    """
    Transforms a given matrix with the given transformation matrix.
    Transformation matrix should be of shape [2, 2] or [3, 3]. If transformation matrix is of shape [3, 3] and the
    matrix to transform is of shape [2, N], matrix will be padded with ones to shape [3, N].
    If mat is of shape [2,] it will be converted to [2, 1].

    The calculation will be transform_matrix @ mat.

    :param transform_matrix: A np.ndarray with shape [2, 2] or [3, 3].
    :param mat: The matrix to convert of shape [2, N]. If mat is of shape [2,] it will be converted to [2, 1].
    :param perspective: If perspective is True and the transform_mat is of shape (3, 3), the x- and y-axis of the
                        resulting vector are divided by the resulting z axis.
    :return:
    """
    expanded = False
    if mat.shape == (2,):
        mat = mat.reshape((2, 1))
        expanded = True

    padded = False
    if transform_matrix.shape == (3, 3):
        mat = np.concatenate([mat, np.ones((1, mat.shape[1]))], axis=0)
        padded = True

    result = transform_matrix @ mat

    if expanded:
        result = result[:, 0]

    if padded:
        if perspective:
            result = result[:-1] / result[-1]
        else:
            result = result[:-1]
    return result


def create_affine_transformation(
        translation: float | np.ndarray | Tuple[int, int] = 0, scale: float | np.ndarray | Tuple[float, float] = 1
) -> np.ndarray:
    if isinstance(scale, numbers.Number):
        scale = (scale, scale)
    scale_coord = np.array(
        [[scale[0], 0, 0],
         [0, scale[1], 0],
         [0, 0, 1]]
    )
    if isinstance(translation, numbers.Number):
        translation = (translation, translation)
    translate_coord = np.array(
        [[1, 0, translation[0]],
         [0, 1, translation[1]],
         [0, 0, 1]]
    )
    return translate_coord @ scale_coord


def draw_coordinate_system(screen: pg.Surface, coordinate_system: CoordinateSystem, render_font: pg.font.Font):
    screen.fill((0, 0, 0))

    def adapt_quotient(quotient):
        if quotient <= 0:
            raise ValueError('Invalid quotient: {}'.format(quotient))
        numb_ten_potency = 0
        while quotient > 10:
            quotient *= 0.1
            numb_ten_potency += 1
        while quotient < 1:
            quotient *= 10
            numb_ten_potency -= 1

        diffs = [abs(quotient - target) for target in TARGET_DIVIDENDS]
        index = np.argmin(diffs)
        best_fitting = TARGET_DIVIDENDS[index] * (10 ** numb_ten_potency)

        return best_fitting

    extreme_points = np.array([
        [0, 0],
        [screen.get_width(), screen.get_height()]
    ]).T
    extreme_points = coordinate_system.screen_to_space(extreme_points).T
    target_num_points = TARGET_NUM_POINTS * screen.get_width() // DEFAULT_SCREEN_SIZE[0]
    target_dividend = (extreme_points[1, 0] - extreme_points[0, 0]) / target_num_points
    dividend = adapt_quotient(target_dividend)
    x_minimum = np.round(extreme_points[0, 0] / dividend) * dividend
    x_maximum = np.round(extreme_points[1, 0] / dividend) * dividend
    x_points = np.arange(x_minimum, x_maximum + dividend, dividend)
    for x in x_points:
        vertical_lines = np.array([[x, 0], [x, 0]])
        transformed_vertical_lines = coordinate_system.space_to_screen(vertical_lines.T).T
        transformed_vertical_lines[:, 1] = [0, screen.get_height()]
        color = pg.Color(30, 30, 30)
        if x == 0:
            color = pg.Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_vertical_lines[0], transformed_vertical_lines[1])

    y_minimum = np.round(extreme_points[1, 1] / dividend) * dividend
    y_maximum = np.round(extreme_points[0, 1] / dividend) * dividend
    y_points = np.arange(y_minimum, y_maximum + dividend, dividend)

    for y in y_points:
        horizontal_lines = np.array([[extreme_points[0, 0], y], [extreme_points[1, 0], y]])
        transformed_horizontal_lines = coordinate_system.space_to_screen(horizontal_lines.T).T
        transformed_horizontal_lines[:, 0] = [0, screen.get_width()]
        color = pg.Color(30, 30, 30)
        if y == 0:
            color = pg.Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_horizontal_lines[0], transformed_horizontal_lines[1])

    # draw numbers
    zero_point = coordinate_system.space_to_screen(np.array([0, 0]))

    if 0 < zero_point[1] < screen.get_height():
        for x in x_points:
            if abs(x) > 10 ** -5:
                float_format = '{:.2f}' if abs(x) > 1 else '{:.2}'
                font = render_font.render(float_format.format(x), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
                pos = coordinate_system.space_to_screen(np.array([x, 0]))
                pos += 10
                render_pos = tuple(pos.flatten().tolist())
                screen.blit(font, render_pos)

    if 0 < zero_point[0] < screen.get_width():
        for y in y_points:
            if abs(y) > 10 ** -5:
                float_format = '{:.2f}' if abs(y) > 1 else '{:.2}'
                font = render_font.render(float_format.format(y), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
                pos = coordinate_system.space_to_screen(np.array([0, y]))
                pos += 10
                render_pos = tuple(pos.flatten().tolist())
                screen.blit(font, render_pos)
