from zephyros1938.csharp import *
import zephyros1938.zephApp as zephApp

w = zephApp.Window(zephApp.WindowArgs(1080, 720, "TESTWINDOW", (0x00, 0xFF, 0x00), vsync=1, framerate=60))

t = zephApp.PolygonalObject(100, 100, [(0, 0), (10, 10), (0, 10)])

w.Run()