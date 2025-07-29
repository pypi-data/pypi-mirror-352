# Contributing guide

Provided you have a machine that:

* runs Linux
* has CVMFS available
* supports user namespaces (most CentOS 7 or later machines do)

you should be able to get a local installation of the `lb-ap` command by following these steps:

```bash
# If you don't have conda installed already, install it
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
bash Mambaforge-Linux-x86_64.sh -b -p $HOME/mambaforge
rm Mambaforge-Linux-x86_64.sh
# Activate the environment manually the first time
eval "$("$HOME/mambaforge/bin/conda" shell.bash hook)"
# Make it so that conda doesn't automatically activate the base environment
conda config --set auto_activate_base false
# Automatically make the "conda" shell function available
conda init bash

# Create a development environment for lbaplocal
git clone ssh://git@gitlab.cern.ch:7999/lhcb-dpa/analysis-productions/lbaplocal.git
mamba env create --name analysis-productions-dev --file environment.yaml
conda activate analysis-productions-dev
pip install -e ./lbaplocal[testing]
# From now on you can activate it any time with "conda activate analysis-productions-dev"

# Clone the main Analysis Productions repository and reproduce the issue
git clone ssh://git@gitlab.cern.ch:7999/lhcb-datapkg/AnalysisProductions.git
cd AnalysisProductions
lb-ap test cbtesting MC_2011_MagDown_Lb2Lee_tuple
> Errors with "NotImplementedError: Currently only support bookkeeping inputs"
```

Additionally, [`pre-commit`](https://pre-commit.com/) is used to provide automatic formatting and other check with each commit.
This can be enabled by running the following from inside one of the Analysis Productions repositories:

```bash
$ pre-commit install
# The rest of this is a hacky workaround for the lack of a central "check copyright" hook
$ curl -o lb-check-copyright "https://gitlab.cern.ch/lhcb-core/LbDevTools/raw/master/LbDevTools/SourceTools.py?inline=false"
$ chmod +x lb-check-copyright
```

These tests will then be ran automatically when when you run a commit:

```bash
$ git commit -m "Add support for metadata"
Trim Trailing Whitespace.................................................Passed
Fix End of Files.........................................................Passed
Check Yaml...........................................(no files to check)Skipped
Check for added large files..............................................Passed
isort................................................(no files to check)Skipped
black................................................(no files to check)Skipped
flake8...............................................(no files to check)Skipped
[dev b6745db] Add support for metadata
 1 file changed, 3 insertions(+)
```

You can also run them manually using:

```
pre-commit run --all-files
```

## Running the unit tests

To run most of the tests:

```bash
$ pytest -vvv
```

Alternatively the full tests can be ran (including tests which are slow to run):

```bash
$ pytest -vvv --runslow
```
