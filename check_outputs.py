import dataclasses
import itertools
from collections import defaultdict
import argparse
import math
import random
from pathlib import Path

import numpy as np
from tabulate import tabulate
import pyroomacoustics as pra
from scipy.io import wavfile


@dataclasses.dataclass(frozen=True)
class RIRInfo:
    path: Path
    num: int
    rt60_tgt: int
    rt60_meas: int


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Checks the RIR generated by different versions of pyroomacoustics."
        )
    )
    parser.add_argument(
        "--path",
        type=Path,
        default="./",
        help="Folder containing the simulation output folders.",
    )
    args = parser.parse_args()

    versions = set()
    files = defaultdict(dict)
    for folder in sorted(list(args.path.rglob("rirs-*"))):
        version = folder.name.split("-")[1]
        versions.add(version)
        for file in sorted(list(folder.rglob("*.wav"))):
            num, rt60_tgt, rt60_meas = file.stem.split("_")

            files[num][version] = RIRInfo(
                path=file,
                num=int(num),
                rt60_tgt=int(rt60_tgt),
                rt60_meas=int(rt60_meas),
            )

    # check that all files have all versions
    for num, infos in files.items():
        missing_versions = versions - set(infos.keys())
        if len(missing_versions) > 0:
            print(f"File {num} missing for versions {missing_versions}")

    mses = []
    versions = sorted(versions)
    for num, infos in files.items():
        rirs = []
        for version in versions:
            info = infos[version]
            fs, data = wavfile.read(info.path)
            rirs.append(data)
        rir_len = max([len(r) for r in rirs])
        mat = np.zeros((len(rirs), rir_len), dtype=rirs[0].dtype)
        for idx, rir in enumerate(rirs):
            mat[idx, : rir.shape[0]] = rir

        mses.append(np.mean(np.square(mat[:, None, :] - mat[None, :, :]), axis=-1))

    error = np.stack(mses, axis=0).mean(axis=0)

    headers = [""] + list(versions)
    rows = [[version] + row.tolist() for version, row in zip(versions, error)]
    print(tabulate(rows, headers=headers))
