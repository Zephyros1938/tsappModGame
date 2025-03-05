import queue
from time import sleep
from typing import List
import threading
import pygame
from zephyros1938.csharp import *

pygame.init()

_ACTIVE_WINDOW = None
_GLOBAL_EVENT_LIST = []
_BARRIER = threading.Barrier(4)
_EVENT_THREAD_FINISH = threading.Event()
_DRAW_MANAGER_THREAD_FINISH = threading.Event()
_RENDER_THREAD_FINISH = threading.Event()


class WindowArgs(metaclass=AutoCastMeta):
    def __init__(
        self,
        width=Int16(1080),
        height=Int16(1080),
        name=String("zephApp Window"),
        background_color=(Byte(255), Byte(255), Byte(255)),
        pygame_gl_args=pygame.OPENGL | pygame.DOUBLEBUF,
        framerate=SByte(-1),
        vsync=Boolean(1),
    ):
        if vsync != 0 and vsync != 1:
            raise ValueError(f"vsync window argument must be 0/1, got {vsync}")
        self.width = width
        self.height = height
        self.name = name
        self.background_color = background_color
        self.pygame_gl_args = pygame_gl_args
        self.framerate = framerate
        self.vsync = vsync


class Window(Object, metaclass=AutoCastMeta):

    def __init__(self, windowargs=WindowArgs()):
        self.windowargs = windowargs
        self._surface = pygame.display.set_mode(
            [self.windowargs.width, self.windowargs.height],
            self.windowargs.pygame_gl_args,
        )

        self._clock = pygame.time.Clock()
        self._draw_list = []
        self._pending_draw_list = []
        self.running = Boolean(0)

        global _ACTIVE_WINDOW
        _ACTIVE_WINDOW = self

    def _get_width(self) -> Int16:
        return self.windowargs.width

    def _set_width(self, width: Int16):
        self.windowargs.width = width
        self._surface = pygame.display.set_mode(
            size=[self.windowargs.width, self.windowargs.height],
            flags=self.windowargs.pygame_gl_args,
            vsync=self.windowargs.vsync,
        )

    width = property(_get_width, _set_width)

    def _get_height(self) -> Int16:
        return self.windowargs.height

    def _set_height(self, height: Int16):
        self.windowargs.height = height
        self._surface = pygame.display.set_mode(
            [self.windowargs.width, self.windowargs.height],
            self.windowargs.pygame_gl_args,
        )

    height = property(_get_height, _set_height)

    @property
    def delta(self) -> Single:
        return self._clock.get_time() / 1000.0

    def _RENDER_THREAD(self):
        while self.running:
            self._clock.tick(self.windowargs.framerate)
            self._surface.fill(self.windowargs.background_color)
            for item in self._draw_list:
                item._draw()
            pygame.display.flip()
            print("RENDR TICK", self.delta)
            try:
                _BARRIER.wait()
            except threading.BrokenBarrierError:
                break
        _BARRIER.wait()

    def _LOGIC_THREAD(self):
        while self.running:
            for item in self._draw_list:
                if item.destroyed:
                    item.destroy()
                else:
                    item._update()
            print("LOGIC TICK", self.delta)
            try:
                _BARRIER.wait()
            except threading.BrokenBarrierError:
                break
        _BARRIER.wait()

    def _EVENT_THREAD(self):
        while self.running:
            global _GLOBAL_EVENT_LIST
            _GLOBAL_EVENT_LIST = pygame.event.get()
            if any(event.type == pygame.QUIT for event in _GLOBAL_EVENT_LIST):
                self.Cleanup()
            print("EVENT TICK", self.delta)
            try:
                _BARRIER.wait()
            except threading.BrokenBarrierError:
                break
        _BARRIER.wait()

    def _DRAW_ADDITION_THREAD(self):
        while self.running:
            for item in self._pending_draw_list:
                self._draw_list.append(item)
                self._pending_draw_list.remove(item)
            print("DRAWR TICK", self.delta)
            try:
                _BARRIER.wait()
            except threading.BrokenBarrierError:
                break
        _BARRIER.wait()

    def Run(self):
        self.running = Boolean(1)
        self.threadpool = [
            threading.Thread(target=ev)
            for ev in [
                self._LOGIC_THREAD,
                self._DRAW_ADDITION_THREAD,
                self._EVENT_THREAD,
            ]
        ]
        [t.start() for t in self.threadpool]
        self._RENDER_THREAD()
        self.Cleanup()

    def Cleanup(self):
        print("Cleaning Up...")
        self.running = Boolean(0)
        for t in self.threadpool:
            print(t.name)
            print(f"{t.is_alive()}")
            t.join()
            print(f"{t.is_alive()}")


class GraphicalObject(Object, metaclass=AutoCastMeta):
    def __init__(self):
        self.visible = Boolean(True)
        self._vel_x = Single(0.0)
        self._vel_y = Single(0.0)
        self.destroyed = Boolean(False)

    def _draw(self):
        raise NotImplementedError(
            "All GraphicalObjects must have a way of drawing themselves"
        )

    def _update():
        pass

    def _get_vel_x(self) -> Single:
        return self._vel_x

    def _set_vel_x(self, new: Single):
        self._vel_x = new

    def _get_vel_y(self) -> Single:
        return self._vel_y

    def _set_vel_y(self, new: Single):
        self._vel_y = new

    vel_x = property(_get_vel_x, _set_vel_x)
    vel_y = property(_get_vel_y, _set_vel_y)

    def _get_vel(self) -> Vector2:
        return (self.vel_x, self.vel_y)

    def _set_vel(self, vx=None, vy=None, v=None):
        if vx != None and vy != None:
            self.vel_x = vx
            self.vel_y = vy
        elif v != None:
            v2 = Vector2.ToVector2(v)
            self.vel_x = v2.X
            self.vel_y = v2.Y
        else:
            raise ValueError(f"Could not change velocity of {self.__qualname__}")

    vel = property(_get_vel, _set_vel)

    def Destroy(self):
        self.destroyed = Boolean(True)


class PolygonalObject(GraphicalObject, metaclass=AutoCastMeta):

    def __init__(self, x, y, points: List[Vector2]):
        super().__init__()
        self.x = x
        self.y = y
