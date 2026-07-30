##UI.py

import Choid
import pygame
import constants
import numpy as np

class UI:

    @staticmethod
    def display_ui(self: Choid, screen: pygame.display, delta_t: float) -> None:

        speeds = np.linalg.norm(self.choids_vel, axis = 1)

        lines = [
            f"mouse : {pygame.mouse.get_pos()}",
            f"choids: {self.choid_count}",
            f"avoidance radius: {constants.CHOID_AVOIDANCE_RADIUS}",
            f"alignment radius: {constants.CHOID_ALIGNMENT_RADIUS}",
            f"cohesion  radius: {constants.CHOID_COHESION_RADIUS}",
            f"choid fov: {constants.CHOID_FOV}%",
            f"speed min: {speeds.min():.0f}",
            f"speed avg: {speeds.mean():.0f}",
            f"speed max: {speeds.max():.0f}",
            f"framerate: {round(1 / delta_t, 1)} fps",
        ]

        padding = 8
        line_height = 20
        box_w = 260
        box_h = padding * 2 + line_height * len(lines)

        panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        screen.blit(panel, (10, 10))

        for i, line in enumerate(lines):
            surf = self.font.render(line, True, (230, 230, 230))
            screen.blit(surf, (10 + padding, 10 + padding + i * line_height))

        return None