## helpers.py

import time

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
