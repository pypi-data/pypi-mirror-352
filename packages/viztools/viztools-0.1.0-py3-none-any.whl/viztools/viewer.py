from abc import abstractmethod, ABC
from typing import Tuple, Optional, List

import pygame as pg

from viztools.coordinate_system import DEFAULT_SCREEN_SIZE, CoordinateSystem, draw_coordinate_system
from viztools.drawable import Drawable


class Viewer(ABC):
    def __init__(
            self, screen_size: Optional[Tuple[int, int]] = None, framerate: int = 60, font_size: int = 16,
    ):
        pg.init()
        pg.key.set_repeat(130, 25)

        self.running = True
        self.render_needed = True
        self.clock = pg.time.Clock()
        self.framerate = framerate

        screen_size = screen_size or DEFAULT_SCREEN_SIZE
        if screen_size == (0, 0):
            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode(screen_size, pg.RESIZABLE)

        self.coordinate_system = CoordinateSystem(screen_size)

        self.render_font = pg.font.Font(pg.font.get_default_font(), font_size)

    def run(self):
        delta_time = 0
        while self.running:
            self._handle_events()
            self.tick(delta_time)
            if self.render_needed:
                self._render()
                self.render_needed = False
            delta_time = self.clock.tick(self.framerate)
        pg.quit()

    @abstractmethod
    def tick(self, delta_time: float):
        pass

    @abstractmethod
    def render(self):
        pass

    def render_drawables(self, drawables: List[Drawable]):
        for drawable in drawables:
            drawable.draw(self.screen, self.coordinate_system)

    def render_coordinate_system(self):
        draw_coordinate_system(self.screen, self.coordinate_system, self.render_font)

    def _render(self):
        self.render()
        pg.display.flip()

    def _handle_events(self):
        events = pg.event.get()
        for event in events:
            self.handle_event(event)

    @abstractmethod
    def handle_event(self, event: pg.event.Event):
        if self.coordinate_system.handle_event(event):
            self.render_needed = True
        if event.type == pg.QUIT:
            self.running = False
