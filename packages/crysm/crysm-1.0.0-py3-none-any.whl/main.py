import enum
from pathlib import Path
from typing import Annotated

import rich
import typer
from typer import Typer

app = Typer(
    name="crysm",
    no_args_is_help=True,
    help="Collection of scripts for CRED. PETS specific commands are prefixed by `pets-`, XDS specific commands by `xds-`",
)


@app.command()
def pets_calibrate_angles(
    range: Annotated[
        float,
        typer.Option(help="Estimaged percentage of total angle range really spanned"),
    ] = 100,
    skip: Annotated[bool, typer.Option(help="Skip first frame after defocus")] = False,
    plot: Annotated[bool, typer.Option(help="Plot timestep histogram")] = False,
):
    """Calibrate the angle of each image based on the timestamps in their metadata.
    Generates

    Example usage: `crysm pets-calibrate-angles`
    """
    import pets
    import pets.calibrate_angles

    pets.calibrate_angles.calibrate_angles(
        percentage=range, skip_after_defocus=skip, plot_timesteps=plot
    )


@app.command()
def find_center_cross_correction(
    flatfield_images: Annotated[
        list[Path], typer.Argument(..., help="Flatfield images to use for calibration")
    ],
):
    """Find central cross intensity correction factor from a flatfield image.
    Supported formats are .tiff or .mib

    Example usage: `crysm finc-center-cross-correction flatfield.mib`
    """
    import lib
    import lib.central_cross_correction_factor

    factors: list[float] = []
    central_factors: list[float] = []
    extra_pixels: list[int] = []

    for flatfield in flatfield_images:
        stats = lib.central_cross_correction_factor.find_center_cross_correction(
            flatfield
        )
        print(f"For image: {flatfield}:")
        print(f"  Mean value of cross: {stats.cross_mean:.2f}")
        print(f"  Mean value of central four pixels: {stats.central_mean:.2f}")
        print(f"  Mean value of rest of image: {stats.rest_mean:.2f}")
        if len(flatfield_images) > 1:
            print(f"  Additional pixels: {stats.num_extra_pixels}")
            print(f"  Correction factor: {stats.factor:.3f}")
            print(f"  Central four factor: {stats.central_factor:.3f}")
        factors.append(stats.factor)
        central_factors.append(stats.central_factor)
        extra_pixels.append(stats.num_extra_pixels)

    factor = sum(factors) / len(factors)
    central_factor = sum(central_factors) / len(central_factors)
    num_extra_pixels = max(extra_pixels)

    print("Suggested arguments for correction:")
    print(
        f" --additional-pixels {num_extra_pixels}"
        f" --correction-factor {factor:.3f}"
        f" --central-four-factor {central_factor:.3f}"
    )
    print("Number of additional pixels should be verified with detector manufacturer")


@app.command()
def pets_correct_center_cross(
    additional_pixels: Annotated[
        int,
        typer.Option(
            ...,
            "--additional-pixels",
            "-a",
            help="How many pixels should be added to the"
            "center to correct the geometry of the images.",
        ),
    ],
    correction_factor: Annotated[
        float,
        typer.Option(
            ...,
            "--correction-factor",
            "-c",
            help="How much more intense a center cross pixel is than a regular pixel",
        ),
    ],
    central_four_factor: Annotated[
        float,
        typer.Option(
            ...,
            "--central-four-factor",
            "-C",
            help="How much more intense the four central pixels are than a regular pixel",
        ),
    ],
):
    """
    Correct central cross of a dataset given the intensity
    correction factor and the number of pixels in the gap.

    Example usage: `crysm pets-correct-center-cross --additional-pixels 2
    --correction-factor 2.196 --central-four-factor 4.051`
    """
    from lib import find_cred_project
    from pets import center_cross_correction

    cur_dir = find_cred_project.find_cred_project()
    center_cross_correction.correct_center_cross(
        cur_dir,
        additional_pixels=additional_pixels,
        correction_factor=correction_factor,
        central_four_factor=central_four_factor,
    )


@app.command()
def pets_correct_center_cross_calibration(
    input: Annotated[Path, typer.Argument(help="Input image")],
    output: Annotated[Path, typer.Argument(help="Output image")],
    additional_pixels: Annotated[
        int,
        typer.Option(
            help="How many pixels should be added to the"
            "center to correct the geometry of the images."
        ),
    ],
    correction_factor: Annotated[
        float | None,
        typer.Option(
            help="How much more intense a center cross pixel is than a regular pixel"
        ),
    ] = None,
    central_four_factor: Annotated[
        float | None,
        typer.Option(
            help="How much more intense the four central pixels are than a regular pixel"
        ),
    ] = None,
):
    """Correct the center cross of a single image, used for correcting calibration images.

    Example usage: `crysm pets-correct-center-cross-calibration --additional-pixels 2
    flatfield.mib flatfield_2px_corrected.tiff`
    """
    from pets import center_cross_correction

    if correction_factor is None:
        correction_factor = 10000
        rich.print(
            f"[bold yellow]Warning: --correction-factor not set, defaulting to {correction_factor}"
        )

    if central_four_factor is None:
        central_four_factor = correction_factor * 2
        rich.print(
            f"[bold yellow]Warning: --central-four-factor not set, defaulting to {central_four_factor}"
        )

    center_cross_correction.correct_center_cross_image(
        input,
        output,
        correction_factor=correction_factor,
        central_four_factor=central_four_factor,
        additional_pixels=additional_pixels,
    )
    print(f"Wrote corrected image to {output}")


