#!/usr/bin/env python3
import re
import subprocess

import lib.find_cred_project as find_cred_project

# Assumption for now
composition = "Si1 O2"

xdsconv_template = """\
! UNIT_CELL_CONSTANTS= {constraints}
! SPACE_GROUP_NUMBER= {space_group}
! GENERATE_FRACTION_OF_TEST_REFLECTIONS=0.05
! INCLUDE_RESOLUTION_RANGE=50 2.0

INPUT_FILE=XDS_ASCII.HKL
OUTPUT_FILE={out_file} SHELX
FRIEDEL'S_LAW=FALSE ! store anomalous signal in output file even if weak
"""


def main():
    cur_dir = find_cred_project.find_cred_project()
    smv_dir = cur_dir / "SMV"
    shelx_dir = cur_dir / "shelx"
    xds_inp = (smv_dir / "INTEGRATE.LP").read_text()
    xds_inp = "\n".join([line.split("!")[0] for line in xds_inp.splitlines()])
    cell_consts: str = re.findall("UNIT_CELL_CONSTANTS=(.*)", xds_inp)[0]
    space_group: str = re.findall("SPACE_GROUP_NUMBER=(.*)", xds_inp)[0]

    out_file = "shelx.hkl"
    mrz_file = xdsconv_template.format(
        constraints=cell_consts, space_group=space_group, out_file=out_file
    )
    (smv_dir / "XDSCONV.INP").write_text(mrz_file)
    subprocess.call(["xdsconv"], cwd=smv_dir)

    shelx_dir.mkdir(exist_ok=True)
    shelx_file = shelx_dir / out_file
    shelx_file.write_text((smv_dir / out_file).read_text())

    subprocess.call(
        [
            "edtools.make_shelx",
            "-m",
            "Si48",
            "O96",
            "-s",
            "47",
            "-c",
            *(const for const in cell_consts.split() if const.strip() != ""),
        ],
        cwd=shelx_dir,
    )

    subprocess.call(["shelxt", shelx_file.stem], cwd=shelx_dir)


if __name__ == "__main__":
    main()
