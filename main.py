##main.py

import pygame
import constants
import numpy as np
import time
import Choid
from   helpers import (
    get_frame_durations_delta_t, get_new_delta_t_frame_durations,
    fill_background, scale_to_screen_size, get_window_size
)

# TODO: (cap angular velocity)?
# TODO: goal count
# TODO: add a button to follow a guy
# TODO: check if window is currently being resized or otherwise add a timer to prevent jittering on resize

def main() -> None:

    window = pygame.Window("Chud-oids simulator", constants.SCREEN_SIZE, resizable = True)
    screen = pygame.Surface(constants.SCREEN_SIZE)
    fullscreen = False

    abort  = False
    choid_manager = Choid.ChoidManager(200)
    choid_ui      = Choid.ChoidUI()
    frame_durations, delta_t = get_frame_durations_delta_t()

    while not abort:

        frame_start = time.time()

        choid_manager.update(delta_t)
        choid_ui.update(choid_manager)

        fill_background(screen)
        choid_manager.display(screen)
        choid_ui.display_ui(choid_manager, screen, delta_t)
        scale_to_screen_size(window.get_surface(), screen)

        window.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                abort = True
                break
            if event.type == pygame.WINDOWMAXIMIZED:
                fullscreen = True
            if event.type == pygame.WINDOWRESIZED:
                if fullscreen:
                    fullscreen = False
                    continue
                window.size = get_window_size(window)

        delta_t, frame_durations = get_new_delta_t_frame_durations(
            frame_durations, frame_start
        )

    return None

if __name__ == '__main__':
    main()
