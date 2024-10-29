# pyroomacoustics checker

Simulates random RIRs with different versions of
[pyroomacoustics](https://github.com/LCAV/pyroomacoustics) and compares the
result.

Note that the scripts only check the most stable part of the API, namely, the
pure image source model.

## Preliminaries

Install [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html).

## Usage

The script relies on [micromamba](

```bash
$ ./multi_version_simulation.sh
$ python ./check_outputs.py
             0.6.0        0.7.0        0.7.7        0.8.0
-----  -----------  -----------  -----------  -----------
0.6.0  0            0            1.28433e-11  1.30244e-11
0.7.0  0            0            1.28433e-11  1.30244e-11
0.7.7  1.28433e-11  1.28433e-11  0            1.16838e-13
0.8.0  1.30244e-11  1.30244e-11  1.16838e-13  0
```
