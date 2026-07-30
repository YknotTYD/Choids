##Choid.py

import pygame
import numpy as np
import constants

class ChoidManager:

    def __init__(self, choid_count: int) -> None:

        self.choids_pos =  np.random.randint(0, 1000, (choid_count, 2)).astype(np.float32)
        self._remove_choids_from_obstacles()
        self.choids_vel = (np.random.random((choid_count, 2)) - 0.5) * 150
        self.choid_max_speed = np.random.randint(
            constants.CHOID_SPEED_RANGE[0],
            constants.CHOID_SPEED_RANGE[1] + 1,
            choid_count
        )

        self.choid_count = choid_count
        self.goal = None
        self._update_goal()

        pygame.init()
        self.font = pygame.font.SysFont("consolas", 18)
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

    def _set_random_goal(self) -> None:

        is_invalid = True

        while is_invalid:

            self.goal = np.array([np.random.randint(0, constants.SCREEN_SIZE[i]) for i in range(2)])
            is_invalid = False

            for x, y, r in constants.OBSTACLES:
                if np.linalg.norm(self.goal - np.array((x, y)), axis = 0) <= (r + constants.CHOID_OBSTACLE_MARGIN):
                    is_invalid = True
                    break

        return None

    def _update_goal(self) -> None:

        if self.goal is None:
            self._set_random_goal()
            return None

        if pygame.mouse.get_focused():
            pass#return None

        norms = np.linalg.norm(self.choids_pos - self.goal, axis = 1)

        if np.any(norms < 8):
            self._set_random_goal()

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

    def _get_goal_pos(self) -> np.array:

        if pygame.mouse.get_focused():
            pass#return np.array(pygame.mouse.get_pos())
            
        return self.goal

    def _goal_force(self, i, strength = 100, arrive_radius = 60):
        goal = np.array(self._get_goal_pos()) - self.choids_pos[i]
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
        valid_fov = angles < (3.14159265358979323846264338327950288419716939937510582097494459 * constants.CHOID_FOV / 180)

        avoid_ids, align_ids, cohes_ids = self._neighbor_masks(distance, valid_fov)

        avoidance = self._avoidance_force(away, distance, avoid_ids)
        alignment = self._alignment_force(i, align_ids)
        cohesion  = self._cohesion_force(i, cohes_ids)
        obstacle  = self._obstacle_force(i)
        goal      = self._goal_force(i)

        steer = (self.choids_vel[i] * 0.00 + obstacle + goal + avoidance + alignment + cohesion)

        self.choids_vel[i] = self.choids_vel[i] + 0.2 * steer
        self._limit_speed(i)
        self._update_goal()

        return None

    def _wrap_positions(self):
        for i in range(2):
            break
            self.choids_pos[:,i][self.choids_pos[:,i] > constants.SCREEN_SIZE[i]] = 0
            self.choids_pos[:,i][self.choids_pos[:,i] < 0] = constants.SCREEN_SIZE[i]

    def update(self, delta_t: float) -> None:

        for i, choid in enumerate(self.choids_pos):
            self._update_choid_velocity(i, choid)

        self.choids_pos += self.choids_vel * delta_t
        self._wrap_positions()

        return None

    def display(self, screen: pygame.display) -> None:

        for pos, vel in zip(self.choids_pos, self.choids_vel):
            pygame.draw.aaline(screen, "green", pos.astype(np.int64), pos + vel * 0.2, 2)

        pygame.draw.aacircle(screen, "yellow", self.goal, 4)

        for x, y, r in constants.OBSTACLES:
            pygame.draw.aacircle(screen, (22, 22, 88), (x, y), r)

        for pos in self.choids_pos:
            pygame.draw.aacircle(screen, "red", pos.astype(np.int64), 4)

        return None
