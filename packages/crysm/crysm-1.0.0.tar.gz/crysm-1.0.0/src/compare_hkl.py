import math
from pathlib import Path
from typing import NamedTuple

import matplotlib.pyplot as plt

from lib.find_cred_project import find_cred_project


class HKLLine(NamedTuple):
    h: int
    k: int
    l: int  # noqa: E741
    intensity: float


def hkl_equal(a: HKLLine, b: HKLLine):
    return a.h == b.h and a.k == b.k and a.l == b.l


def magnitude(p: HKLLine, x: HKLLine) -> float:
    return math.sqrt(p.intensity**2 + x.intensity**2)


def find_pets_hkl(cur_dir: Path):
    new_placement = cur_dir / "pets.hkl"
    old_placement = cur_dir / "tiff/pets.hkl"
    if new_placement.is_file():
        return new_placement
    if old_placement.is_file():
        return old_placement
    raise Exception("Pets hkl not found")


def parse_pets_hkl(pets_file: Path) -> list[HKLLine]:
    output = []
    with pets_file.open("r") as data:
        reader = (row.strip().split() for row in data)
        for row in reader:
            h = int(row[0])
            k = int(row[1])
            l = int(row[2])  # noqa: E741
            intensity = float(row[3])

            output.append(HKLLine(h, k, l, intensity))
    return output


def parse_xds_integrate(integrate_file: Path) -> list[HKLLine]:
    output = []
    with integrate_file.open("r") as data:
        reader = (row.strip().split() for row in data if not row.strip()[0] == "!")
        for row in reader:
            h = int(row[0])
            k = int(row[1])
            l = int(row[2])  # noqa: E741
            intensity = float(row[3])

            output.append(HKLLine(h, k, l, intensity))
    return output


def plot_diffs(diffs: list[float], different_sign: list[bool], magnitudes: list[float]):
    plt.stairs(
        [diff if not ds else 0 for (diff, ds) in zip(diffs, different_sign)],
        fill=True,
    )
    plt.stairs(
        [diff if ds else 0 for (diff, ds) in zip(diffs, different_sign)],
        fill=True,
        color="orange",
    )
    plt.yscale("symlog")
    plt.xlabel("Common indices, sorted by xds intensity magnitude")
    plt.ylabel(r"PETS overestimation $\frac{|I_{PETS}| - |I_{XDS}|}{|I_{XDS}|}$")
    plt.xticks(
        ticks=range(len(magnitudes))[::500],
        labels=[f"{mag:.2f}" for mag in magnitudes[::500]],
    )
    plt.show()
    plt.close()


def plot_hkl_file(filename: str | Path | None):
    if type(filename) is Path:
        toparse = filename
    else:
        cur_dir = find_cred_project()
        if filename is None:
            filename = "pets.hkl"
        toparse = cur_dir / filename

    hkldata = parse_pets_hkl(toparse)
    hkldata.sort(key=lambda line: line.intensity)

    intensities = [line.intensity for line in hkldata]
    plt.plot(intensities)
    plt.yscale("symlog")
    plt.show()


def main(save=True):
    cur_dir = find_cred_project()

    pets_file = find_pets_hkl(cur_dir)
    xds_file = cur_dir / "SMV/INTEGRATE.HKL"
    pets_hkl = parse_pets_hkl(pets_file)
    xds_hkl = parse_xds_integrate(xds_file)

    common_xds_hkl: list[HKLLine] = []
    common_pets_hkl: list[HKLLine] = []
    counter = 0
    for hkl in pets_hkl:
        xds_r = [x for x in xds_hkl if hkl_equal(x, hkl)]
        if len(xds_r):
            counter += 1
            common_pets_hkl.append(hkl)
            common_xds_hkl.append(xds_r[0])

    print(
        counter, "of", len(pets_hkl), "of the indices in pets hkl are also in xds hkl"
    )
    print(counter, "of", len(xds_hkl), "of the indices in xds hkl are also in pets hkl")

    zipped = list(zip(common_pets_hkl, common_xds_hkl))

    # zipped.sort(key=lambda z: magnitude(*z))
    zipped.sort(key=lambda z: abs(z[1].intensity))

    diffs: list[float] = []
    different_sign: list[bool] = []
    for p, x in zipped:
        # diffs.append((abs(p.intensity) - abs(x.intensity)) / magnitude(p, x))
        # diffs.append((abs(p.intensity) - abs(x.intensity)) / abs(x.intensity))
        diffs.append((abs(p.intensity) - abs(x.intensity)))
        # diffs.append(abs(p.intensity) / abs(x.intensity))
        different_sign.append(
            math.copysign(1, p.intensity) != math.copysign(1, x.intensity)
        )

    # Sort the two lists by the difference
    zipped2 = list(zip(diffs, different_sign))
    zipped2.sort(key=lambda z: z[0])
    diffs = [z[0] for z in zipped2]
    different_sign = [z[1] for z in zipped2]

    if False:
        plt.stairs(
            [diff if not ds else 0 for (diff, ds) in zip(diffs, different_sign)],
            fill=True,
        )
        plt.stairs(
            [diff if ds else 0 for (diff, ds) in zip(diffs, different_sign)],
            fill=True,
            color="orange",
        )
        plt.yscale("symlog")
        plt.xlabel("Index. Orange means sign is different")
        plt.ylabel(r"PETS overestimation $|I_{PETS}| - |I_{XDS}|$")
        if save:
            plt.tight_layout()
            plt.savefig("pets_overestimation.png", bbox_inches="tight", dpi=300)
        plt.show()
        plt.close()

    pets_hkl.sort(key=lambda x: x.intensity)
    xds_hkl.sort(key=lambda x: x.intensity)
    if True:
        plt.plot([x.intensity for x in pets_hkl], label="PETS")
        plt.plot([x.intensity for x in xds_hkl], label="XDS")
        plt.yscale("symlog")
        plt.xlabel("Peaks")
        plt.ylabel("Intensity (log)")
        plt.legend()
        if save:
            plt.tight_layout()
            plt.savefig("intensity_distribution.png", bbox_inches="tight", dpi=300)
        plt.show()
        plt.close()

    if True:
        common_xds_hkl_i = [x.intensity for x in common_xds_hkl]
        common_pets_hkl_i = [x.intensity for x in common_pets_hkl]
        plt.grid()
        plt.scatter(common_xds_hkl_i, common_pets_hkl_i, s=3, label="Common peaks")
        plt.axline((0, 0), (1, 1), label="Expected distribution")
        plt.xlabel("Intensity from XDS")
        plt.ylabel("Intensity from PETS")
        plt.xscale("symlog")
        plt.yscale("symlog")
        plt.gca().set_aspect("equal")
        plt.legend()
        if save:
            plt.tight_layout()
            plt.savefig("common_peaks_intensities.png", bbox_inches="tight", dpi=300)
        plt.show()
        plt.close()


if __name__ == "__main__":
    main()
