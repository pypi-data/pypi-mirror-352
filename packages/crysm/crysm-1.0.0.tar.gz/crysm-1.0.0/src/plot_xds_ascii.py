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
    im = ax.scatter(xs, ys, zs, c=intensities)
    fig.colorbar(im, ax=ax)
    plt.show()


if __name__ == "__main__":
    main()
