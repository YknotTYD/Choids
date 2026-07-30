##Choid.py

import pygame
import numpy as np
import constants

_FORCES = constants.FORCES

class ChoidManager:

    def _get_new_pos(self, count: int) -> np.array:
        return np.random.randint(0, 1000, (count, 2)).astype(np.float32)

    def _get_new_vel(self, count: int) -> np.array:
        return (np.random.random((count, 2)) - 0.5) * 150

    def _get_new_max_speed(self, count: int) -> np.array:
        return np.random.randint(
            constants.CHOID_SPEED_RANGE[0],
            constants.CHOID_SPEED_RANGE[1] + 1,
            count
        )

    def __init__(self, choid_count: int) -> None:

        self.choids_pos = self._get_new_pos(choid_count)
        self._remove_choids_from_obstacles()

        self.choids_vel = self._get_new_vel(choid_count)
        self.choid_max_speed = self._get_new_max_speed(choid_count)

        self.choid_count = choid_count
        self.goals = [None] * constants.GOAL_COUNT

        for i in range(constants.GOAL_COUNT):
            self._update_goal(i)

        pygame.init()
        self.font = pygame.font.SysFont("consolas", 18)

        self.last_forces = dict()
        for key in _FORCES:
            self.last_forces[key] = []

        self.current_last_force = 0

        return None

    def _remove_choids_from_obstacles(self) -> None:

        for i in range(len(self.choids_pos)):

            is_invalid = True

            while is_invalid:

                is_invalid = False

                for x, y, r in constants.OBSTACLES:
                    if np.linalg.norm(self.choids_pos[i] - np.array((x, y)), axis = 0) <= (r + constants.CHOID_OBSTACLE_MARGIN):
                        is_invalid = True
                        self.choids_pos[i] = np.random.randint(0, 1000, (2,))
                        break

        return None

    def _set_random_goal(self, i: int) -> None:

        is_invalid = True

        while is_invalid:

            self.goals[i] = np.array([np.random.randint(50, constants.SCREEN_SIZE[i] - 50) for i in range(2)])
            is_invalid = False

            for x, y, r in constants.OBSTACLES:
                if np.linalg.norm(self.goals[i] - np.array((x, y)), axis = 0) <= (r + constants.CHOID_OBSTACLE_MARGIN):
                    is_invalid = True
                    break

        return None

    def _update_goal(self, i: int) -> None:

        if self.goals[i] is None:
            self._set_random_goal(i)
            return None

        if pygame.mouse.get_focused():
            pass#return None

        norms = np.linalg.norm(self.choids_pos - self.goals[i], axis = 1)

        if np.any(norms < 8):
            self._set_random_goal(i)

        return None

    def _neighbor_masks(self, distance, valid_fov) -> tuple[np.array,np.array, np.array]:
        avoid_ids = (distance <= constants.CHOID_AVOIDANCE_RADIUS) & (distance > 0) & valid_fov
        align_ids = (distance <= constants.CHOID_ALIGNMENT_RADIUS) & (distance > 0) & valid_fov
        cohes_ids = (distance <= constants.CHOID_COHESION_RADIUS)  & (distance > 0) & valid_fov
        return (avoid_ids, align_ids, cohes_ids)

    def _avoidance_force(self, away, distance, avoid_ids) -> np.array:

        if not np.any(avoid_ids):
            return np.zeros(2, dtype = np.float32)

        d = distance[avoid_ids]
        vels = constants.CHOID_AVOIDANCE_FORCE / d
        dirs = away[avoid_ids] / d[:, np.newaxis]

        return np.average(vels[:, np.newaxis] * dirs, axis = 0)

    def _alignment_force(self, i, align_ids) -> np.array:

        if not np.any(align_ids):
            return np.zeros(2, dtype = np.float32)

        return np.average(self.choids_vel[align_ids], axis = 0) - self.choids_vel[i]

    def _cohesion_force(self, i, cohes_ids) -> np.array:

        if not np.any(cohes_ids):
            return np.zeros(2, dtype = np.float32)

        return np.average(self.choids_pos[cohes_ids], axis = 0) - self.choids_pos[i]

    def _obstacle_force(self, i): #TODO: @HERE

        pos = self.choids_pos[i]
        steer = np.zeros(2, dtype = np.float32)

        for ox, oy, r in constants.OBSTACLES:

            away = pos - np.array([ox, oy], dtype = np.float32)
            dist = np.linalg.norm(away)
            edge_dist = dist - r

            if edge_dist < constants.CHOID_OBSTACLE_MARGIN and dist > 0:
                steer += (constants.CHOID_OBSTACLE_FORCE / (edge_dist ** 2 + 1)) * (away / dist)

        return steer

    def _get_goal_index(self, i: int) -> int:

        if pygame.mouse.get_focused():
            pass#return np.array(pygame.mouse.get_pos())

        dist = np.linalg.norm(np.array(self.goals) - self.choids_pos[i], axis = 1)
        return np.argmin(dist)

    def _goal_force(self, i, strength = 100, arrive_radius = 60) -> np.array:

        if constants.GOAL_COUNT == 0:
            return np.array((0, 0))

        goal = np.array(self.goals[self._get_goal_index(i)]) - self.choids_pos[i]
        dist = np.linalg.norm(goal)
        if dist == 0:
            return np.zeros(2, dtype = np.float32)

        scale = min(dist / arrive_radius, 1.0)
        return (goal / dist) * strength * scale

    def _limit_speed(self, i) -> None:

        norm = np.linalg.norm(self.choids_vel[i], axis = 0)

        if norm == 0:
            return None

        units = self.choids_vel[i] / norm
        norm  = min(norm, self.choid_max_speed[i])
        self.choids_vel[i] = units * norm

        return None

    def _update_choid_velocity(self, i, choid) -> None:

        away = choid - self.choids_pos
        distance = np.linalg.norm(away, axis = 1)

        vects  = self.choids_pos - choid
        angles = np.abs(np.arctan2(vects[:, 1], vects[:, 0]))
        valid_fov = angles < (constants.PI * constants.CHOID_FOV / 180)

        avoid_ids, align_ids, cohes_ids = self._neighbor_masks(distance, valid_fov)

        avoidance = self._avoidance_force(away, distance, avoid_ids)
        alignment = self._alignment_force(i, align_ids)
        cohesion  = self._cohesion_force(i, cohes_ids)
        obstacle  = self._obstacle_force(i)
        goal      = self._goal_force(i)

        for key, value in (
            ("avoidance", avoidance), ("alignment", alignment),
            ("cohesion",  cohesion),  ("obstacle",  obstacle),
            ("goal",      goal)
        ):
            self.last_forces[key].append(value)

        steer = (obstacle + goal + avoidance + alignment + cohesion)

        self.choids_vel[i] = self.choids_vel[i] + 0.2 * steer
        self._limit_speed(i)

        for i in range(constants.GOAL_COUNT):
            self._update_goal(i)

        return None

    def _wrap_positions(self) -> None:

        if constants.GOAL_COUNT > 0:
            return None

        for i in range(2):
            self.choids_pos[:,i][self.choids_pos[:,i] > constants.SCREEN_SIZE[i]] = 0
            self.choids_pos[:,i][self.choids_pos[:,i] < 0] = constants.SCREEN_SIZE[i]

        return None

    def _update_last_force(self) -> None:

        for key in self.last_forces.keys():
            self.last_forces[key] = []

        return None

    def update(self, delta_t: float) -> None:

        self._update_last_force()

        for i, choid in enumerate(self.choids_pos):
            self._update_choid_velocity(i, choid)

        self.choids_pos += self.choids_vel * delta_t * constants.TIME_SCALING_FACTOR
        self._wrap_positions()

        return None

    def display(self, screen: pygame.display) -> None:

        for goal in self.goals:
            pygame.draw.aacircle(screen, "yellow", goal, 4)

        for x, y, r in constants.OBSTACLES:
            pygame.draw.aacircle(screen, constants.OBSTACLE_RENDER_COLOR, (x, y), r)

        for i, (pos, vel) in enumerate(zip(self.choids_pos, self.choids_vel)):

            norm  = vel / np.linalg.norm(vel, axis = 0)
            top   = pos + norm * constants.CHOID_RENDER_H
            angle = np.atan2(norm[1], norm[0])

            left  = angle + constants.PI / 2
            right = angle - constants.PI / 2

            left  = pos + np.array([np.cos(left), np.sin(left)])   * constants.CHOID_RENDER_W / 2
            right = pos + np.array([np.cos(right), np.sin(right)]) * constants.CHOID_RENDER_W / 2

            top   -= norm * constants.CHOID_RENDER_H / 2
            left  -= norm * constants.CHOID_RENDER_H / 2
            right -= norm * constants.CHOID_RENDER_H / 2

            if i >= len(self.last_forces[_FORCES[self.current_last_force]]): # just in case
                color = "white"
            else:
                color_range = constants.CHOID_RENDER_FORCE_COLOR_RANGE[_FORCES[self.current_last_force]]
                larp  = np.linalg.norm((self.last_forces[_FORCES[self.current_last_force]][i]), axis = 0)
                larp  = min(larp, color_range) / color_range
                larp_correction = 0.5 - abs(larp - 0.5)
                color = (255 * larp + 255 * larp_correction, 255 - 255 * larp + 255 * larp_correction, 0)

            pygame.draw.polygon(screen, color, (left, right, top))

        return None
