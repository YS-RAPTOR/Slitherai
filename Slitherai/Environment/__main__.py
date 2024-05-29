import Slitherai.Environment.Constants as C
import pyray as pr
import numpy as np


def new_angle_calculator(input_angle, direction_angle) -> float:
    angle = input_angle - direction_angle
    if angle < 0:
        angle += np.pi * 2
    angle = angle if angle < np.pi else angle - np.pi * 2
    return angle


if __name__ == "__main__":
    directions = [
        pr.Vector2(1, 1),
        pr.Vector2(1, 0),
        pr.Vector2(1, -1),
        pr.Vector2(0, 1),
        pr.Vector2(0, -1),
        pr.Vector2(-1, 1),
        pr.Vector2(-1, 0),
        pr.Vector2(-1, -1),
    ]

    i = 0
    should_be_angles = [-135]

    for input_dir in directions:
        for direction in directions:
            delta_time = 1 / 60
            input_angle = np.arctan2(input_dir.y, input_dir.x) + np.pi / 2
            print(
                "Input Angle",
                np.rad2deg(input_angle),
                " for ",
                input_dir.x,
                ",",
                input_dir.y,
            )

            direction_angle = np.arctan2(direction.y, direction.x) + np.pi / 2
            print(
                "Direction Angle",
                np.rad2deg(direction_angle),
                " for ",
                direction.x,
                ",",
                direction.y,
            )

            angle = input_angle - direction_angle
            angle = angle if angle < np.pi else angle - np.pi * 2

            if (
                input_dir.y == -1
                and input_dir.x == 0
                or input_dir.y == -1
                and input_dir.x == -1
            ):
                if (
                    direction.y == 0
                    and direction.x == -1
                    or direction.y == 1
                    and direction.x == -1
                ):
                    print("Old Angle: ", np.rad2deg(angle))
                    print(
                        "New Angle: ",
                        np.rad2deg(new_angle_calculator(input_angle, direction_angle)),
                    )
                    print()
                    continue

            if abs(angle - new_angle_calculator(input_angle, direction_angle)) > 0.1:
                print("Old Angle: ", np.rad2deg(angle))
                print(
                    "New Angle: ",
                    np.rad2deg(new_angle_calculator(input_angle, direction_angle)),
                )

            print("Angle: ", np.rad2deg(angle))
            print()

