#!/usr/bin/env python3
import csv
import itertools as it
from typing import Generator, TypeVar

import matplotlib.pyplot as plt
import numpy as np
import tifffile as tf
from matplotlib.widgets import Slider

import lib.find_cred_project as find_cred_project



def peek[T](iterator: Generator[T, None, None]) -> tuple[T, Generator[T, None, None]]:
    first = next(iterator)
    iterator = it.chain((first,), iterator)
    return first, iterator


def main():
    cur_dir = find_cred_project.find_cred_project()
    view_corrected = False

    # cur_dir = Path("/home/iverks/progging/master/zenodo/mordenite_cRED_1")
    # view_corrected = False
    corrected = "_corrected" if view_corrected else ""

    integrate = cur_dir / "SMV/SPOT.XDS"

    with integrate.open() as rf:
        # Sometimes 'iseg' is here, sometimes not
        line_iter = (line for line in rf if not line.startswith("!"))
        first_line, line_iter = peek(line_iter)
        if len(first_line.strip().split(" ")) == 7:
            fieldnames = (
                "x",
                "y",
                "z",
                "Intensity",
                "h",
                "k",
                "l",
            )
        elif len(first_line.strip().split(" ")) == 4:
            fieldnames = ("x", "y", "z", "Intensity")
        else:
            fieldnames = (
                "x",
                "y",
                "z",
                "Intensity",
                "iseg",
                "h",
                "k",
                "l",
            )

        line_iter = it.chain((first_line,), line_iter)
        data = csv.DictReader(
            line_iter,
            fieldnames=fieldnames,
            delimiter=" ",
            skipinitialspace=True,
        )

        dataa = list(data)

    highest_image_number = max(
        [int(f.stem) for f in (cur_dir / f"tiff{corrected}").glob("*.tiff")]
    )
    image_number = 75
    delta = highest_image_number // 80
    try:
        is_indexed = [
            False if d["h"] + d["k"] + d["l"] == "000" else True for d in dataa
        ]
    except KeyError:
        is_indexed = [True for _ in dataa]
    # print(is_indexed)

    fig = plt.figure()
    ax = fig.add_subplot()
    plt.subplots_adjust(bottom=0.25)
    axfreq = plt.axes([0.25, 0.15, 0.65, 0.03])
    axamplitude = plt.axes([0.25, 0.1, 0.65, 0.03])
    image_file = cur_dir / f"tiff{corrected}/{image_number:05d}.tiff"
    image = tf.imread(image_file.as_posix())
    image_shape = image.shape

    i_num_slider = Slider(
        axfreq, "Image", 0, highest_image_number, valinit=image_number, valstep=1.0
    )
    delta_slider = Slider(
        axamplitude, "delta", 0, highest_image_number / 2, valinit=delta, valstep=1.0
    )

    bgimg = ax.imshow(image + 0.001, norm="log")
    (indexed,) = ax.plot(
        [], [], marker="o", ls="", markerfacecolor="none", color="black"
    )
    (unindexed,) = ax.plot(
        [], [], marker="x", ls="", markerfacecolor="none", color="red"
    )

    prev_image = image_number

    def update(val):
        nonlocal prev_image
        image_number = int(i_num_slider.val)
        delta = delta_slider.val
        if image_number != prev_image:
            prev_image = image_number
            try:
                image = tf.imread(
                    str(cur_dir / f"tiff{corrected}/{image_number:05d}.tiff")
                )
            except FileNotFoundError:
                image = np.zeros(image_shape)
            bgimg.set_data(image + 0.001)

        xs = [float(d["x"]) - 1 for d in dataa]
        ys = [float(d["y"]) - 1 for d in dataa]
        zs = [float(d["z"]) - 1 for d in dataa]

        xdata = [
            x
            for x, z, is_idx in zip(xs, zs, is_indexed)
            if abs(z - image_number) <= delta and is_idx
        ]
        ydata = [
            y
            for y, z, is_idx in zip(ys, zs, is_indexed)
            if abs(z - image_number) <= delta and is_idx
        ]
        indexed.set_data(xdata, ydata)
        xdata = [
            x
            for x, z, is_idx in zip(xs, zs, is_indexed)
            if abs(z - image_number) <= delta and not is_idx
        ]
        ydata = [
            y
            for y, z, is_idx in zip(ys, zs, is_indexed)
            if abs(z - image_number) <= delta and not is_idx
        ]
        unindexed.set_data(xdata, ydata)

        fig.canvas.draw()

    update(None)
    i_num_slider.on_changed(update)
    delta_slider.on_changed(update)

    plt.show()
    fig.savefig(
        cur_dir
        / f"img_w_spots_{int(i_num_slider.val)}_delta_{int(delta_slider.val)}.png",
        dpi=600,
        pad_inches=0,
        bbox_inches=None,
    )


if __name__ == "__main__":
    main()