@app.command()
def pets_mark_dead_pixels(
    image: Annotated[
        Path, typer.Argument(help="Image to look at to find the dead pixels")
    ],
    dead_pixels: Annotated[
        Path | None,
        typer.Option(
            ...,
            "--dead-pixels",
            "-d",
            help="PETS generated file of initial dead pixels",
        ),
    ] = None,
):
    """
    Open an interactive matplotlib window to mark pixels as dead.
    Double click to mark a pixel as dead.
    Use "a" and "d" as arrow keys to rotate through the dataset.

    Example usage: `crysm pets-mark-dead-pixels
    --correction-factor 2.196 --central-four-factor 4.051`
    """
    from pets import mark_dead_pixels

    mark_dead_pixels.mark_dead_pixels(image, dead_pixels)


class BeamstopType(str, enum.Enum):
    cross = "cross"
    square = "square"


@app.command()
def pets_create_beamstop(
    output: Annotated[Path, typer.Argument(help="File to store beamstop in")],
    image_width: Annotated[
        int,
        typer.Option(
            ...,
            "--image-width",
            "-w",
            help="Width of image in pixels, after eventual widening of the cross",
        ),
    ],
    beamstop_width: Annotated[
        int,
        typer.Option(..., "--beamstop-width", "-b", help="Width of beamstop in pixels"),
    ],
    beamstop_kind: Annotated[
        BeamstopType,
        typer.Option(
            ...,
            "--beamstop-kind",
            "-k",
            help='Type of beamstop, either "cross" or "square"',
        ),
    ] = BeamstopType.cross,
):
    """
    Create a beamstop
    """
    from pets.create_bs import create_bs, create_center_bs

    if beamstop_kind == BeamstopType.cross:
        bs = create_bs(beamstop_width=beamstop_width, image_width=image_width)
    elif beamstop_kind == BeamstopType.square:
        bs = create_center_bs(beamstop_width=beamstop_width, image_width=image_width)
    else:
        raise RuntimeError("Unreachable")

    if output.exists() and output.is_dir():
        output = output / "beamstop.xyz"
        rich.print(
            f"[bold yellow]Output path is an existing directory, writing to {output} instead"
        )
    if output.exists() and output.is_file():
        yes = typer.confirm(
            f"Trying to write to {output}.\nFile already exists. Override? ",
            default=True,
        )
        if not yes:
            return

    with open(output, "w") as wf:
        wf.write(bs)
    print(f"Wrote {len(bs.splitlines())} lines to {output}")


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def pets_solve(
    composition: Annotated[
        str,
        typer.Option(
            ...,
            "-m",
            "--composition",
            help="Composition of substance, e.g. SiO or Si2O4. Case sensitive.",
        ),
    ],
    pets_file: Annotated[
        Path, typer.Argument(..., help="Pets .pts2 file to read the Laue class from")
    ],
    ctx: typer.Context,
):
    """
    Runs SHELXT on the given project using the generated .hkl and .ins files from newest integration.
    Adds elements to .ins file and runs with the Laue group found in .pts2 file
    Any arguments can be added after the .pts2 file and will be passed on to SHELXT, overriding the defaults set by crysm:

    `crysm pets-solve pets.pts2 -l4 -a"0.5"`
    """
    from pets.run_shelx import run_shelx

    if not (isinstance(pets_file, Path) and pets_file.suffix == ".pts2"):
        raise RuntimeError(
            f"The first argument should be a .pts2 file, got {pets_file}"
        )
    run_shelx(pets_file, composition, ctx.args)


@app.command(
    help="Print lines to add to XDS.INP to correct the rotation axis and detector distance"
)
def xds_calibrate(
    pixel_size: Annotated[
        float,
        typer.Option(
            help="Calibrated pixel size, depends on camera length."
            "Suggested values: 120cm -> 0.00947, 150cm -> 0.007929, 200cm -> 0.006167"
        ),
    ] = 0.007929,
    rotation_axis: Annotated[
        float,
        typer.Option(help="Rotation axis in degrees. Default 231 degrees."),
    ] = 231,
):
    import xds.calibrate

    xds.calibrate.calibrate(rotation_axis=rotation_axis, pixel_size=pixel_size)


@app.command(help="Compare the indexed reflections in SMV/INTEGRATE.HKL and pets.hkl")
def compare_hkl():
    import compare_hkl as mod_compare_hkl

    mod_compare_hkl.main()


@app.command(help="Plot the distribution of indexed peaks in a pets .hkl-file")
def plot_hkl(filename: Path | None = None):
    import compare_hkl as mod_compare_hkl

    mod_compare_hkl.plot_hkl_file(filename)


@app.command(help="Plot the rocking curve from a .cml-file")
def plot_camel(filename: Annotated[Path, typer.Argument(help="The .cml file to plot")]):
    from matplotlib import pyplot as plt

    from pets.camel import parse_camel, plot_camel

    data = parse_camel(filename)
    _ax = plot_camel(data)
    plt.show()


if __name__ == "__main__":
    app()
