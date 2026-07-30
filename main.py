##main.py

import pygame
import constants
import numpy as np
import time
import Choid
from   helpers import (
    get_frame_durations_delta_t, get_new_delta_t_frame_durations,
    fill_background, scale_to_screen_size,
    get_window_size, process_events
)

# TODO: proper documentation
# TODO: prevent choids from spawning into each other
# TODO: make subfuntions to get new pos/vel/speed values

def main() -> None:

    window = pygame.Window("Chud-oids simulator", constants.SCREEN_SIZE, resizable = True)
    screen = pygame.Surface(constants.SCREEN_SIZE)

    fullscreen = False
    abort      = False

    frame_durations, delta_t = get_frame_durations_delta_t()

    choid_manager = Choid.ChoidManager(200)
    choid_ui      = Choid.ChoidUI()

    while not abort:

        frame_start = time.time()

        choid_manager.update(delta_t)
        choid_ui.update(choid_manager)

        fill_background(screen)
        choid_manager.display(screen)
        choid_ui.display_ui(choid_manager, screen, delta_t)
        scale_to_screen_size(window.get_surface(), screen)

        window.flip()
        abort, fullscreen = process_events(window, abort, fullscreen)

        delta_t, frame_durations = get_new_delta_t_frame_durations(
            frame_durations, frame_start
        )

    return None

if __name__ == '__main__':
    main()
