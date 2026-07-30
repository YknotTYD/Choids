##UI.py

import Choid
import pygame
import constants
import numpy as np
import math
import time
import random

def _modify_avoidance_radius(self, value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_AVOIDANCE_RADIUS += value * 25
    constants.CHOID_AVOIDANCE_RADIUS  = max(constants.CHOID_AVOIDANCE_RADIUS, 0)
    return None

def _modify_alignment_radius(self, value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_ALIGNMENT_RADIUS += value * 25
    constants.CHOID_ALIGNMENT_RADIUS  = max(constants.CHOID_ALIGNMENT_RADIUS, 0)
    return None

def _modify_cohesion_radius(self, value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_COHESION_RADIUS += value * 25
    constants.CHOID_COHESION_RADIUS  = max(constants.CHOID_COHESION_RADIUS, 0)
    return None

def _modify_choid_fov(self, value: int, choid_manager: Choid.ChoidManager) -> None:
    constants.CHOID_FOV += value * 15
    constants.CHOID_FOV  = min(max(constants.CHOID_FOV, 0), 360)
    return None

def _modify_current_force(self, value: int, choid_manager: Choid.ChoidManager) -> None:

    choid_manager.current_last_force += value
    choid_manager.current_last_force %= len(constants.FORCES)
    choid_manager.current_last_force  = max(choid_manager.current_last_force, 0)

    return None

def _modify_time_scaling(self, value: int, choid_manager: Choid.ChoidManager) -> None:

    constants.TIME_SCALING_FACTOR += value * 0.1
    constants.TIME_SCALING_FACTOR = round(constants.TIME_SCALING_FACTOR, 1)
    constants.TIME_SCALING_FACTOR = max(constants.TIME_SCALING_FACTOR, 0)

    #choid_manager.current_last_force += value
    #choid_manager.current_last_force %= len(constants.FORCES)
    #choid_manager.current_last_force  = max(choid_manager.current_last_force, 0)

    return None

LINE_COUNT = 12
MODIFICATION_TABLE = {
    0:  None,#(1, 0, f"mouse : {pygame.mouse.get_pos()}"),
    1:  None,#(1, 1, f"choids: {choid_manager.choid_count}"),
    2:  _modify_avoidance_radius,#(1, 1, f"avoidance radius: {constants.CHOID_AVOIDANCE_RADIUS}"),
    3:  _modify_alignment_radius,#(1, 1, f"alignment radius: {constants.CHOID_ALIGNMENT_RADIUS}"),
    4:  _modify_cohesion_radius,#(1, 1, f"cohesion  radius: {constants.CHOID_COHESION_RADIUS}"),
    5:  _modify_choid_fov,#(1, 0, f"choid fov: {constants.CHOID_FOV}%"),
    6:  None,#(1, 0, f"speed min: {speeds.min():.0f}"),
    7:  None,#(1, 0, f"speed avg: {speeds.mean():.0f}"),
    8:  None,#(1, 0, f"speed max: {speeds.max():.0f}"),
    9:  None,#(1, 0, f"framerate: {round(1 / delta_t, 1)} fps"),
    10: _modify_current_force,#(1, 0, f"current force: {constants.FORCES[choid_manager.current_last_force]}"),
    11: _modify_time_scaling,#(1, 0, f"current force: {constants.FORCES[choid_manager.current_last_force]}"),

}

class ChoidUI:

    def __init__(self) -> None:
        self.cursor_index = 0
        self.follow_index = None
        return None

    def _send_modification(self, value: int, choid_manager: Choid.ChoidManager) -> None:

        func = MODIFICATION_TABLE[self.cursor_index]

        if func is None:
            return None

        func(self, value, choid_manager)
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

        if pressed[pygame.K_RETURN] or pressed[pygame.K_SPACE]:
            self.follow_index = (
                None if self.follow_index is not None
                    else random.randrange(choid_manager.choid_count)
            )

        return None

    @staticmethod
    def triangle_offset() -> float:
        return (
            (
                math.cos(time.time() * 2 * constants.PI / constants.CHOID_RENDER_TRIANGLE_DURATION) -
                constants.CHOID_RENDER_TRIANGLE_DURATION / 2
            ) * constants.CHOID_RENDER_TRIANGLE_AMPLITUDE
        )

    def _scale_to_follow(
            self,
            screen: pygame.Surface,
            choid_manager: Choid.ChoidManager
        ) -> None:

        blit_pos = [
            int(choid - constants.SCREEN_SIZE[i] / (constants.FOLLOW_SCALING_FACTOR * 2))
                for i, choid in enumerate(choid_manager.choids_pos[self.follow_index])
        ]

        zoom = pygame.Surface(constants.SCREEN_SIZE)
        zoom.blit(screen, (0, 0, *constants.SCREEN_SIZE), (*blit_pos, *constants.SCREEN_SIZE))
        zoom = pygame.transform.smoothscale_by(zoom, constants.FOLLOW_SCALING_FACTOR)
        screen.blit(zoom, (0, 0), (0, 0, *constants.SCREEN_SIZE))
        # choid_manager.choids_pos[self.follow_index]

        return None

    def display_ui(
            self, choid_manager: Choid.ChoidManager,
            screen: pygame.Surface, delta_t: float
    ) -> None:

        if self.follow_index is not None:
            self._scale_to_follow(screen, choid_manager)
            return None

        speeds = np.linalg.norm(choid_manager.choids_vel, axis = 1)
        lines = [
            (1, 0, f"mouse : {pygame.mouse.get_pos()}"),
            (0, 0, ""),
            (1, 0, f"choids: {choid_manager.choid_count}"),
            (1, 1, f"avoidance radius: {constants.CHOID_AVOIDANCE_RADIUS}"),
            (1, 1, f"alignment radius: {constants.CHOID_ALIGNMENT_RADIUS}"),
            (1, 1, f"cohesion  radius: {constants.CHOID_COHESION_RADIUS}" ),
            (0, 0, ""),
            (1, 1, f"choid fov: {constants.CHOID_FOV}%"),
            (1, 0, f"speed min: {speeds.min():.0f}"    ),
            (1, 0, f"speed avg: {speeds.mean():.0f}"   ),
            (1, 0, f"speed max: {speeds.max():.0f}"    ),
            (1, 0, f"framerate: {round(1 / delta_t, 1)} fps"),
            (1, 1, f"current force: {constants.FORCES[choid_manager.current_last_force]}"),
            (1, 1, f"time scaling:  {constants.TIME_SCALING_FACTOR}"),
            (0, 0, ""                  ),
            (0, 0, "[controls]:"       ),
            (0, 0, ""                  ),
            (0, 0, "[up/down]:"        ),
            (0, 0, "   move cursor"    ),
            (0, 0, "[left/right]:"     ),
            (0, 0, "   modify value"   ),
            (0, 0, "[enter/space]:"    ),
            (0, 0, "   follow/unfollow")
        ]

        padding = 8
        line_height = 20
        box_w = 280 + 24
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
