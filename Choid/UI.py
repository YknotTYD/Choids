##UI.py

import Choid
import pygame
import constants
import numpy as np
import math
import time
import random

def _modify_avoidance_radius(value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_AVOIDANCE_RADIUS += value * 25
    constants.CHOID_AVOIDANCE_RADIUS  = max(constants.CHOID_AVOIDANCE_RADIUS, 0)
    return None

def _modify_alignment_radius(value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_ALIGNMENT_RADIUS += value * 25
    constants.CHOID_ALIGNMENT_RADIUS  = max(constants.CHOID_ALIGNMENT_RADIUS, 0)
    return None

def _modify_cohesion_radius(value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_COHESION_RADIUS += value * 25
    constants.CHOID_COHESION_RADIUS  = max(constants.CHOID_COHESION_RADIUS, 0)
    return None

def _modify_choid_fov(value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_FOV += value * 15
    constants.CHOID_FOV  = min(max(constants.CHOID_FOV, 0), 360)
    return None

def _modify_current_force(value: int, choid_manager: Choid.ChoidManager) -> None:

    choid_manager.current_last_force += value
    choid_manager.current_last_force %= len(constants.FORCES)
    choid_manager.current_last_force  = max(choid_manager.current_last_force, 0)

    return None

def _modify_time_scaling(value: int, choid_manager: Choid.ChoidManager) -> None:

    if value == 1:
        value *= 0.1 if constants.TIME_SCALING_FACTOR < 1.0 else 0.2
    elif value == -1:
        value *= 0.1 if constants.TIME_SCALING_FACTOR <= 1.0 else 0.2
    else:
        return None

    constants.TIME_SCALING_FACTOR += value
    constants.TIME_SCALING_FACTOR = round(constants.TIME_SCALING_FACTOR, 1)
    constants.TIME_SCALING_FACTOR = max(constants.TIME_SCALING_FACTOR, 0)

    return None

def _modify_follow_scaling(value: int, choid_manager: Choid.ChoidManager) -> None:

    constants.FOLLOW_SCALING_FACTOR += value * 0.2
    constants.FOLLOW_SCALING_FACTOR  = round(constants.FOLLOW_SCALING_FACTOR, 1)
    constants.FOLLOW_SCALING_FACTOR  = max(constants.FOLLOW_SCALING_FACTOR, 1)
    constants.FOLLOW_SCALING_FACTOR  = min(constants.FOLLOW_SCALING_FACTOR, 4)

    return None

def _choid_count_to_amount(count: int) -> int:
    if count <= 10:
        return 1
    if count <= 75:
        return 5
    if count <= 150:
        return 10
    return 20

def _modify_choid_count(value: int, choid_manager: Choid.ChoidManager) -> None:

    choid_amount = _choid_count_to_amount(choid_manager.choid_count)

    if value == 1:

        new_pos       = choid_manager._get_new_pos(choid_amount)
        new_vel       = choid_manager._get_new_vel(choid_amount)
        new_max_speed = choid_manager._get_new_max_speed(choid_amount)

        choid_manager.choids_pos      = np.concat((choid_manager.choids_pos, new_pos), axis = 0)
        choid_manager.choids_vel      = np.concat((choid_manager.choids_vel, new_vel), axis = 0)
        choid_manager.choid_max_speed = np.concat((choid_manager.choid_max_speed, new_max_speed), axis = 0)
        choid_manager.choid_count    += choid_amount

        choid_manager._remove_choids_from_obstacles()
        return None

    if value != -1:
        return None

    if choid_amount >= choid_manager.choid_count:
        return None

    choid_manager.choids_pos      = choid_manager.choids_pos[:-choid_amount]
    choid_manager.choids_vel      = choid_manager.choids_vel[:-choid_amount]
    choid_manager.choid_max_speed = choid_manager.choid_max_speed[:-choid_amount]
    choid_manager.choid_count    -= choid_amount
    return None

def _modify_goal_count(value: int, choid_manager: Choid.ChoidManager) -> None:

    if value == 1:

        choid_manager.goals.append(None)
        choid_manager._update_goal(constants.GOAL_COUNT)
        constants.GOAL_COUNT += 1

        return None

    if value != -1 or constants.GOAL_COUNT <= 0:
        return None

    choid_manager.goals = choid_manager.goals[:-1]
    constants.GOAL_COUNT -= 1

    return None

def _modify_step_count(value: int, choid_manager: Choid.ChoidManager) -> None:

    if abs(value) != 1:
        return None

    constants.STEPS_PER_FRAME = min(max(constants.STEPS_PER_FRAME + value, 0), 10)
    return None

LINE_COUNT = 16
MODIFICATION_TABLE = [
    None,                     # mouse
    _modify_choid_count,      # choids
    _modify_goal_count,       # food
    _modify_avoidance_radius, # avoidance radius
    _modify_alignment_radius, # alignment radius
    _modify_cohesion_radius,  # cohesion  radius
    _modify_choid_fov,        # choid fov
    None,                     # speed min
    None,                     # speed avg
    None,                     # speed max
    None,                     # framerate
    _modify_current_force,    # current force
    _modify_time_scaling,     # time scaling
    _modify_step_count,       # step count
    _modify_follow_scaling,   # spectating scaling
]

class ChoidUI:

    def __init__(self) -> None:
        self.cursor_index = 0
        self.follow_index = None
        self.hide_panel   = False
        return None

    def _send_modification(self, value: int, choid_manager: Choid.ChoidManager) -> None:

        func = MODIFICATION_TABLE[self.cursor_index]

        if func is None:
            return None

        func(value, choid_manager)
        return None

    def update(self, choid_manager: Choid.ChoidManager) -> None:

        pressed = pygame.key.get_just_pressed()

        if pressed[pygame.K_DOWN]:
            self.cursor_index += 1
            self.cursor_index %= LINE_COUNT

        if pressed[pygame.K_UP]:
            self.cursor_index -= 1
            if self.cursor_index < 0:
                self.cursor_index = LINE_COUNT - 1

        if pressed[pygame.K_LEFT]:
            self._send_modification(-1, choid_manager)
        if pressed[pygame.K_RIGHT]:
            self._send_modification( 1, choid_manager)

        if pressed[pygame.K_RETURN]:
            self.follow_index = (
                None if self.follow_index is not None
                    else random.randrange(choid_manager.choid_count)
            )

        if pressed[pygame.K_SPACE]:
            self.hide_panel = not(self.hide_panel)

        return None

    @staticmethod
    def triangle_offset() -> float:
        return (
            (
                math.cos(time.time() * 2 * constants.PI / constants.CHOID_RENDER_TRIANGLE_DURATION) -
                constants.CHOID_RENDER_TRIANGLE_DURATION / 2
            ) * constants.CHOID_RENDER_TRIANGLE_AMPLITUDE
        )

    def _draw_cross(
            self,
            screen: pygame.Surface,
            screen_center: np.array
        ) -> None:

        cross_len = constants.CROSS_LEN / 2

        for t, color in zip(constants.CROSS_TICKNESSES, constants.CROSS_COLORS):
            pygame.draw.line(screen, color,
                (int(screen_center[0]) - cross_len, int(screen_center[1]) - cross_len),
                (int(screen_center[0]) + cross_len, int(screen_center[1]) + cross_len),
                t
            )
            pygame.draw.line(screen, color,
                (int(screen_center[0]) + cross_len, int(screen_center[1]) - cross_len),
                (int(screen_center[0]) - cross_len, int(screen_center[1]) + cross_len),
                t
            )
        return None

    def _scale_to_follow(
            self,
            screen: pygame.Surface,
            choid_manager: Choid.ChoidManager
        ) -> None:

        screen_center = choid_manager.choids_pos[self.follow_index].copy()

        center_xy_bounds = [
            (
                constants.SCREEN_SIZE[i] * (1 - 1 / (constants.FOLLOW_SCALING_FACTOR * 2)),
                constants.SCREEN_SIZE[i] / (constants.FOLLOW_SCALING_FACTOR * 2)
            )
            for i in range(2)
        ]

        self._draw_cross(screen, screen_center)

        for i, bounds in enumerate(center_xy_bounds):
            screen_center[i] = max(min(screen_center[i], bounds[0]), bounds[1])

        blit_pos = [
            int(coord - constants.SCREEN_SIZE[i] / (constants.FOLLOW_SCALING_FACTOR * 2))
                for i, coord in enumerate(screen_center)
        ]

        zoom = pygame.Surface(constants.SCREEN_SIZE)
        zoom.blit(screen, (0, 0, *constants.SCREEN_SIZE), (*blit_pos, *constants.SCREEN_SIZE))
        zoom = pygame.transform.smoothscale_by(zoom, constants.FOLLOW_SCALING_FACTOR)
        screen.blit(zoom, (0, 0), (0, 0, *constants.SCREEN_SIZE))

        return None

    def display_ui(
            self, choid_manager: Choid.ChoidManager,
            screen: pygame.Surface, delta_t: float
    ) -> None:

        if self.follow_index is not None:
            self._scale_to_follow(screen, choid_manager)
            return None

        if self.hide_panel:
            return None

        speeds = np.linalg.norm(choid_manager.choids_vel, axis = 1)
        lines = [
            (1, 0, f"mouse : {pygame.mouse.get_pos()}"),
            (0, 0, ""),
            (1, 1, f"choids: {choid_manager.choid_count}"),
            (1, 1, f"food:   {constants.GOAL_COUNT}"),
            (1, 1, f"avoidance radius: {constants.CHOID_AVOIDANCE_RADIUS}"),
            (1, 1, f"alignment radius: {constants.CHOID_ALIGNMENT_RADIUS}"),
            (1, 1, f"cohesion  radius: {constants.CHOID_COHESION_RADIUS}" ),
            (0, 0, ""),
            (1, 1, f"choid fov: {constants.CHOID_FOV}%"),
            (1, 0, f"speed min: {speeds.min():.0f}"    ),
            (1, 0, f"speed avg: {speeds.mean():.0f}"   ),
            (1, 0, f"speed max: {speeds.max():.0f}"    ),
            (1, 0, f"framerate: {round(1 / delta_t, 1)} fps"),
            (1, 1, f"current force:   {constants.FORCES[choid_manager.current_last_force]}"),
            (1, 1, f"time scaling:    {constants.TIME_SCALING_FACTOR}"),
            (1, 1, f"step count:      {constants.STEPS_PER_FRAME}"),
            (1, 1, f"spectating scaling: {constants.FOLLOW_SCALING_FACTOR}"),
            (0, 0, ""                        ),
            (0, 0, "[controls]:"             ),
            (0, 0, ""                        ),
            (0, 0, "[up/down]:"              ),
            (0, 0, "  move cursor"           ),
            (0, 0, "[left/right]:"           ),
            (0, 0, "  modify value"          ),
            (0, 0, "[enter]:"                ),
            (0, 0, "  toggle spectating mode"),
            (0, 0, "[space]:"                ),
            (0, 0, "  hide/show panel"       ),
        ]

        padding = 8
        line_height = 20
        box_w = 290 + 24
        box_h = padding * 2 + line_height * len(lines)

        panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        screen.blit(panel, (10, 10))

        triangle_h = 10
        triangle_w = 5
        triangle   = ((0, -triangle_w), (0, +triangle_w), (triangle_h, 0))
        line_index = -1

        for i, (line_index_offset, is_modifiable, line) in enumerate(lines):

            line_index += line_index_offset
            pos = (24 + 10 + padding, 10 + padding + i * line_height)

            surf = choid_manager.font.render(line, True, (230, 230, 230))

            if line_index == self.cursor_index and line_index_offset:
                pygame.draw.polygon(
                    screen,
                    "green" if is_modifiable else "red",
                    [
                        (24 + c0 + ChoidUI.triangle_offset(), pos[1] + surf.get_height() / 2 + c1)
                            for c0, c1 in triangle
                    ],
                )

            screen.blit(surf, pos)

        return None
