##main.py

import pygame
import constants
import numpy as np
import time
import Choid
from   helpers import get_frame_durations_delta_t, get_new_delta_t_frame_durations

#multiple boid groups
#cap angular velocity

def main() -> None:

    screen = pygame.display.set_mode(constants.SCREEN_SIZE)
    abort  = False
    choid_manager = Choid.ChoidManager(200)
    frame_durations, delta_t = get_frame_durations_delta_t()

    while not abort:

        frame_start = time.time()

        choid_manager.update(delta_t)

        screen.fill(constants.BACKGROUND_COLOR)
        choid_manager.display(screen)
        Choid.UI.display_ui(choid_manager, screen, delta_t)

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
