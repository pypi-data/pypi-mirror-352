#!/usr/bin/env python3
import csv
import re

import matplotlib.pyplot as plt
import numpy as np

import lib.find_cred_project as find_cred_project


def main():
    cur_dir = find_cred_project.find_cred_project()

    integrate = cur_dir / "SMV/SPOT.XDS"

    with integrate.open() as rf:
        data = csv.DictReader(
            (line for line in rf if not line.startswith("!")),
            fieldnames=(
                "x",
                "y",
                "z",
                "Intensity",
                "iseg",
                "h",
                "k",
                "l",
            ),
            delimiter=" ",
            skipinitialspace=True,
        )

        dataa = list(data)

    # Hardcoded for particle 3 ZSM-5_1
    osc_angle = np.radians(0.112660)
    rotation_axis = np.radians(50.30)
    origin_x = 271
    origin_y = 234

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    xs = [float(d["x"]) - origin_x for d in dataa]
    ys = [float(d["y"]) - origin_y for d in dataa]
    zs = [float(d["z"]) for d in dataa]

    angles = [z * osc_angle for z in zs]

    def yaw(angle: float):
        return np.array(
            [
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)],
            ]
        )

    def pitch(angle: float):
        return np.array(
            [
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)],
            ]
        )

    def roll(angle: float):
        return np.array(
            [
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1],
            ]
        )

    roll_mat = roll(rotation_axis)
    pitch_mat = pitch(rotation_axis)

    poss = np.array(
        [
            roll(0) @ pitch(angle) @ yaw(-rotation_axis) @ np.array([x, y, 0])
            for (x, y, angle) in zip(xs, ys, angles)
        ]
    )

    intensities = [float(d["Intensity"]) for d in dataa]
    im = ax.scatter(poss[:, 0], poss[:, 1], poss[:, 2], c=intensities)
    fig.colorbar(im, ax=ax)
    plt.show()


if __name__ == "__main__":
    main()
