#!/usr/bin/env python3

import csv

import matplotlib.pyplot as plt

import lib.find_cred_project as find_cred_project


def main():
    cur_dir = find_cred_project.find_cred_project()

    integrate = cur_dir / "SMV/INTEGRATE.HKL"

    with integrate.open() as rf:
        data = csv.DictReader(
            (line for line in rf if not line.startswith("!")),
            fieldnames=(
                "H",
                "K",
                "L",
                "IOBS",
                "SIGMA",
                "XCAL",
                "YCAL",
                "ZCAL",
                "RLP",
                "PEAK",
                "CORR",
                "MAXC",
                "XOBS",
                "YOBS",
                "ZOBS",
                "ALF0",
                "BET0",
                "ALF1",
                "BET1",
                "PSI",
                "ISEG",
            ),
            delimiter=" ",
            skipinitialspace=True,
        )

        dataa = list(data)

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    # xs = [float(d["XCAL"]) for d in dataa]
    # ys = [float(d["YCAL"]) for d in dataa]
    # zs = [float(d["ZCAL"]) for d in dataa]
    # xs = [float(d["XOBS"]) for d in dataa]
    # ys = [float(d["YOBS"]) for d in dataa]
    # zs = [float(d["ZOBS"]) for d in dataa]
    xs = [float(d["H"]) for d in dataa]
    ys = [float(d["K"]) for d in dataa]
    zs = [float(d["L"]) for d in dataa]
    intensities = [float(d["IOBS"]) for d in dataa]
    im = ax.scatter(xs, ys, zs, c=intensities)
    fig.colorbar(im, ax=ax)
    plt.show()


if __name__ == "__main__":
    main()
