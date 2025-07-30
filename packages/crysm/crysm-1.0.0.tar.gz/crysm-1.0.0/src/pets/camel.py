from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from matplotlib import pyplot as plt


@dataclass(slots=True)
class CamelLine:
    shell: float
    excitation: float
    rsg: float
    rc: float
    rcalc: float


@dataclass()
class CamelData:
    data: list[CamelLine]

    @cached_property
    def shells(self):
        return set([line.shell for line in self.data])

    @cached_property
    def excitations(self):
        _excitations = defaultdict(list)
        for line in self.data:
            _excitations[line.shell].append(line.excitation)
        return _excitations

    @cached_property
    def rcs(self):
        _rcs = defaultdict(list)
        for line in self.data:
            _rcs[line.shell].append(line.rc)
        return _rcs


def parse_camel(file: Path) -> CamelData:
    data = []
    for line in file.open():
        line = line.strip()
        if not line:
            continue
        shell, excitation, rsg, rc, rcalc = line.split()
        data.append(
            CamelLine(
                float(shell), float(excitation), float(rsg), float(rc), float(rcalc)
            )
        )
    return CamelData(data)


def plot_camel(data: CamelData):
    nplots = len(data.shells)
    _fig, axs = plt.subplots(nplots, sharex=True)
    for shell, ax in zip(sorted(data.shells, reverse=True), axs):
        exc = data.excitations[shell]
        rcd = data.rcs[shell]
        ax.plot(exc, [rc + shell for rc in rcd])

    return ax


if __name__ == "__main__":
    from lib.find_cred_project import find_cred_project

    cur_dir = find_cred_project()
    camelfiles = list(cur_dir.glob("**/*.cml"))
    if len(camelfiles) == 0:
        raise RuntimeError("No camel file found")
    camelfile = camelfiles[0]
    print(f"Found camel file {camelfile}")
    data = parse_camel(camelfile)
    plot_camel(data)
    plt.show()
