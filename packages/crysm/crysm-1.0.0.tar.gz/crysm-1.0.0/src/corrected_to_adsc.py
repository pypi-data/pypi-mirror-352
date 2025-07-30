#!/usr/bin/env python3
import tifffile as tf

import lib.find_cred_project as find_cred_project
from lib.adscimage import read_adsc, write_adsc


def main():
    cur_dir = find_cred_project.find_cred_project()
    img_folder = cur_dir / "SMV/data_corrected"
    img_folder.mkdir(exist_ok=True)

    for old_img_path in (cur_dir / "SMV/data").glob("*.img"):
        img_name = old_img_path.with_suffix(".tiff").name
        tiff_path = cur_dir / "tiff_corrected" / img_name
        uncorrected, header = read_adsc(old_img_path.as_posix())
        img_path = img_folder / old_img_path.name
        if tiff_path.exists():
            img = tf.imread(tiff_path.as_posix())
        else:
            img = uncorrected

        print(img_path)
        write_adsc(img_path.as_posix(), img, header)


if __name__ == "__main__":
    main()
