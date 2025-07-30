import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

from rich import print

from lib.find_cred_project import find_cred_project


def parse_composition(composition: str) -> list[tuple[str, int]]:
    """
    Parses an input composition to

    >>> parse_composition("SiO") == [("Si", 1), ("O", 1)]
    True
    >>> parse_composition("SiO2") == [("Si", 1), ("O", 2)]
    True
    >>> parse_composition("SiO") == [("Si", 1), ("O", 1)]
    True
    >>> parse_composition("OF") == [("O", 1), ("F", 1)]
    True
    >>> parse_composition("O2F") == [("O", 2), ("F", 1)]
    True
    >>> parse_composition("OF2") == [("O", 1), ("F", 2)]
    True
    >>> parse_composition("Si O") == [("Si", 1), ("O", 1)]
    True
    >>> parse_composition("Si") == [("Si", 1)]
    True
    """

    materials = composition.split()

    if len(materials) == 1:  # Maybe camelcased
        materials = re.findall("[A-Z][^A-Z]*", composition)

    output: list[tuple[str, int]] = []
    for material in materials:
        element = "".join([c for c in material if not c.isdigit()])
        count_str = "".join([c for c in material if c.isdigit()])
        count = int(count_str) if count_str else 1

        if element == "":  # Assume user supplied Si 2 O 4
            if not len(output) > 0:
                raise ValueError(
                    "Composition parsing failed due to first element being a number"
                )
            if not output[-1][1] == 1:
                raise ValueError(
                    "Composition parsing failed due to receiving two numbers in a row"
                )
            output[-1] = (output[-1][0], count)
            continue
        output.append((element, count))

    return output


def laue_number(pets_num: int) -> int:
    """
    Translates from PETS' numbering convention to SHELX. Some numbers are missing
    """
    pets_numbers = {
        0: "Auto",
        1: "-1",
        2: "2/m",
        3: "112/m",
        4: "2/m11",
        5: "mmm",
        6: "4/m",
        7: "4/mmm",
        8: "-3",
        9: "-31m",
        10: "-3m1",
        11: "6/m",
        12: "6/mmm",
        13: "m-3",
        14: "m-3m",
    }

    shelx_numbers = {
        "Auto": 0,
        "-1": 1,
        "2/m": 2,
        "112/m": 2,  # UNSURE
        "2/m11": 2,  # UNSURE
        "mmm": 3,
        "4/m": 4,
        "4/mmm": 5,
        "-3": 6,  # or 7 UNSURE
        "-31m": 9,
        "-3m1": 10,
        "6/m": 11,
        "6/mmm": 12,
        "m-3": 13,
        "m-3m": 14,
    }
    string_version = pets_numbers[pets_num]
    if pets_num in [3, 4]:
        print(f"[Yellow]Warning, changing Laue group {string_version} to 2/m")
    if pets_num == 8:
        print("[Yellow]Warning, assuming rhombohedral primitive for Laue group -3")
    return shelx_numbers[string_version]


def run_shelx(pts_file: Path, composition: str, shelxt_args: list[str]):
    cur_dir = find_cred_project(pts_file.parent)
    pets_contents = pts_file.read_text(errors="ignore")
    integration_mode = re.findall("integrationmode .*\n", pets_contents)
    if integration_mode is None:
        raise RuntimeError("Couldn't find integrationmode line in .pts2 file")
    laue_class = int(integration_mode[0].split()[3])
    laue_class = laue_number(laue_class)  # Translate from PETS to SHELX
    if laue_class == 0:
        print("[Yellow]Warning: Laue class set to auto")
    elif laue_class == 1:
        print("[Yellow]Warning: Laue class set to -1")

    elements = parse_composition(composition)
    print("Found composition", "".join(f"{el}{cnt}" for el, cnt in elements))
    shelx_folder = cur_dir / "shelx"
    os.makedirs(shelx_folder, exist_ok=True)
    hkl_file = pts_file.with_name(pts_file.stem + "_shelx.hkl")
    ins_file = pts_file.with_name(pts_file.stem + "_shelx.ins")
    sfac = "SFAC " + " ".join([el[0] for el in elements]) + "\n"
    unit = "UNIT " + " ".join([str(el[1]) for el in elements]) + "\n"
    assert hkl_file.exists()
    assert ins_file.exists()
    ins_string = ins_file.read_text()
    ins_string = re.sub("SFAC.*\n", sfac, ins_string)
    ins_string = re.sub("UNIT.*\n", unit, ins_string)
    shutil.copyfile(hkl_file, shelx_folder / hkl_file.name)
    (shelx_folder / ins_file.name).write_text(ins_string)
    command = shlex.split(f"shelxt {ins_file.stem} -l{laue_class} -a0.6") + shelxt_args
    print(f"Running SHELX: {shlex.join(command)}")
    subprocess.call(
        command,
        cwd=shelx_folder,
    )



if __name__ == "__main__":
    import doctest

    doctest.testmod()
