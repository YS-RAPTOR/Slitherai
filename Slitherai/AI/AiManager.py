from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.SnakeBodyComponent import ServerSnakeBodyComponent
from Slitherai.Environment.Food import Food, FoodSpawner
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH, MAX_LENGTH
from Slitherai.AI.Constants import (
    ACTION_LIST,
    CLOSEST_FOODS,
    CLOSEST_PLAYERS,
    OBSERVATION_SIZE,
)
from stable_baselines3 import PPO
from typing import List
import numpy as np
import pyray as pr


class AiManager(Component):
    def __init__(
        self,
        app: Application,
        model_path,
        food_spawner: FoodSpawner,
        num_players=20,
    ):
        self.app = app
        self.num_players = num_players

        self.model = PPO.load(model_path)

        self.players: List[ServerSnakeBodyComponent] = [
            ServerSnakeBodyComponent(
                pr.Vector2(0, 0), pr.Vector2(0, 0), 0 - i - 1, food_spawner
            )
            for i in range(self.num_players)
        ]

    def reset_player(self, player_id: int, dead=False) -> None:
        location = pr.Vector2(
            np.random.randint(0, self.world_size), np.random.randint(0, self.world_size)
        )
        direction = pr.Vector2(np.random.choice([-1, 1]), np.random.choice([-1, 1]))
        self.players[player_id].reset(location, direction)
        if dead:
            self.app.get_active_world().add_entity(
                Entity(f"Player {player_id}", [self.players[player_id]])
            )

    def init(self):
        self.world_size = self.app.get_active_world().size  # type: ignore
        for i in range(self.num_players):
            self.app.get_active_world().add_entity(
                Entity(f"Player {self.players[i].id}", [self.players[i]])
            )
            self.reset_player(i)

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
            observations[i] = (self.world_size - origin.x) / self.world_size
        else:
            observations[i] = (-origin.x) / self.world_size
        i += 1

        if origin.y > self.world_size / 2:
            observations[i] = (self.world_size - origin.y) / self.world_size
        else:
            observations[i] = (-origin.y) / self.world_size
        i += 1

        # Food and Player Observations
        observed_entity_indices = (
            self.app.get_active_world().grid.get_collisions_within_area(  # type: ignore
                origin, OPTIMAL_RESOLUTION_WIDTH
            )
        )
        foods: List[Food | None] = []
        players: List[ServerSnakeBodyComponent | None] = []

        for entity_index in observed_entity_indices:
            entity = self.app.get_active_world().entities[entity_index]
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
                key=lambda food: pr.vector_2distance_sqr(food.bodies[0], origin),  # type: ignore
            )[:CLOSEST_FOODS]
        else:
            foods += [None for _ in range(CLOSEST_FOODS - len(foods))]

        if len(players) > CLOSEST_PLAYERS:
            players = sorted(
                players,
                key=lambda player: pr.vector_2distance_sqr(player.bodies[0], origin),  # type: ignore
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
        if i != OBSERVATION_SIZE:
            raise Exception("Observation size is not 2319")
        return observations  # Full Total Floats 2319

    def get_actions(self, action: np.ndarray):
        return ACTION_LIST[action]

    def update(self, delta_time: float):
        for i, player in enumerate(self.players):
            if player.is_dead:
                self.reset_player(i, True)

            obs = self.get_observations(player)
            action, _ = self.model.predict(obs)
            w, a, s, d, boost = self.get_actions(action)
            player.set_controls(w, a, s, d, boost)
