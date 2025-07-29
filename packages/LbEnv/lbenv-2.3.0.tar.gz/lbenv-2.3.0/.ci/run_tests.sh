#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Print each command before it is ran
set -x

if [ "$#" -ge 1 ] && [ "$1" == "PATCH_COVERAGE" ]; then
    # Patch the installation to include coverage for subprocesses
    # See: https://coverage.readthedocs.io/en/coverage-4.2/subprocess.html
    python -m pip install coverage
    cp always-include-coverage.pth "$(python -c "import sysconfig; print(sysconfig.get_path(\"purelib\"))")"
    export COVERAGE_DATA_DIR=${PWD}
    export COVERAGE_PROCESS_START=$PWD/.coveragerc
fi

if which apptainer >/dev/null 2>&1 ; then
    apptainer --version
fi
echo "CONTAINER_IMPLEMENTATION=${CONTAINER_IMPLEMENTATION:-}"

python --version
python -m pip install '.[testing]'
pytest -vv --doctest-modules --cov=LbEnv --cov-report=html
