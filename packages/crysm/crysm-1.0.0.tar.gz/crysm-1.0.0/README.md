# CRYSM

## Installation

The package can be installed from PyPI using 

```bash
pip install crysm
```

This exposes the `crysm` command. To see available commands, run `crysm --help`. The commands correspond to the decorated functions in `src/main.py`.

## Installation of uv

In this package, `uv` is used for package management. To install on linux/mac, run

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

and on windows (in powershell)

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Usage

The functionality of this library can be found by typing `crysm --help` or reading the functions in `src/main.py`. Below are some examples.

### Example 1: Finding correction factors for the central cross from a flatfield image

```bash
crysm find-center-cross-correction 24bit/flatfield_200kV_24bit.mib
> For image: 24bit/flatfield_200kV_24bit.mib:
>   Mean value of cross: 40151.59
>   Mean value of central four pixels: 74076.75
>   Mean value of rest of image: 18284.44
> Suggested arguments for correction:
>  --additional-pixels 4 --correction-factor 2.196 --central-four-factor 4.051
> Number of additional pixels should be verified with detector manufacturer
```

This command can also take multiple images, but they should be collected with the same parameters (unlike the example below):

```bash
crysm find-center-cross-correction 24bit/flatfield_200kV_24bit.mib 12bit/flatfield_200kV_12bit.mib 6bit/flatfield_200kV_6bit.mib                                          3.11   17:08:04
> For image: 24bit/flatfield_200kV_24bit.mib:
>   Mean value of cross: 40151.59
>   Mean value of central four pixels: 74076.75
>   Mean value of rest of image: 18284.44
>   Additional pixels: 4
>   Correction factor: 2.196
>   Central four factor: 4.051
> For image: 12bit/flatfield_200kV_12bit.mib:
>   Mean value of cross: 2013.16
>   Mean value of central four pixels: 3716.25
>   Mean value of rest of image: 916.51
>   Additional pixels: 4
>   Correction factor: 2.197
>   Central four factor: 4.055
> For image: 6bit/flatfield_200kV_6bit.mib:
>   Mean value of cross: 39.97
>   Mean value of central four pixels: 63.00
>   Mean value of rest of image: 18.22
>   Additional pixels: 4
>   Correction factor: 2.194
>   Central four factor: 3.457
> Suggested arguments for correction:
>  --additional-pixels 4 --correction-factor 2.195 --central-four-factor 3.854
> Number of additional pixels should be verified with detector manufacturer
```

### Example 2: Correcting the central cross of a calibration image

```bash
crysm pets-correct-center-cross-calibration --additional-pixels 4 --correction-factor 2.196 --central-four-factor 4.051 SAED_150cm.mib WIDE_150cm.tiff
> Wrote corrected image to WIDE_150cm.tiff
```

### Example 3: Correcting the central cross of a pets project

```bash
crysm pets-correct-center-cross --additional-pixels 4 --correction-factor 2.196 --central-four-factor 4.051
> Using cred project C:\Users\iverks\progging\master\cRED_070325\experiment_5
> 100%|█████████████████████████████████████████████████████████████████████████████| 1093/1093 [00:10<00:00, 109.19it/s]
> Wrote 1093 corrected images to C:\Users\iverks\progging\master\cRED_070325\experiment_5\tiff_corr
```

## Developers

In order to install the package locally, run 

```bash
uv tool install -e .
```

The `crysm` command is then available globally.

- `pets/run_shelx.py` depends on the internal format of .pts2-files, future updates might break
- `lib/find_cred_project.py` depends on the existence of cRED_log.txt, which Stef Smeets has hinted at removing in the future. Beware.
- To publish a new update to PyPi, bump the version number in pyproject.toml, then run `uv publish`. Developer permissions must be acquired first. 
