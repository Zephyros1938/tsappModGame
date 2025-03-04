import zephyros1938.tsappMod as tsappMod
import zephyros1938.tsapp as tsapp

class Entity2D(tsappMod.PolygonalObject):
    def __init__(self,name = str, movementSpeed = float, config = tsappMod.PolygonalObjectConfig(), debug_config = tsappMod.PolygonalObjectDebugConfig()):
        super().__init__(config=config, debug_config=debug_config)
        self.move_speed = movementSpeed
        self.name = name