#!/usr/bin/env python3
import textwrap
from dataclasses import dataclass
from pathlib import Path

from lib.find_cred_project import find_cred_project


@dataclass
class CRED_log:
    start_angle: float
    end_angle: float


def parse_cred_log(cred_log_file: Path) -> CRED_log:
    with open(cred_log_file, "r") as cf:
        for line in cf:
            match line.split("#")[0].split(": "):
                case ["Starting angle", rest]:
                    start_angle = float(rest.removesuffix(" degrees\n"))
                case ["Ending angle", rest]:
                    end_angle = float(rest.removesuffix(" degrees\n"))
                # TODO maybe: rest of the data, but I'm not sure what we need
    return CRED_log(start_angle=start_angle, end_angle=end_angle)


@dataclass
class PETSImage:
    image: str
    alpha_angle: float
    beta_angle: float | None


@dataclass
class PETS:
    lambda_val: float
    a_per_pixel: float
    phi: float
    omega: float
    bin: int
    reflection_size: int
    noise_parameters: list[int]
    imagelist: list[PETSImage]


def parse_pets(pets_file: Path) -> PETS:
    with open(pets_file, "r") as pf:
        try:
            while line := next(pf):
                match line.split("#")[0].strip().split(" "):
                    case ["lambda", rest]:
                        lambda_val = float(rest)
                    case ["Aperpixel", rest]:
                        a_per_pixel = float(rest)
                    case ["phi", rest]:
                        phi = float(rest)
                    case ["omega", rest]:
                        omega = float(rest)
                    case ["bin", rest]:
                        bin = int(rest)
                    case ["reflectionsize", rest]:
                        reflection_size = int(rest)
                    case ["noiseparameters", *rest]:
                        noise_parameters = [int(r) for r in rest]
                    case ["imagelist"]:
                        imagelist: list[PETSImage] = []
                        while line := next(pf):
                            line = line.split("#")[0].strip()
                            if line == "endimagelist":
                                break
                            l = line.split()
                            img = PETSImage(l[0], float(l[1]), float(l[2]))
                            imagelist.append(img)
        except StopIteration:
            pass

    return PETS(
        lambda_val=lambda_val,
        a_per_pixel=a_per_pixel,
        phi=phi,
        omega=omega,
        bin=bin,
        reflection_size=reflection_size,
        noise_parameters=noise_parameters,
        imagelist=imagelist,
    )


@dataclass
class REDpFile:
    filename: str
    stage_angle: float
    beam_angle: float
    total_angle: float


@dataclass
class REDp:
    wavelength: float
    rotation_axis: float
    ccd_pixel_size: float
    stretching_amp: float
    stretching_azimuth: int
    filelist: list[REDpFile]


def petsimg_to_redpimg(img: PETSImage) -> REDpFile:
    return REDpFile(
        filename=img.image,
        stage_angle=img.alpha_angle,
        beam_angle=img.beta_angle,
        total_angle=img.alpha_angle,
    )


def pets_to_redp(pets: PETS) -> REDp:
    return REDp(
        wavelength=pets.lambda_val,
        rotation_axis=pets.omega,
        ccd_pixel_size=pets.a_per_pixel,
        stretching_amp=1,  # ??????
        stretching_azimuth=180,  # ??????
        filelist=[petsimg_to_redpimg(img) for img in pets.imagelist],
    )


def serialize_redp(redp: REDp) -> str:
    redp_str = textwrap.dedent(
        f"""
    WAVELENGTH\t{redp.wavelength}
    ROTATIONAXIS\t{redp.rotation_axis}
    CCDPIXELSIZE\t{redp.ccd_pixel_size}
    STRETCHINGAMP\t{redp.stretching_amp}
    STRETCHINGAZIMUTH\t{redp.stretching_azimuth}

    FILELIST
    """
    ).lstrip()
    for file in redp.filelist:
        redp_str += f"FILE {file.filename} {file.stage_angle}\t{file.beam_angle}\t {file.total_angle}\n"
    redp_str += "ENDFILELIST"
    return redp_str


def main():
    zpath = find_cred_project()

    print("Parsing ", zpath / "cRED_log.txt")
    cred_log = parse_cred_log(zpath / "cRED_log.txt")
    print("Parsing ", zpath / "tiff/pets.pts")
    pets = parse_pets(zpath / "tiff/pets.pts")
    redp = pets_to_redp(pets)
    with open(zpath / "tiff/redp.ed3d", "w") as wf:
        print("Writing to", wf.name)
        wf.write(serialize_redp(redp))


if __name__ == "__main__":
    main()
