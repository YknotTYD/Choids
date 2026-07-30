## helpers.py

import time
import pygame
import constants

def get_frame_durations_delta_t() -> tuple[list, float]:
    return ([None] * 60, 1 / 60)

def get_new_delta_t_frame_durations(frame_durations: list, frame_start: float) -> tuple[float, list]:

    frame_durations_cpy = frame_durations.copy()
    frame_durations_cpy.append(time.time() - frame_start)
    del frame_durations_cpy[0]

    delta_t = (sum([f for f in frame_durations_cpy if f]) /
        (len(frame_durations_cpy) - frame_durations_cpy.count(None))
    )

    return (delta_t, frame_durations_cpy)

def fill_background(screen: pygame.display) -> None:

    screen.fill(constants.BACKGROUND_COLOR)

    for index in range(2):
        val = constants.BACKGROUND_GRID_SPACING
        while val < constants.SCREEN_SIZE[index]:
            pygame.draw.aaline(
                screen, constants.BACKGROUND_GRID_COLOR,
                (val, 0)[::(-1 if index else 1)],
                (val, max(constants.SCREEN_SIZE))[::(-1 if index else 1)],
            )
            val += constants.BACKGROUND_GRID_SPACING

    return None
