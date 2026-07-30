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

    pygame.draw.rect(screen, constants.BACKGROUND_COLOR, (0, 0, *constants.SCREEN_SIZE))
    #screen.draw.rect(constants.BACKGROUND_COLOR)

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

def get_window_size(window: pygame.Window) -> tuple[int, int]:
    size    = list(window.size)
    size[1] = int((size[0] / constants.SCREEN_SIZE[0]) * constants.SCREEN_SIZE[1])
    return size

def scale_to_screen_size(window_surface, screen: pygame.Surface) -> None:
    scale = window_surface.get_width() / constants.SCREEN_SIZE[0]
    scaled = pygame.transform.scale_by(screen, scale)
    window_surface.blit(scaled, (0, 0))
    return None
