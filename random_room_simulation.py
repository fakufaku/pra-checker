import argparse
import math
import random
from pathlib import Path

import numpy as np
import pyroomacoustics as pra
from scipy.io import wavfile

# Simulation parameters
_SEED = 20241029
_ROOM_DIM_RANGE = [2.5, 10]
_MIN_WALL_DIST = 1.0
_MIN_SRC_MIC_DIST = 1.5
_SAMPLE_RATE = 16000
_RT60_RANGE = [0.05, 0.7]
_AIR_ABSORPTION = False
_OCTAVE_BANDS_KEEP_DC = False


def compute_rir(room_dim, src_loc, mic_loc, e_absorption, max_order, rt60_tgt):

    room = pra.ShoeBox(room_dim, fs=_SAMPLE_RATE)
    pra.constants.set("octave_bands_keep_dc", _OCTAVE_BANDS_KEEP_DC)

    # Create the room
    room = pra.ShoeBox(
        room_dim,
        fs=_SAMPLE_RATE,
        materials=pra.Material(e_absorption),
        max_order=max_order,
        air_absorption=_AIR_ABSORPTION,
    )

    # place the source in the room
    room.add_source(src_loc)
    room.add_microphone(mic_loc)

    room.compute_rir()

    rt60_measured = room.measure_rt60()

    rir = room.rir[0][0]
    rt60 = np.round(rt60_measured[0][0] * 1000, decimals=0)
    rt60_tgt = np.round(rt60_tgt * 1000, decimals=0)

    return rir, int(rt60), int(rt60_tgt)


def sample_room_dim(rng, room_dim_range, min_wall_dist):
    while True:
        room_dim = [rng.uniform(*room_dim_range) for _ in range(3)]
        if all([r > 2 * min_wall_dist for r in room_dim]):
            break
    return np.array(room_dim)


def sample_point_from_room(rng, room_dim, min_wall_dist):
    return np.array([rng.uniform(min_wall_dist, r - min_wall_dist) for r in room_dim])


def generate_parameters(num_rirs):

    rng = random.Random(_SEED)

    parameters = []

    while len(parameters) < num_rirs:
        room_dim = sample_room_dim(rng, _ROOM_DIM_RANGE, _MIN_WALL_DIST)
        while True:
            src_loc = sample_point_from_room(rng, room_dim, _MIN_WALL_DIST)
            mic_loc = sample_point_from_room(rng, room_dim, _MIN_WALL_DIST)

            if np.linalg.norm(src_loc - mic_loc) > _MIN_SRC_MIC_DIST:
                break

        rt60_tgt = rng.uniform(*_RT60_RANGE)

        try:
            # We invert Sabine's formula to obtain the parameters for the ISM simulator
            e_absorption, max_order = pra.inverse_sabine(rt60_tgt, room_dim)
        except ValueError:
            continue

        parameters.append(
            (room_dim, src_loc, mic_loc, e_absorption, max_order, rt60_tgt)
        )

    return parameters


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate many random room impulse responses"
    )
    parser.add_argument(
        "--num", type=int, default=20, help="Number of RIRs to generate."
    )
    parser.add_argument("--out", type=Path, help="Output folder.")
    args = parser.parse_args()

    if args.out is None:
        args.out = Path(f"./rirs-{pra.__version__}")

    if _ROOM_DIM_RANGE[0] > _ROOM_DIM_RANGE[1] or any(
        [val <= 0 for val in _ROOM_DIM_RANGE]
    ):
        raise ValueError(
            "The room dimension range should contain increasing positive values."
        )

    if 2 * _MIN_WALL_DIST > _ROOM_DIM_RANGE[1] - _ROOM_DIM_RANGE[0]:
        raise ValueError(
            "The room dimension range should be at least "
            "twice the minimum wall distance."
        )

    if args.out.exists():
        raise ValueError(f"Path {args.out} already exists. Abort.")

    args.out.mkdir(parents=True)

    parameters = generate_parameters(args.num)

    num_zeros = math.ceil(math.log10(args.num))

    for idx, pmt in enumerate(parameters):
        rir, rt60, rt60_tgt = compute_rir(*pmt)

        path = args.out / f"{idx:0{num_zeros}d}_{rt60_tgt:d}_{rt60:d}.wav"

        wavfile.write(path, _SAMPLE_RATE, rir)
