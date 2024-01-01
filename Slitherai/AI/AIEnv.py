from typing import Any, List, Optional, Sequence, Tuple

import numpy as np
import pyray as pr
from gymnasium.spaces import Box, Discrete
from stable_baselines3.common.vec_env import VecEnv
from stable_baselines3.common.vec_env.base_vec_env import (
    VecEnvIndices,
    VecEnvObs,
    VecEnvStepReturn,
)

from Slitherai.Environment.Constants import (
    MAX_LENGTH,
    MIN_BOOST_RADIUS,
    OPTIMAL_RESOLUTION_WIDTH,
)
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.GridWorld import GridWorld
from Slitherai.Environment.Core.World import World
from Slitherai.Environment.Food import Food, FoodSpawner
from Slitherai.Environment.Server import Server
from Slitherai.Environment.SnakeBodyComponent import ServerSnakeBodyComponent


# Create Vectorized Environment
class AIEnv(VecEnv, Server):
    def __init__(
        self,
        num_players: int,
        world_size: int = 50000,
        max_steps: int = -1,
        frame_rate=60,
    ):
        # Variables
        self.frame_rate = frame_rate
        self.num_players = num_players
        self.render_mode = None
        self.world_size = world_size

        # Initialize world
        self.worlds: List[World] = []
        self.active_world: int = -1
        world = GridWorld(self.world_size, 50)

        # Initialize manager
        food_spawner = FoodSpawner(self)
        self.manager_entity = Entity("Manager", [food_spawner])
        world.add_entity(self.manager_entity)

        # Initialize Players
        self.players = [
            ServerSnakeBodyComponent(
                pr.Vector2(0, 0), pr.Vector2(0, 0), i, food_spawner
            )
            for i in range(self.num_players)
        ]

        self.closest_foods = 25
        self.closest_players = 10
        self.observation_size = (
            (MAX_LENGTH - 1) * 2
            + 6
            + self.closest_foods * 3
            + self.closest_players * (4 + 2 * MAX_LENGTH)
        )

        # Add players to the world
        for i in range(num_players):
            world.add_entity(Entity(f"Player {i}", [self.players[i]]))

        # Finish Initializing world
        self.add_world(world)
        self.set_active_world(0)
        self.activate_world()

        # Initialize action list
        self.action_list = [
            # W, A, S, D, Space
            (True, False, False, False, False),  # W
            (False, True, False, False, False),  # A
            (False, False, True, False, False),  # S
            (False, False, False, True, False),  # D
            (True, True, False, False, False),  # W + A
            (True, False, False, True, False),  # W + D
            (False, True, True, False, False),  # A + S
            (False, False, True, True, False),  # S + D
            (True, False, False, False, True),  # W + Space
            (False, True, False, False, True),  # A + Space
            (False, False, True, False, True),  # S + Space
            (False, False, False, True, True),  # D + Space
            (True, True, False, False, True),  # W + A + Space
            (True, False, False, True, True),  # W + D + Space
            (False, True, True, False, True),  # A + S + Space
            (False, False, True, True, True),  # S + D + Space
        ]

        # Track Timeout
        self.max_steps = max_steps
        self.num_steps = 0

        super().__init__(
            num_players,
            Box(
                low=-self.world_size,
                high=self.world_size,
                shape=(self.observation_size,),
                dtype=np.float32,
            ),
            Discrete(len(self.action_list)),
        )

    def get_action(self, action: np.ndarray) -> Tuple[bool, bool, bool, bool, bool]:
        return self.action_list[action]

    def get_observations(self, player: ServerSnakeBodyComponent) -> np.ndarray:
        # My Snake Body Observations
        origin = player.bodies[0]

        observations = np.zeros((self.observation_size,), np.float32)
        i = 0

        # My radius [1 float]
        observations[i] = player.radius
        i += 1

        # direction [2 floats] already normalized
        observations[i] = player.direction.x
        i += 1
        observations[i] = player.direction.y
        i += 1

        # Is Boosting [1 float] 0 or 1
        observations[i] = 1.0 if player.is_boosting() else 0.0
        i += 1

        # My Body parts as distance from head [2 float]
        for body_part in player.bodies[1:]:
            delta = pr.vector2_subtract(body_part, origin)
            observations[i] = delta.x
            i += 1
            observations[i] = delta.y
            i += 1

        # If less than 99 body parts, fill with 0s
        for _ in range(MAX_LENGTH - len(player.bodies)):
            observations[i] = 0
            i += 1
            observations[i] = 0
            i += 1

        # Total Floats 202

        # Environment Observations
        # Closest Distance to Edge [2 floats] normalized using world_size
        if origin.x > self.world_size / 2:
            observations[i] = self.world_size - origin.x
        else:
            observations[i] = -origin.x
        i += 1

        if origin.y > self.world_size / 2:
            observations[i] = self.world_size - origin.y
        else:
            observations[i] = -origin.y
        i += 1

        # Food and Player Observations
        observed_entity_indices = (
            self.get_active_world().grid.get_collisions_within_area(  # type: ignore
                origin, OPTIMAL_RESOLUTION_WIDTH
            )
        )
        foods: List[Food | None] = []
        players: List[ServerSnakeBodyComponent | None] = []

        for entity_index in observed_entity_indices:
            entity = self.get_active_world().entities[entity_index]
            component = entity.get_component(ServerSnakeBodyComponent.component_id)
            if component is None:
                continue

            if component.collision_type == Food.collision_type:
                foods.append(component)
            elif component.collision_type == ServerSnakeBodyComponent.collision_type:
                players.append(component)

        # Not filled with any nones if greater than 25. If less than 25, filled with Nones
        if len(foods) > self.closest_foods:
            foods = sorted(
                foods,
                key=lambda food: pr.vector_2distance_sqr(food.bodies[0], origin),  # type: ignore
            )[: self.closest_foods]
        else:
            foods += [None for _ in range(self.closest_foods - len(foods))]

        if len(players) > self.closest_players:
            players = sorted(
                players,
                key=lambda player: pr.vector_2distance_sqr(player.bodies[0], origin),  # type: ignore
            )[: self.closest_players]  # type: ignore
        else:
            players += [None for _ in range(self.closest_players - len(players))]

        # Closest 25 Foods and their radius and distance [3 floats].
        # If less than 25 foods, fill with 0s
        for food in foods:
            if food is not None:
                observations[i] = food.radius
                i += 1

                delta = pr.vector2_subtract(food.bodies[0], origin)
                observations[i] = delta.x
                i += 1
                observations[i] = delta.y
                i += 1
            else:
                observations[i] = 0
                i += 1
                observations[i] = 0
                i += 1
                observations[i] = 0
                i += 1

        # Total Floats 77

        # 10 Closest Player Information
        for p in players:
            if p is not None and p.id != player.id:
                # My radius [1 float]
                observations[i] = p.radius
                i += 1
                # direction [2 floats] normalized
                observations[i] = p.direction.x
                i += 1
                observations[i] = p.direction.y
                i += 1
                # Is Boosting [1 float] 0 or 1
                observations[i] = 1.0 if p.is_boosting() else 0.0
                i += 1
                # My Body parts as distance from head [2 float] * 100 normalized using world size
                for body_part in p.bodies:
                    delta = pr.vector2_subtract(body_part, origin)
                    observations[i] = delta.x
                    i += 1
                    observations[i] = delta.y
                    i += 1
                # If less than 100 body parts, fill with 0s
                for _ in range(MAX_LENGTH - len(p.bodies)):
                    observations[i] = 0
                    i += 1
                    observations[i] = 0
                    i += 1
            else:
                observations[i] = 0
                i += 1
                observations[i] = 0
                i += 1
                observations[i] = 0
                i += 1
                observations[i] = 0
                i += 1
                for _ in range(MAX_LENGTH):
                    observations[i] = 0
                    i += 1
                    observations[i] = 0
                    i += 1
        # Total Floats 2020
        if i != 2319:
            raise Exception("Observation size is not 2319")
        return observations  # Full Total Floats 2319

    def step_async(self, actions: np.ndarray) -> None:
        self.actions = actions

    def step_wait(self) -> VecEnvStepReturn:
        # Set Actions to the players
        for i in range(self.num_players):
            w, a, s, d, space = self.get_action(self.actions[i])
            self.players[i].set_controls(w, a, s, d, space)

        self.get_active_world().update(1 / self.frame_rate)
        self.get_active_world().update_grid()  # type: ignore

        # Get the observation, reward, done, info for each player
        observations = np.array(
            [self.get_observations(player) for player in self.players]
        )
        rewards = np.zeros((self.num_players,), np.float32)
        dones = np.zeros((self.num_players,), np.bool_)
        infos = [{} for _ in range(self.num_players)]

        event = self.get_active_world().consume_event()
        # TODO : Better reward system
        while event is not None:
            if event.type == 0:  # Food Eaten
                entity_id = event.EntityThatAte
                mass_eaten = event.MassEaten
                # TODO: Food Eating Reward
                rewards[entity_id] += mass_eaten / 50  # Max reward is 1
            elif event.type == 1:  # Player Killed
                entity_id = event.EntityKilled
                killer_id = event.KilledBy

                # TODO: Killed by border reward
                if killer_id is None:
                    rewards[entity_id] -= 100

                # TODO: Killed by other player reward
                rewards[entity_id] -= 10

                # Terminate the player
                dones[entity_id] = True  # Cannot be truncated
                infos[entity_id]["TimeLimit.truncated"] = False
                infos[entity_id]["terminal_observation"] = observations[entity_id]
                self.reset_player(entity_id, True)
                self.get_active_world().update_grid()  # type: ignore
                observations[entity_id] = self.get_observations(self.players[entity_id])

            elif event.type == 2:  # Player Kill
                entity_id = event.EntityThatKilled
                # killed_id = event.KilledEntity

                # TODO: Kill reward
                rewards[entity_id] += 10

            event = self.get_active_world().consume_event()

        # TODO: Other rewards
        for i in range(self.num_players):
            if not self.players[i].can_boost() and self.actions[i] >= 8:
                rewards[i] -= MIN_BOOST_RADIUS - self.players[i].radius

        # Max Steps
        self.num_steps += 1
        if self.max_steps != -1 and self.num_steps >= self.max_steps:
            for i in range(self.num_players):
                infos[i]["TimeLimit.truncated"] = True and not dones[i]
                dones[i] = True
                infos[i]["terminal_observation"] = observations[i]

        return observations, rewards, dones, infos

    def reset(self) -> VecEnvObs:
        self.num_steps = 0
        for i in range(self.num_players):
            self.reset_player(i)

        # Get Active world returns world. What is stored is GridWorld
        self.get_active_world().update_grid()  # type: ignore
        return np.array([self.get_observations(player) for player in self.players])

    def reset_player(self, player_id: int, dead=False) -> None:
        location = pr.Vector2(
            np.random.randint(0, self.world_size), np.random.randint(0, self.world_size)
        )
        direction = pr.Vector2(np.random.choice([-1, 1]), np.random.choice([-1, 1]))
        self.players[player_id].reset(location, direction)
        if dead:
            self.get_active_world().add_entity(
                Entity(f"Player {player_id}", [self.players[player_id]])
            )

    def __del__(self):
        self.worlds[self.active_world].destroy()

    def close(self) -> None:
        self.__del__()

    def get_attr(self, attr_name: str, indices: VecEnvIndices = None) -> List[Any]:
        value = self.__getattribute__(attr_name)
        return [value for _ in range(self.num_players)]

    def set_attr(
        self, attr_name: str, value: Any, indices: VecEnvIndices = None
    ) -> None:
        self.__setattr__(attr_name, value)

    def env_method(
        self,
        method_name: str,
        *method_args,
        indices: VecEnvIndices = None,
        **method_kwargs,
    ) -> List[Any]:
        value = self.__getattribute__(method_name)(*method_args, **method_kwargs)
        return [value for _ in range(self.num_players)]

    def env_is_wrapped(
        self, wrapper_class: type, indices: VecEnvIndices = None
    ) -> List[bool]:
        from stable_baselines3.common import env_util

        value = env_util.is_wrapped(self, wrapper_class)  # type: ignore
        return [value for _ in range(self.num_players)]

    def get_images(self) -> Sequence[Optional[np.ndarray]]:
        return [None for _ in range(self.num_players)]


if __name__ == "__main__":
    print("Testing AIEnv")
    env = AIEnv(10, 50000)
    obs = env.reset()
    for step in range(1000):
        obs, rewards, dones, infos = env.step(env.action_space.sample())
        print(f"Step {step}")
