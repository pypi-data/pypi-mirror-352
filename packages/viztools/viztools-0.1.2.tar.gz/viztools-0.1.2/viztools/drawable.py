import time
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

import pygame as pg
import numpy as np

from viztools.coordinate_system import CoordinateSystem


ColorTuple = Tuple[int, int, int, int]


class Drawable(ABC):
    @abstractmethod
    def draw(self, screen: pg.Surface, coordinate_system: CoordinateSystem, screen_size: np.ndarray):
        pass


def _color_to_tuple(color: pg.Color | np.ndarray) -> ColorTuple:
    return color[0], color[1], color[2], color[3]


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
        self._colors: np.ndarray = np.array([_color_to_tuple(c) for c in colors])
        assert len(self._colors) == len(self.points), 'Number of colors must match number of points.'

        self._color_set: List[ColorTuple] = [_color_to_tuple(c) for c in np.unique(self._colors, axis=0)]

    def set_color(self, color: pg.Color | Tuple[int, int, int], index: int):
        color = _color_to_tuple(color)
        self._colors[index] = color
        if color not in self._color_set:
            self._color_set.append(color)

    def draw(self, screen: pg.Surface, coordinate_system: CoordinateSystem, screen_size: np.ndarray):
        draw_size = self._get_draw_size(coordinate_system)

        # filter out invalid positions
        screen_points = coordinate_system.space_to_screen(self.points.T).T
        valid_positions = _get_valid_positions(screen_points, draw_size, screen_size)
        screen_points = screen_points[valid_positions]
        valid_colors = self._colors[valid_positions]

        # create blit surfaces
        surfaces = _create_point_surfaces(self._color_set, draw_size)
        end_time = time.perf_counter()

        tuple_colors = [_color_to_tuple(c) for c in valid_colors]

        # draw
        blit_sequence = []
        for pos, color in zip(screen_points, tuple_colors):
            blit_sequence.append((surfaces[color], pos - draw_size))
        screen.blits(blit_sequence)

    def _get_draw_size(self, coordinate_system):
        draw_size = self.size
        if isinstance(draw_size, float):
            draw_size = max(int(draw_size * coordinate_system.zoom_factor), 1)
        return draw_size

    def clicked_points(self, event: pg.event.Event, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Returns the indices of the points clicked by the mouse. Returns an empty array if no point was clicked.

        :param event: The event to check.
        :param coordinate_system: The coordinate system to use.
        """
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            draw_size = self._get_draw_size(coordinate_system)

            screen_pos = np.array(event.pos).reshape(1, 2)
            screen_points = coordinate_system.space_to_screen(self.points.T).T
            distances = np.linalg.norm(screen_points - screen_pos, axis=1)
            return np.nonzero(distances < draw_size)[0]
        return np.array([])


def _create_point_surfaces(
        colors: List[ColorTuple], draw_size: int
) -> Dict[ColorTuple, pg.Surface]:
    surfaces = {}
    for color in colors:
        point_surface = pg.Surface((draw_size * 2, draw_size * 2), pg.SRCALPHA)
        point_surface.fill((0, 0, 0, 0))
        pg.draw.circle(point_surface, color, (draw_size, draw_size), draw_size)
        surfaces[color] = point_surface
    return surfaces


def _get_valid_positions(screen_points: np.ndarray, draw_size: int, screen_size: np.ndarray) -> np.ndarray:
    return np.where(np.logical_and(
        np.logical_and(screen_points[:, 0] > -draw_size, (screen_points[:, 0] < screen_size[0] + draw_size)),
        np.logical_and(screen_points[:, 1] > -draw_size, (screen_points[:, 1] < screen_size[1] + draw_size))
    ))[0]


def to_draw_positions(
        points: np.ndarray, coordinate_system: CoordinateSystem, valid_positions: np.ndarray
) -> np.ndarray:
    """
    Converts a list of points to a list of positions to draw them on the screen.
    Filters out points outside the screen.

    :param points: Numpy array of shape [N, 2] where N is the number of points.
    :param coordinate_system: The coordinate system to use.
    :param valid_positions: Array with shape [N], where N is the number of points. This array contains booleans
                            indicating, whether the point is visible on the screen.
    :return: Numpy array with shape [K, 2] where K is the number of valid points that are visible on the screen.
    """
    screen_points = coordinate_system.space_to_screen(points.T).T
    return screen_points[valid_positions].astype(int)
