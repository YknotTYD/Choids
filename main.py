##main.py

import pygame
import constants
import numpy as np
import time
from   helpers import get_frame_durations_delta_t, get_new_delta_t_frame_durations

#multiple boid groups
#cap angular velocity

class ChoidManager:

    def __init__(self, choid_count: int) -> None:
        self.choids_pos =  np.random.randint(0, 1000, (choid_count, 2)).astype(np.float32)
        self.choids_vel = (np.random.random((choid_count, 2)) - 0.5) * 150
        self.choid_max_speed = (np.random.random(choid_count) + 0.2) * 100

        self.choid_count = choid_count
        return None

    def update(self, delta_t: float) -> None:

        for i, choid in enumerate(self.choids_pos):

            away = choid - self.choids_pos.copy()

            distance  = np.linalg.norm(away, axis = 1)
            valid_ids = (distance <= constants.CHOID_AVOIDANCE_RADIUS) & (distance > 0)

            away = away[valid_ids]
            distance  = distance[valid_ids]

            vels = constants.CHOID_AVOIDANCE_FORCE / distance
            dirs = away / distance[:,np.newaxis]

            avoidance = np.average(vels[:, np.newaxis] * dirs, axis = 0)
            alignment = np.average(self.choids_vel[valid_ids], axis = 0) - self.choids_vel[i]
            cohesion  = np.average(self.choids_pos[valid_ids]) - self.choids_pos[i]

            self.choids_vel[i] = self.choids_vel[i] * 0.8 + (self.choids_vel[i] + avoidance + alignment + cohesion) * 0.3

            norm  = np.linalg.norm(self.choids_vel[i], axis = 0)
            units = self.choids_vel[i] / norm

            if norm > self.choid_max_speed[i]:
                norm = self.choid_max_speed[i]

            self.choids_vel[i] = units * norm

        self.choids_pos += self.choids_vel * delta_t
        self.choids_pos = np.fmod(self.choids_pos, constants.SCREEN_SIZE)

        return None

    def display(self, screen: pygame.display) -> None:

        for pos, vel in zip(self.choids_pos, self.choids_vel):
            pygame.draw.aaline(screen, "green", pos.astype(np.int64), pos + vel, 2)

        for pos in self.choids_pos:
            pygame.draw.aacircle(screen, "red", pos.astype(np.int64), 4)

        return None

def main() -> None:

    screen = pygame.display.set_mode(constants.SCREEN_SIZE, pygame.RESIZABLE)
    abort  = False
    choid_manager = ChoidManager(200)
    frame_durations, delta_t = get_frame_durations_delta_t()

    while not abort:

        frame_start = time.time()

        screen.fill(constants.BACKGROUND_COLOR)
        choid_manager.update(delta_t)
        choid_manager.display(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                abort = True

        delta_t, frame_durations = get_new_delta_t_frame_durations(
            frame_durations, frame_start
        )

    return None

if __name__ == '__main__':
    main()
