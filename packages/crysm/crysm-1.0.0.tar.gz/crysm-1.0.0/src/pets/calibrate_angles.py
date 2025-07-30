"""
This script finds the calibrated angles for each image by looking at the timestamps in their metadata.
We assume:
1. The start angle was recorded immediately before the end timestamp of the first image.
2. The end angle was recorded immediately after the start timestamp of the last image.
3. The time between acquisition and end timestamp is constant for any given dataset.
"""
import re
from dataclasses import dataclass
from pathlib import Path

import tifffile as tf
import yaml

from lib.find_cred_project import find_cred_project


def get_timings(image: Path):
    with tf.TiffFile(image) as img:
        page: tf.TiffPage = img.pages[0]
        header: str = page.tags["ImageDescription"].value
        lines = [
            line
            for line in header.splitlines()
            if line.startswith("ImageGetTimeStart")
            or line.startswith("ImageGetTimeEnd")
        ]
        metadata = yaml.load("\n".join(lines), Loader=yaml.Loader)
        start = float(metadata["ImageGetTimeStart"])
        end = float(metadata["ImageGetTimeEnd"])
    return start, end


@dataclass
class DatasetStat:
    start: float
    end: float
    end_times: list[float]
    names: list[int]


def get_stats_for_folder(dataset: Path):
    names = []
    start_times = []
    end_times = []
    for img in dataset.glob("*.tiff"):
        start, end = get_timings(img)
        names.append(int(img.stem))
        start_times.append(start)
        end_times.append(end)

    zipped = list(zip(names, start_times, end_times))
    zipped.sort()
    names, start_times, end_times = zip(*zipped)

    return DatasetStat(start_times[0], end_times[-1], end_times, names)


def calibrate_angles(percentage: float = 100, skip_after_defocus: bool = False, plot_timesteps: bool = False):
    cur_dir = find_cred_project()
    cred_log = (cur_dir / "cRED_log.txt").read_text(errors="ignore")
    start_angle = float(cred_log.split("Starting angle: ")[1].split(" degrees")[0])
    end_angle = float(cred_log.split("Ending angle: ")[1].split(" degrees")[0])
    print(f"Parsed angles as {start_angle} to {end_angle}")

    total_angle = end_angle - start_angle
    if percentage != 100:
        old_total_angle = total_angle
        total_angle *= percentage / 100
        print(f"Reduced angle span from {old_total_angle:.1f} to {total_angle:.1f} degrees")


    pets = (cur_dir / "pets.pts").read_text(errors="ignore")
    rest = pets.split("imagelist")[0]

    stats = get_stats_for_folder(cur_dir / "tiff")
    total_time = stats.end - stats.start

    timesteps = [b - a for a,b in zip(stats.end_times[:-1], stats.end_times[1:])]
    semiangles = [timestep / total_time * total_angle / 2 for timestep in timesteps]
    
    if plot_timesteps:
        import matplotlib.pyplot as plt
        import numpy as np
        _, (ax1, ax2) = plt.subplots(1,2)
        anglz = np.array(timesteps)
        ax1.plot(anglz)
        ax1.set_title("Timesteps")
        anglz = anglz[anglz < np.median(timesteps)*3]
        ax2.hist(list(anglz), bins=len(anglz))
        ax2.set_title("Timestep histogram")
        plt.show()
        plt.close()

    semiangles.sort()
    median_semiangle = abs(semiangles[len(semiangles)//2])
    anynumber_regex = r"\d+\.?\d*"
    rest = re.sub(f"phi {anynumber_regex}\n", f"phi {median_semiangle:.4f}\n", rest)

    if percentage == 100:
        perc = "pets"
    else:
        perc = f"{percentage}"
    prev_name = 0
    filename = f"{perc}-fromtime.pts"
    if skip_after_defocus:
        filename = f"{perc}-skipframe.pts"
    with open(cur_dir / filename, "w") as petsout:
        petsout.write(rest)
        petsout.write("imagelist\n")

        for name, time in zip(stats.names, stats.end_times):
            if skip_after_defocus and name - 1 > prev_name:
                prev_name = name
                continue
            prev_name = name
            timefraction = (time - stats.start) / total_time
            angle = start_angle + total_angle * timefraction
            petsout.write(f"tiff/{name:05d}.tiff   {angle:.4f} {0.0:.2f}\n")

        petsout.write("endimagelist\n\n")
    print(f"Wrote image list to {filename}. Semiangle was set to {median_semiangle}")
