#!/usr/bin/env python3
import csv

import matplotlib.pyplot as plt

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

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    xs = [float(d["x"]) for d in dataa]
    ys = [float(d["y"]) for d in dataa]
    zs = [float(d["z"]) for d in dataa]
    intensities = [float(d["Intensity"]) for d in dataa]
    for d in dataa:
        if abs(float(d["x"]) - 356) < 1 and abs(float(d["y"]) - 243) < 1:
            print(d)
    im = ax.scatter(xs, ys, zs, c=intensities)
    ax.set_xlabel("x (px)")
    ax.set_ylabel("y (px)")
    ax.set_zlabel("z (images)")
    plt.subplots_adjust(right=0.8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.15, shrink=0.80, label="Intensity")
    plt.show()
    fig.savefig(cur_dir / "spot.png", dpi=600, pad_inches=0, bbox_inches=None)


if __name__ == "__main__":
    main()
