from functools import cache
from pathlib import Path

import matplotlib.pyplot as plt
import tifffile as tf
from matplotlib.axes import Axes
from matplotlib.backend_bases import KeyEvent, MouseButton, MouseEvent
from matplotlib.patches import Rectangle


def parse_dead_pixels(dead_pixels: Path) -> list[tuple[int, int]]:
    try:
        out = []
        for line in dead_pixels.read_text().strip().splitlines():
            a, b = [int(part) for part in line.strip().split()]
            out.append((a, b))
        return out
    except FileNotFoundError:
        return []


@cache
def load_image(image: Path):
    return tf.imread(image)


def mark_dead_pixels(image: Path, dead_pixels_path: Path | None = None):
    dead_pixels = (
        parse_dead_pixels(dead_pixels_path) if dead_pixels_path is not None else []
    )
    # List cosplaying as a pointer
    cur_image = [image]
    other_images = sorted(list(image.parent.iterdir()))
    fig, _ax = plt.subplots()
    ax: Axes = _ax
    bg = ax.imshow(load_image(image), norm="symlog")
    rects: dict[tuple[int, int], Rectangle] = {}

    title = "Double click to toggle dead pixels\n Use 'a' and 'd' to check other images\n Image {image}"
    for px, py in dead_pixels:
        # subtract 1 to correct for 1-indexing, and 0.5 because we draw from the center
        rect = Rectangle(
            xy=(px - 1.5, py - 1.5),
            width=1,
            height=1,
            edgecolor="r",
            facecolor="none",
            alpha=1,
        )
        rects[px, py] = ax.add_patch(rect)

    def on_keydown(event: KeyEvent):
        if event.key == "d" or event.key == "a":
            image_idx = other_images.index(cur_image[0])
            if event.key == "d":
                next_idx = (image_idx + 1) % len(other_images)
            else:
                next_idx = (image_idx - 1) % len(other_images)
            cur_image[0] = other_images[next_idx]
            bg.set_data(load_image(cur_image[0]))
            plt.title(title.format(image=cur_image[0]))
            plt.draw()

    def on_click(event: MouseEvent):
        if event.button is MouseButton.LEFT and event.dblclick:
            px = int(round(event.xdata)) + 1
            py = int(round(event.ydata)) + 1
            if (px, py) not in rects:
                rect = Rectangle(
                    xy=(px - 1.5, py - 1.5),
                    width=1,
                    height=1,
                    edgecolor="r",
                    facecolor="none",
                    alpha=1,
                )
                rects[(px, py)] = ax.add_patch(rect)
            else:
                rect = rects.pop((px, py))
                rect.remove()
            plt.draw()

    plt.connect("key_press_event", on_keydown)
    plt.connect("button_press_event", on_click)
    plt.title(title.format(image=cur_image[0]))
    plt.show()

    dead_pixels = list(rects.keys())

    if dead_pixels_path is None:
        dead_pixels_path = Path("__deadpixels.txt")
    with dead_pixels_path.open("w") as dp:
        for px, py in dead_pixels:
            dp.write(f"{px} {py}\n")
    print(f"Wrote {len(dead_pixels)} dead pixels to {dead_pixels_path}")
