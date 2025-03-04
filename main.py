import zephyros1938.tsapp as tsapp
import zephyros1938.tsappMod as tsappMod
import threading as th
from zephyros1938.overrides import *

class GameConfig():
    def __init__(
        self, width: int, height: int, title: str, color: (int, int, int)
    ):
        self.width = width
        self.height = height
        self.title = title
        self.color = color


class Game:
    display: tsappMod.Surface
    logicThread: th.Thread
    displayThread: th.Thread
    threads = []

    def __init__(
        self,
        windowargs=GameConfig(250, 250, "TEST", (0xFF, 0xFF, 0xFF)),
    ):
        self.windowargs = windowargs
        self.width = windowargs.width
        self.height = windowargs.height
        self.title = windowargs.title
        self.color = windowargs.color
        self.display = tsappMod.Surface(
            width=self.windowargs.width, height=self.windowargs.height, title=self.windowargs.title, background_color=self.windowargs.color
        )
        print(self.display._surface.get_flags())

    def gameLogicLoop(self):
        pass

    def gameDisplayLoop(self):
        self.display.finish_frame()

    def run(self):
        self.logicThread = th.Thread(target=self.gameLogicLoop)
        self.displayThread = th.Thread(target=self.gameDisplayLoop)
        self.threads.append(self.logicThread)
        self.threads.append(self.displayThread)
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()


class Main(metaclass=AutoCastMeta):
    game: Game

    def __init__(self, *args, **kwargs):
        self.game = Game()
        self.game.run()


if __name__ == "__main__":
    Main()
