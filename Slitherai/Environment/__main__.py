from Slitherai.Environment.SnakeBodyComponent import ServerSnakeBodyComponent
from Slitherai.Environment.Food import Food
from Slitherai.Environment.Core.CollisionComponent import CollisionComponent
import pyray as pr
import numpy as np
from radyx import GridPhysics

if __name__ == "__main__":
    size = 500
    blocks = 50
    grid = GridPhysics(size, blocks)
    grid.add_static_circle(0, pr.Vector2(0, 200), 10)
    grid.add_static_circle(1, pr.Vector2(100, 10), 10)
    grid.add_static_circle(2, pr.Vector2(0, 250), 10)

    collisions = grid.get_collisions_within_area(pr.Vector2(250, 250), 250)
    print(collisions)

