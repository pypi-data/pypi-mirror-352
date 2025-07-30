from io import BytesIO
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from matplotlib.widgets import Slider

from lib.adscimage import read_adsc

cur_dir = Path(__file__).parent


image_number = 69

fig, (ax1, ax2) = plt.subplots(1, 2)
plt.subplots_adjust(bottom=0.10)
axslider = plt.axes([0.25, 0.1, 0.65, 0.03])
image, _ = read_adsc(f"./SMV/data/{image_number:05d}.img")
fake_file = "tmp.tiff"
with tifffile.TiffWriter(fake_file) as f:
    towrite = np.round(image, 0)
    f.write(data=towrite)
corr_image = cv2.imread(fake_file, cv2.IMREAD_GRAYSCALE)
# corr_image = tifffile.imread(fake_file)
# corr_image, _ = read_adsc(f"./SMV/data/{image_number:05d}.img")


bgimg = ax1.imshow(image + 0.001, norm="log")
corr_bgimg = ax2.imshow(corr_image + 0.001, norm="log")
fig.colorbar(bgimg, ax=ax1)
fig.colorbar(corr_bgimg, ax=ax2)

# i_num_slider = Slider(axslider, "Image", 0, 392, image_number, valstep=1.0)

# def update(val):
#     image_number = int(i_num_slider.val)
#     image, _ = read_adsc(f"./SMV/data/{image_number:05d}.img")
#     corr_image, _ = read_adsc(f"./SMV/data_corrected/{image_number:05d}.img")
#     bgimg.set_data(image + 0.001)
#     corr_bgimg.set_data(corr_image + 0.001)

#     fig.canvas.draw()


# update(...)
# i_num_slider.on_changed(update)


plt.show()
