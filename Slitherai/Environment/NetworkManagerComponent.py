from socket import AF_INET, SOCK_DGRAM, socket
from typing import Dict, Tuple

import numpy as np
import pyray as pr
from radyx import GridPhysics

from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH

from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.CollisionComponent import CollisionComponent
from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Entity import Entity
from Slitherai.Environment.Core.GridWorld import GridWorld
from Slitherai.Environment.Food import Food
from Slitherai.Environment.Replication import Replicator
from Slitherai.Environment.SnakeBodyComponent import (
    ClientSnakeBodyComponent,
    ServerSnakeBodyComponent,
)


class ServerNetworkManager(Component):
    def __init__(self, host: str, port: int, app: Application):
        self.host = host
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.setblocking(False)
        self.server_socket.settimeout(0.01)

        self.incrementing_id = 0

        self.clients: Dict[Tuple[str, int], ServerSnakeBodyComponent] = {}
        self.app = app
        self.replicator = Replicator()

    def accept_connections(self, address: Tuple[str, int]):
        # Handle Incoming Connections

        world: GridWorld = self.app.worlds[self.app.active_world]  # type: ignore

        location = pr.Vector2(
            np.random.randint(0, world.size), np.random.randint(0, world.size)
        )
        direction = pr.Vector2(np.random.choice([-1, 1]), np.random.choice([-1, 1]))

        component = ServerSnakeBodyComponent(location, direction, self.incrementing_id)
        player = Entity(f"Player{self.incrementing_id}", [component])

        self.clients[address] = component
        self.app.worlds[self.app.active_world].add_entity(player)

        self.server_socket.sendto(self.incrementing_id.to_bytes(4), address)
        self.incrementing_id += 1

    def handle_input(self, client: Tuple[str, int], data: bytes):
        # Handle input from the clients
        # Input is in form:
        # int
        # the bits of the int represent:
        # w a s d space
        # if -1, then the client has disconnected

        input_bits = int.from_bytes(data, signed=True)

        if input_bits == -1:
            self.handle_disconnections(client)
            return

        W = bool(input_bits & 0b0001)
        A = bool(input_bits & 0b0010)
        S = bool(input_bits & 0b0100)
        D = bool(input_bits & 0b1000)
        Space = bool(input_bits & 0b10000)

        self.clients[client].set_controls(W, S, A, D, Space)

    def replicate_world(self):
        # Replicate the server world to the clients
        # Protocol is replication.md
        grid: GridPhysics = self.app.worlds[self.app.active_world].grid  # type: ignore

        for client, component in self.clients.items():
            self.replicator.clear()
            entity_indices = grid.get_collisions_within_area(
                component.bodies[0], OPTIMAL_RESOLUTION_WIDTH
            )

            for entity_index in entity_indices:
                try:
                    entity = self.app.worlds[self.app.active_world].entities[
                        entity_index
                    ]
                except IndexError:
                    print("Information ", entity_index)
                    print("Entity Information")
                    for i, entity in enumerate(
                        self.app.worlds[self.app.active_world].entities
                    ):
                        print(f"{i} : {entity}")
                    ids = grid.get_collisions_within_area(
                        pr.Vector2(25000, 25000), 25000
                    )
                    print("Grid Probe")
                    for i in ids:
                        try:
                            print(
                                f"{i} : { self.app.worlds[self.app.active_world].entities [i]}"
                            )
                        except IndexError:
                            print(f"{i} : None")

                    raise IndexError

                component: ServerSnakeBodyComponent = entity.get_component(  # type: ignore
                    CollisionComponent.component_id
                )
                if component is None:
                    continue
                if component.collision_type == ServerSnakeBodyComponent.collision_type:
                    self.replicator.add_player(
                        component.id, component.radius, component.bodies
                    )
                elif component.collision_type == Food.collision_type:
                    self.replicator.add_food(
                        entity_index, component.radius, component.bodies[0]
                    )

            self.server_socket.sendto(self.replicator.encode(), client)

    def handle_disconnections(self, client_address: Tuple[str, int]):
        component = self.clients.pop(client_address)
        self.app.worlds[self.app.active_world].remove_entity(component.get_entity())

    def update(self, delta_time: float):
        for _ in range(100):
            try:
                data, address = self.server_socket.recvfrom(1024)
            except Exception:
                break
            if address not in self.clients and data == b"":
                self.accept_connections(address)
            else:
                self.handle_input(address, data)

        self.replicate_world()

    def destroy(self):
        for client in self.clients.keys():
            self.server_socket.sendto(b"\xff", client)
        self.server_socket.close()


class ClientNetworkManager(Component):
    def __init__(self, server_address: Tuple[str, int], app: Application):
        self.app = app
        self.server_address = server_address
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.settimeout(100)
        self.replicator = Replicator()

    def init(self):
        self.client_socket.sendto(b"", self.server_address)
        data, address = self.client_socket.recvfrom(1024)
        if address != self.server_address:
            raise Exception("Server address does not match")

        self.client_id = int.from_bytes(data)
        self.client_socket.setblocking(False)
        self.client_socket.settimeout(0.01)

    def handle_server_replication(self, data: bytes):
        if int.from_bytes(data[:1], signed=True) == -1:
            self.app.set_active_world(2)
            return

        self.replicator.clear()
        self.replicator.decode(data)
        self.app.worlds[self.app.active_world].entities.clear()
        self.app.worlds[self.app.active_world].entities.append(self.get_entity())
        found = False

        for player in self.replicator.players:
            if player.id == self.client_id:
                found = True
            entity = Entity(
                f"Player{player.id}",
                [
                    ClientSnakeBodyComponent(
                        self.client_id == player.id,
                        player.radius,
                        player.position,  # type: ignore
                    )
                ],
            )
            entity.can_update = False
            self.app.worlds[self.app.active_world].add_entity(entity)
            if self.client_id == player.id:
                self.app.camera.target = player.position[0]

        if not found:
            self.app.set_active_world(2)
            return

        for food in self.replicator.foods:
            entity = Entity(
                f"Food{food.id}",
                [Food(food.position, radius=food.radius)],  # type: ignore
            )
            self.app.worlds[self.app.active_world].add_entity(entity)

    def optimistic_replication(self, delta_time):
        for entity in self.app.worlds[self.app.active_world].entities:
            component: ClientSnakeBodyComponent = entity.get_component(  # type: ignore
                ClientSnakeBodyComponent.component_id
            )
            if component is None:
                continue
            component.update(delta_time)
            if component.is_player:
                self.app.camera.target = component.bodies[0]

    def handle_input(self):
        input = 0
        input |= pr.is_key_down(pr.KeyboardKey.KEY_W) << 0
        input |= pr.is_key_down(pr.KeyboardKey.KEY_A) << 1
        input |= pr.is_key_down(pr.KeyboardKey.KEY_S) << 2
        input |= pr.is_key_down(pr.KeyboardKey.KEY_D) << 3
        input |= pr.is_key_down(pr.KeyboardKey.KEY_SPACE) << 4

        self.client_socket.sendto(input.to_bytes(1, signed=True), self.server_address)

    def update(self, delta_time: float):
        try:
            data, _ = self.client_socket.recvfrom(1024)
            self.handle_server_replication(data)
        except Exception:
            self.optimistic_replication(delta_time)
        finally:
            self.handle_input()

    def destroy(self):
        self.client_socket.sendto(b"\xff", self.server_address)
        self.client_socket.close()

