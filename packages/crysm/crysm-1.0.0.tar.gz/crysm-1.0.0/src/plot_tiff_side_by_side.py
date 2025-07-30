#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from matplotlib.widgets import Slider

import lib.find_cred_project as find_cred_project


def main():
    cur_dir = find_cred_project.find_cred_project()

    highest_image_number = max([int(f.stem) for f in (cur_dir / "tiff").glob("*.tiff")])
    image_number = 69

    fig, (ax1, ax2) = plt.subplots(1, 2)
    plt.subplots_adjust(bottom=0.10)
    axslider = plt.axes([0.25, 0.1, 0.65, 0.03])
    image = tifffile.imread(cur_dir / f"tiff/{image_number:05d}.tiff")
    corr_image = tifffile.imread(cur_dir / f"tiff_corrected/{image_number:05d}.tiff")
    image_shape = image.shape

    i_num_slider = Slider(
        axslider, "Image", 0, highest_image_number, image_number, valstep=1.0
    )

    bgimg = ax1.imshow(image + 0.001, norm="log")
    corr_bgimg = ax2.imshow(corr_image + 0.001, norm="log")
    fig.colorbar(bgimg, ax=ax1)
    fig.colorbar(corr_bgimg, ax=ax2)

    def update(_val):
        image_number = int(i_num_slider.val)
        try:
            image = tifffile.imread(cur_dir / f"/tiff/{image_number:05d}.tiff")
            corr_image = tifffile.imread(
                cur_dir / f"tiff_corrected/{image_number:05d}.tiff"
            )
        except FileNotFoundError:
            image = np.zeros(image_shape)
            corr_image = image
        bgimg.set_data(image + 0.001)
        corr_bgimg.set_data(corr_image + 0.001)

        fig.canvas.draw()

    update(...)
    i_num_slider.on_changed(update)

    plt.show()


if __name__ == "__main__":
    main()
