import zephyros1938.tsappMod as tsappMod
from zephyros1938.tsappMod import Builtins as TSMConst
import zephyros1938.tsapp as tsapp
import entity
import math
import random

display = tsappMod.Surface(width=1280, height=720, background_color=(0, 0, 0))
camera = tsappMod.Camera2D(0, 0)

q = 32
l = q * display.aspect_ratio
l2 = l / 2

debug_config = tsappMod.PolygonalObjectDebugConfig(True, True, True, True)

pconfig = config = tsappMod.PolygonalObjectConfig(
    points=[
        [l2, -l2],
        [-((l * (math.sqrt(3) / 10)) - l2), 0],
        [l2, l2],
        [-((l * (math.sqrt(3) / 2)) - l2), 0],
    ],
    color=(255, 0, 255),
    linewidth=0,
)

p = entity.Entity2D(name="Player", movementSpeed=200, config=pconfig)

p2 = tsappMod.PolygonalObject(
    config=tsappMod.PolygonalObjectConfig(
        points=[[-l2, -l2], [l2, -l2], [l2, l2], [-l2, l2]],
        color=(128, 0, 128),
        linewidth=0,
        center=[display.width, display.height],
        attraction_radius=100 * display.aspect_ratio,
    ),
    debug_config=debug_config,
)

# Set initial centers
p2.center_x = display.width / 2
p2.center_y = display.height / 2
p.center_x = display.width / 2
p.center_y = display.height / 2

player_info = tsappMod.TextLabel(
    "CourierNew.ttf", 25, 0, 25, display.width, "EMPTY", (255, 255, 255)
)
performance_info = tsappMod.TextLabel(
    "CourierNew.ttf", 25, 0, 25, display.width, "FPS_METER", (255, 255, 255)
)
camera_info = tsappMod.TextLabel(
    "CourierNew.ttf",
    25,
    0,
    display.height - 25,
    display.width,
    "CAMERA_INFO",
    (255, 255, 255),
)
performance_info.align = "right"
display.framerate = -1

display.add_object(player_info)
display.add_object(performance_info)
display.add_object(camera_info)
display.add_object(p2)
display.add_object(p)

GUI_UPDATE_TICK = 0
DECELERATION_TICK = 0
WANDER_TICK = 0

P_MOVE_SPEED = 200
P2_MOVE_SPEED = 200

while display.is_running:
    dt = display.deltatime  # cache delta time
    mouse_pos = tsapp.get_mouse_position()

    if tsapp.is_key_down(TSMConst.Special.K_ESCAPE):
        exit()

    # Cache movement delta value
    move_delta = P_MOVE_SPEED * dt

    # Cache movement key states
    move_keys = (
        tsapp.is_key_down(tsapp.K_w),
        tsapp.is_key_down(tsapp.K_s),
        tsapp.is_key_down(tsapp.K_a),
        tsapp.is_key_down(tsapp.K_d),
    )

    if move_keys[0]:
        p.move_forward(move_delta)
    if move_keys[1]:
        p.move_backward(move_delta)
    if move_keys[2]:
        p.move_left(move_delta)
    if move_keys[3]:
        p.move_right(move_delta)

    if tsappMod.is_mouse_down(TSMConst.Mouse.M_RIGHT):
        p.rotate_to(mouse_pos)

    # Update camera position according to player
    camera.origin_x = p.center[0] - display.width / 2
    camera.origin_y = p.center[1] - display.height / 2

    # GUI update every 60 seconds (adjust threshold as needed)
    if GUI_UPDATE_TICK >= display.seconds_passed(seconds=60):
        player_info.text = f"PLAYER\nPOS: {p.world_center} R: {(p.current_angle_rad / tsappMod.Math.tau) * 360}"
        performance_info.text = f"FPS: {display._clock.get_fps()}"
        camera_info.text = f"CAMERA\nPOS: {camera.origin}"
        GUI_UPDATE_TICK = 0

    # Deceleration logic every 60 seconds
    if DECELERATION_TICK >= display.seconds_passed(60):
        # Decelerate p if no movement keys are pressed
        if not any(move_keys) and p.speed != (0, 0):
            p.x_speed *= 0.75
            p.y_speed *= 0.75
            if tsapp.is_key_down(tsapp.K_e):
                p.x_speed *= 0.8
                p.y_speed *= 0.8
            if abs(p.x_speed) <= 1 and abs(p.y_speed) <= 1:
                p.x_speed, p.y_speed = 0, 0

        # Decelerate p2 if outside its attraction radius
        if (
            p2.speed != (0, 0)
            and tsappMod.Math.magnitude(p2.world_center, p.world_center)
            >= p2.config.attraction_radius
        ):
            p2.x_speed *= 0.75
            p2.y_speed *= 0.75
            if abs(p2.x_speed) <= 1 and abs(p2.y_speed) <= 1:
                p2.x_speed, p2.y_speed = 0, 0

        DECELERATION_TICK = 0

    # p2 moves toward p if within attraction radius
    if (
        tsappMod.Math.magnitude(p2.world_center, p.world_center)
        < p2.config.attraction_radius
    ):
        p2.rotate_to(p.world_center)
        p2.move_forward(P2_MOVE_SPEED * dt)
    elif WANDER_TICK >= display.seconds_passed(240):
        speed = random.randint(P2_MOVE_SPEED, P2_MOVE_SPEED * 10)
        while WANDER_TICK >= 0:
            p2.rotate_rad(random.uniform(0, tsappMod.Math.tau))
            p2.move_forward(speed * dt)
            WANDER_TICK -= dt
        WANDER_TICK = 0

    # Increment timers using dt
    GUI_UPDATE_TICK += dt
    DECELERATION_TICK += dt
    WANDER_TICK += dt

    display.finish_frame()
