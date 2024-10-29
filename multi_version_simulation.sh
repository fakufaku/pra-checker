#!/bin/bash

PY="3.10"
VERSIONS="0.6.0 0.7.0 0.7.7"
NUM_RIR=100

for version in ${VERSIONS}; do
    env_name="pra-${version}"
    echo ${env_name}

    echo "- Create micromamba env"
    # For compatibility with older versions, we require slightly older
    # versions of numpy and scipy.
    micromamba create -y -q -n ${env_name} python=${PY} 'numpy<2' 'scipy<=1.8.1' -c anaconda

    # PYBIN="$MAMBA_ROOT_PREFIX/envs/${env_name}/bin/python"

    echo "- Install pyroomacoustics"
    micromamba run -n ${env_name} python -m pip install -q "pyroomacoustics==${version}"

    # run some program
    echo "- Run simulation"
    micromamba run -n ${env_name} python ./random_room_simulation.py --num ${NUM_RIR}

    # delete the environment
    echo "- Delete micromamba env"
    micromamba env remove -n ${env_name} -y -q
done
