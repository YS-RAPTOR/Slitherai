from socket import socket, AF_INET, SOCK_DGRAM
from Slitherai.Environment.Core.Application import Application
from Slitherai.Environment.Core.Component import Component
from Slitherai.Environment.Core.Entity import Entity
from typing import Tuple
import pyray as pr

# Access to Food Manager
# Access to World


class ServerNetworkManager(Component):
    def __init__(self, host: str, port: int, app: Application):
        self.host = host
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.setblocking(False)
        self.server_socket.settimeout(0.01)

        self.incrementing_id = 0

        self.clients = {}
        self.entities = {}
        self.app = app

    def accept_connections(self, address: Tuple[str, int]):
        # Handle Incoming Connections
        self.clients[address] = self.incrementing_id

        # TODO: Add player components
        player = Entity(f"Player{self.incrementing_id}", [])
        self.app.worlds[self.app.active_world].add_entity(player)
        self.entities[address] = player

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

        print(f"W: {W}, A: {A}, S: {S}, D: {D}, Space: {Space}")

        # TODO: Set player controls

    def replicate_world(self):
        # Replicate the server world to the clients
        # world will be in form:
        # players: [player]
        # player : playerid, mass, [body_parts]
        # food_created : [id, x, y, mass]
        # food_destroyed : [id]
        self.replicated_world = b"Hello"
        for player in self.entities.values():
            pass

        # Access Food Manager

        for client in self.clients.keys():
            self.server_socket.sendto(self.replicated_world, client)

    def handle_disconnections(self, client_address: Tuple[str, int]):
        self.clients.pop(client_address)
        entity = self.entities.pop(client_address)
        self.app.worlds[self.app.active_world].remove_entity(entity)

    def update(self, delta_time: float):
        for _ in range(100):
            try:
                data, address = self.server_socket.recvfrom(1024)
            except:
                break
            if address not in self.clients.keys():
                self.accept_connections(address)
            else:
                self.handle_input(address, data)

        self.replicate_world()


class ClientNetworkManager(Component):
    def __init__(self, server_address: Tuple[str, int], app: Application):
        self.app = app
        self.server_address = server_address
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.settimeout(100)

    def init(self):
        print("Client Network Manager Init")
        self.client_socket.sendto(b"", self.server_address)
        data, address = self.client_socket.recvfrom(1024)
        if address != self.server_address:
            raise Exception("Server address does not match")

        self.client_id = int.from_bytes(data)
        self.client_socket.setblocking(False)
        self.client_socket.settimeout(0.01)

    def handle_server_replication(self, data: bytes):
        print(data)
        pass

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
            data, address = self.client_socket.recvfrom(1024)
            if address != self.server_address:
                raise Exception("Server address does not match")
            self.handle_server_replication(data)
        except:
            print("No data")
        finally:
            self.handle_input()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.client_socket.sendto((-1).to_bytes(1, signed=True), self.server_address)

