from abc import ABC, abstractmethod
from typing import List, Tuple

import pygame as pg
import numpy as np

from viztools.coordinate_system import CoordinateSystem


class Drawable(ABC):
    @abstractmethod
    def draw(self, screen: pg.Surface, coordinate_system: CoordinateSystem, screen_size: np.ndarray):
        pass


class Points(Drawable):
    def __init__(
            self, points: np.ndarray, size: int | float = 3, colors: pg.Color | List[pg.Color] = pg.Color(77, 178, 11)
    ):
        """
        Drawable to display a set of points.
        :param points: A list of points with the shape [N, 2] where N is the number of points.
        :param size: The radius of the points. If set to an integer, this is the radius on the screen in pixels. If set
                     to a float, this is the radius on the screen in units of the coordinate system.
        :param colors: The color of the points.
        """
        self.points = points
        self.size = size
        if isinstance(colors, pg.Color):
            colors = [colors] * len(points)
        self.colors = colors
        assert len(self.colors) == len(self.points), 'Number of colors must match number of points.'

    def draw(self, screen: pg.Surface, coordinate_system: CoordinateSystem, screen_size: np.ndarray):
        draw_size = self._get_draw_size(coordinate_system)
        screen_points = to_draw_positions(self.points, coordinate_system, screen_size, draw_size)
        for pos, color in zip(screen_points, self.colors):
            pg.draw.circle(screen, color, pos, draw_size)

    def _get_draw_size(self, coordinate_system):
        draw_size = self.size
        if isinstance(draw_size, float):
            draw_size = max(int(draw_size * coordinate_system.zoom_factor), 1)
        return draw_size

    def clicked_points(self, event: pg.event.Event, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Returns the indices of the points clicked by the mouse. Returns empty array if no point was clicked.

        :param event: The event to check.
        :param coordinate_system: The coordinate system to use.
        """
        if event.type == pg.MOUSEBUTTONDOWN:
            draw_size = self._get_draw_size(coordinate_system)

            screen_pos = np.array(event.pos).reshape(1, 2)
            screen_points = coordinate_system.space_to_screen(self.points.T).T
            distances = np.linalg.norm(screen_points - screen_pos, axis=1)
            return np.nonzero(distances < draw_size)[0]
        return np.array([])


def to_draw_positions(
        points: np.ndarray, coordinate_system: CoordinateSystem, screen_size: np.ndarray, draw_size: int
) -> List[Tuple[int, int]]:
    """
    Converts a list of points to a list of positions to draw them on the screen.
    Filters out points outside the screen.

    :param points: Numpy array of shape [N, 2] where N is the number of points.
    :param coordinate_system: The coordinate system to use.
    :param screen_size: The size of the screen in pixels.
    :param draw_size: The radius of the points in screen space pixels.
    :return: List of tuples (x, y) where x and y are the screen coordinates of the points.
    """
    screen_points = coordinate_system.space_to_screen(points.T).T
    valid_positions = np.where(np.logical_and(
        np.logical_and(screen_points[:, 0] > -draw_size, (screen_points[:, 0] < screen_size[0] + draw_size)),
        np.logical_and(screen_points[:, 1] > -draw_size, (screen_points[:, 1] < screen_size[1] + draw_size))
    ))
    screen_points = screen_points[valid_positions]
    return screen_points_to_tuple_list(screen_points)


def screen_points_to_tuple_list(screen_points: np.ndarray) -> List[Tuple[int, int]]:
    # noinspection PyTypeChecker
    return [tuple(p) for p in screen_points.astype(int).tolist()]
