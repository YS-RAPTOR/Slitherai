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
from Slitherai.Environment.CameraComponent import ServerCameraComponent
from Slitherai.Environment.Constants import (
    INITIAL_FOOD_SPAWN,
    MAX_LENGTH,
    MIN_BOOST_RADIUS,
    OPTIMAL_RESOLUTION_WIDTH,
)
from Slitherai.AI.Constants import (
    ACTION_LIST,
    CLOSEST_FOODS,
    CLOSEST_PLAYERS,
    OBSERVATION_SIZE,
)
from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.GridWorld import GridWorld
from Slitherai.Environment.Core.World import World
from Slitherai.Environment.Food import Food, FoodSpawner
from Slitherai.Server import Server
from Slitherai.Environment.SnakeBodyComponent import ServerSnakeBodyComponent


# Create Vectorized Environment
class AIEnv(VecEnv, Server):
    def __init__(
        self,
        num_players: int,
        world_size: int = 50000,
        max_steps: int = -1,
        initial_food_spawn: int = INITIAL_FOOD_SPAWN,
        reset_food_every: int = 2,
        frame_rate=20,
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
        self.food_spawner = FoodSpawner(self, initial_food_spawn)
        self.manager_entity = Entity("Manager", [self.food_spawner])
        world.add_entity(self.manager_entity)

        # Initialize Players
        self.players = [
            ServerSnakeBodyComponent(
                pr.Vector2(0, 0), pr.Vector2(0, 0), i, self.food_spawner
            )
            for i in range(self.num_players)
        ]

        # Add players to the world
        for i in range(num_players):
            world.add_entity(Entity(f"Player {i}", [self.players[i]]))

        # Finish Initializing world
        self.add_world(world)
        self.set_active_world(0)
        self.activate_world()

        # Track Timeout
        self.max_steps = max_steps
        self.num_steps = [0 for _ in range(self.num_players)]

        # Food Reset
        self.reset_food_every = reset_food_every
        self.num_resets = 0

        # Reward Stuff
        self.closest_food = [(-1.0, 0.0, pr.Vector2(0, 0)) for _ in range(num_players)]

        super().__init__(
            num_players,
            Box(
                low=-self.world_size,
                high=self.world_size,
                shape=(OBSERVATION_SIZE,),
                dtype=np.float32,
            ),
            Discrete(len(ACTION_LIST)),
        )

    def get_action(self, action: np.ndarray) -> Tuple[bool, bool, bool, bool, bool]:
        return ACTION_LIST[action]

    def get_observations(self, player: ServerSnakeBodyComponent) -> np.ndarray:
        # My Snake Body Observations
        origin = player.bodies[0]

        observations = np.zeros((OBSERVATION_SIZE,), np.float32)
        i = 0

        # My radius [1 float]
        observations[i] = player.radius
        i += 1

        # direction [2 floats] already normalized
        observations[i] = player.direction.x
        i += 1
        observations[i] = player.direction.y
        i += 1

        # Is Boosting [1 float] -1 or 1
        observations[i] = 1.0 if player.is_boosting() else -1
        i += 1

        # Can Boost [1 float] -1 or 1
        observations[i] = 1.0 if player.can_boost() else -1
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
        observations[i] = (self.world_size - origin.x) / self.world_size
        i += 1
        observations[i] = (self.world_size - origin.y) / self.world_size
        i += 1
        observations[i] = (-origin.x) / self.world_size
        i += 1
        observations[i] = (-origin.y) / self.world_size
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
        if len(foods) > CLOSEST_FOODS:
            foods = sorted(
                foods,
                key=lambda food: pr.vector_2distance(food.bodies[0], origin),  # type: ignore
            )[:CLOSEST_FOODS]
        else:
            foods += [None for _ in range(CLOSEST_FOODS - len(foods))]

        # Remove self
        for index in range(len(players)):
            if players[index].id == player.id:  # type: ignore
                players.pop(index)
                break

        if len(players) > CLOSEST_PLAYERS:
            players = sorted(
                players,
                key=lambda player: pr.vector_2distance(player.bodies[0], origin),  # type: ignore
            )[:CLOSEST_PLAYERS]
        else:
            players += [None for _ in range(CLOSEST_PLAYERS - len(players))]

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
            if p is not None:
                # My radius [1 float]
                observations[i] = p.radius
                i += 1
                # direction [2 floats] normalized
                observations[i] = p.direction.x
                i += 1
                observations[i] = p.direction.y
                i += 1
                # Is Boosting [1 float] -1 or 1
                observations[i] = 1.0 if p.is_boosting() else -1
                i += 1
                # Can Boost [1 float] -1 or 1
                observations[i] = 1.0 if p.can_boost() else -1
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
                observations[i] = 0
                i += 1
                for _ in range(MAX_LENGTH):
                    observations[i] = 0
                    i += 1
                    observations[i] = 0
                    i += 1
        # Total Floats 2020

        # Closest Food Distance [1 float]
        if foods[0] is not None:
            self.closest_food[player.id] = (
                pr.vector_2distance(foods[0].bodies[0], origin),
                foods[0].mass,
                pr.vector2_normalize(pr.vector2_subtract(foods[0].bodies[0], origin)),
            )
        else:
            self.closest_food[player.id] = (-1.0, 0.0, pr.Vector2(0, 0))

        if i != OBSERVATION_SIZE:
            raise Exception("Observation size is not 2319")

        # Check if finite
        if not np.isfinite(observations).all():
            raise Exception("Observation is not finite")

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

        while event is not None:
            if event.type == 0:  # Food Eaten
                entity_id = event.EntityThatAte
                mass_eaten = event.MassEaten
                # Food Eating Reward
                rewards[entity_id] += mass_eaten * 30
            elif event.type == 1:  # Player Killed
                entity_id = event.EntityKilled
                killer_id = event.KilledBy

                if killer_id is None:
                    # Killed by border reward
                    rewards[entity_id] -= 5000
                else:
                    # Killed by other player reward. Also, if killed by smaller player, give bigger punishment
                    rewards[entity_id] -= np.max(
                        [
                            self.players[entity_id].radius
                            - self.players[killer_id].radius,
                            10,
                        ]
                    )

                # Terminate the player
                dones[entity_id] = True  # Cannot be truncated
                infos[entity_id]["TimeLimit.truncated"] = False
                infos[entity_id]["terminal_observation"] = observations[entity_id]
                self.reset_player(entity_id, True)
                self.get_active_world().update_grid()  # type: ignore
                observations[entity_id] = self.get_observations(self.players[entity_id])

            elif event.type == 2:  # Player Kill
                entity_id = event.EntityThatKilled
                killed_id = event.KilledEntity

                # Kill reward. If killed bigger player, give bigger reward
                rewards[entity_id] += np.max(
                    [
                        self.players[killed_id].radius - self.players[entity_id].radius,
                        10,
                    ]
                )
            event = self.get_active_world().consume_event()

        # Misc
        for i in range(self.num_players):
            if not dones[i]:
                # Size reward
                rewards[i] += (self.players[i].length() / MAX_LENGTH) * 100

                # Getting closer to food reward and facing the direction of the food
                dist_to_food_norm = self.closest_food[i][0] / 3000

                # If no food, then no reward
                if dist_to_food_norm > 0:
                    angle = pr.vector_2dot_product(
                        self.players[i].direction, self.closest_food[i][2]
                    )
                    rewards[i] += (
                        angle
                        * (1 - dist_to_food_norm)
                        * np.max([5, self.closest_food[i][1]])
                    )

                # Center distance reward
                center_dist = pr.vector_2distance(
                    pr.Vector2(self.world_size // 2, self.world_size // 2),
                    self.players[i].bodies[0],
                )

                rewards[i] += (
                    1 - center_dist / ((self.world_size / 2) - self.world_size * 0.1)
                ) * 5

            if not self.players[i].can_boost() and self.actions[i] >= 8:
                # Boosting when not allowed. Reward is greater if you are closer to being able to boost
                rewards[i] -= MIN_BOOST_RADIUS - self.players[i].radius

            # Rescale rewards
            rewards[i] /= 100

            self.num_steps[i] += 1
            # Max Steps
            if self.max_steps != -1 and self.num_steps[i] >= self.max_steps:
                infos[i]["TimeLimit.truncated"] = True and not dones[i]
                dones[i] = True
                infos[i]["terminal_observation"] = observations[i]
                observations[i] = self.reset_player(i)

        return observations, rewards, dones, infos

    def reset_food(self):
        self.get_active_world().entities.clear()

        self.get_active_world().entities.append(self.manager_entity)
        for i in range(self.num_players):
            if not self.players[i].is_dead:
                self.get_active_world().entities.append(self.players[i].get_entity())

        # Spawn new food
        self.food_spawner.init()

    def reset(self) -> VecEnvObs:
        self.num_steps = [0 for _ in range(self.num_players)]
        self.num_resets = 0
        self.closest_food = [
            (-1.0, 0.0, pr.Vector2(0, 0)) for _ in range(self.num_players)
        ]

        self.reset_food()
        for i in range(self.num_players):
            self.reset_player(i)

        self.num_resets = 0

        # Get Active world returns world. What is stored is GridWorld
        self.get_active_world().update_grid()  # type: ignore
        return np.array([self.get_observations(player) for player in self.players])

    def reset_player(self, player_id: int, dead=False) -> None:
        # Delete all the food and spawn new food
        self.num_steps[player_id] = 0
        self.closest_food[player_id] = (-1.0, 0.0, pr.Vector2(0, 0))
        self.num_resets += 1
        if self.num_resets >= self.reset_food_every:
            self.num_resets = 0
            self.reset_food()

        location = pr.Vector2(
            np.random.randint(int(self.world_size * 0.25), int(self.world_size * 0.75)),
            np.random.randint(int(self.world_size * 0.25), int(self.world_size * 0.75)),
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


class AIEnvUI(AIEnv):
    def __init__(
        self,
        num_players: int,
        world_size: int,
        max_steps: int = -1,
        initial_food_spawn: int = INITIAL_FOOD_SPAWN,
        reset_food_every: int = 2,
        frame_rate: int = 20,
    ):
        super().__init__(
            num_players,
            world_size,
            max_steps,
            initial_food_spawn,
            reset_food_every,
            frame_rate,
        )
        pr.init_window(1920 // 2, 1080 // 2, "Slitherai")
        center = pr.Vector2(1920 // 4, 1080 // 4)
        camera = pr.Camera2D(center, pr.Vector2(world_size // 2, world_size // 2), 0, 1)
        self.init_camera(camera)
        self.camera_component = ServerCameraComponent(self)
        self.manager_entity.components.append(self.camera_component)
        self.ui_entity = Entity("UI", [AIInfo(self)])
        self.worlds[self.active_world].add_ui_entity(self.ui_entity)
        self.targetted_player = 0

    def step_wait(self) -> VecEnvStepReturn:
        vals = super().step_wait()
        if pr.window_should_close():
            raise KeyboardInterrupt

        if pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT):
            self.targetted_player = (self.targetted_player - 1) % self.num_players
        if pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT):
            self.targetted_player = (self.targetted_player + 1) % self.num_players

        self.ui_entity.components[0].set_reward(vals[1][self.targetted_player])  # type: ignore

        self.camera.target = self.players[self.targetted_player].bodies[0]
        self.draw()
        return vals

    def __del__(self):
        super().__del__()
        pr.close_window()


class AIInfo(Component):
    def __init__(self, app: AIEnvUI) -> None:
        self.app = app

    def set_reward(self, reward: float) -> None:
        self.reward = reward

    def draw(self, camera: pr.Camera2D) -> None:
        text = f"Targetting Player {self.app.targetted_player}\nRewards: {self.reward}\nNum Steps: {self.app.num_steps[self.app.targetted_player]}"
        pr.draw_text(
            text,
            10,
            70,
            20,
            pr.Color(0, 0, 0, 255),
        )


if __name__ == "__main__":
    print("Testing AIEnv")
    num_agents = 10
    env = AIEnvUI(num_agents, 7500, 1000, 10, 60)
    obs = env.reset()
    for step in range(10000):
        obs, rewards, dones, infos = env.step(
            np.array([env.action_space.sample() for _ in range(num_agents)])
        )
        for i in range(len(rewards)):
            print(f"Agent {i} got reward {rewards[i]}")
        print(f"Step {step}")

