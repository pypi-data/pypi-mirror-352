# LHCb Analysis Production submission

Welcome to the Analysis Production data package.
This is for analysts to upload options files, configure and submit Analysis Productions.
If you are looking for the magic behind the scenes, please see the [`LbAnalysisProductions` repository](https://gitlab.cern.ch/lhcb-dpa/analysis-productions).

## Table of contents

* [Overview](#overview)
* [Creating a new Analysis Production](#creating-a-new-analysis-production)
  * [YAML configuration](#yaml-configuration)
  * [Options files](#options-files)
  * [Python environment](#python-environment)
* [Testing](#testing)
  * [Local testing](#local-testing)
  * [Continuous integration](#continuous-integration)
* [Submitting](#submitting)
* [Monitoring](#monitoring)
* [Accessing output](#accessing-output)
* [Technical support](#technical-support)

## Overview

Analysis Productions are a method by which data processing can be performed using DIRAC, most commonly to produce ntuples for analysis.
This is similar to "WG productions" with a focus on individual analyses and automated tooling.
Productions are normally ran as follows:

1. Analysts create a merge request to this repository, adding their options and the associated metadata.
2. After the merge request is accepted, the production is submitted to LHCbDIRAC.
3. Productions are ran using the DIRAC transformation system and can be monitored on the [LHCbDIRAC web portal](https://lhcb-portal-dirac.cern.ch/DIRAC/?url_state=1|*LHCbDIRAC.AnalysisProductions.classes.AnalysisProductions:,).
4. After the transformations complete, the output data is replicated to CERN EOS.

## Creating a new Analysis Production

To create the configuration for a new analysis production, you will need to clone the repository and create a new branch:

```bash
git clone ssh://git@gitlab.cern.ch:7999/lhcb-datapkg/AnalysisProductions.git
cd AnalysisProductions
git checkout -b ${USER}/my-analysis
```

Then you need to create a directory containing an [`info.yml`](#yaml-configuration) and any [options files](#options-files) your jobs may need.

Once you have added these, you can commit and push your changes.

```bash
git add <new directory>
git commit -m "<meaningful commit message>"
git push -u origin ${USER}/my-analysis
```

### YAML configuration

Write a file called `info.yml` which will configure your jobs.

Each top-level key is the name of a job, and the value must be a dict whose allowed keys are:

| Key | Type | Meaning |
|:-- | :-- | :-- |
| `application`               | string         | The application and version that you want to run, separated by a `/`. |
| `options`                   | string or list | The options files to pass to the application. |
| `input`                     | dict           | The input to the job. You can use `bk_query` for data in BookKeeping, or `job_name` to use the output of another job in the same production. |
| `output`                    | string         | The output file to be registered in BookKeeping. |
| `wg`                        | string         | The Working Group that the analysis belongs to. The allowed values are listed [here](https://gitlab.cern.ch/lhcb-dpa/analysis-productions/LbAnalysisProductions/-/blob/1e7c90fdb8cd23686fdd1540d172dd8718c4a7a7/src/LbAnalysisProductions/config.py#L84-104). |
| `automatically_configure`\* | boolean        | Deduce common options based on the input data. (Default `False`) |
| `inform`\*                  | string or list | Email address(es) to inform about the status of the production. (Default empty) |

*\* optional keys.*

A job can therefore be created like this:

```yaml
My_job:
  application: DaVinci/v45r4
  wg: WG
  automatically_configure: yes
  inform:
    - someone@cern.ch
  options:
    - make_ntuple.py
  input:
    bk_query: /some/bookkeeping/path.DST
  output: DVNtuple.root
```

Instead of defining the same values for every job, you can use the special key `defaults`.

```yaml
defaults:
  application: DaVinci/v45r4
  wg: WG
  automatically_configure: yes
  inform:
    - someone@cern.ch
  options:
    - make_ntuple.py
  output: DVNtuple.root

My_MagUp_job:
  input:
    bk_query: /some/MagUp/bookkeeping/path.DST

My_MagDown_job:
  input:
    bk_query: /some/MagDown/bookkeeping/path.DST
```

You can use the [Jinja](https://jinja.palletsprojects.com/) templating language to add some python functionality, *e.g.* looping over years and polarities.

```yaml
defaults:
  application: DaVinci/v45r4
  wg: WG
  automatically_configure: yes
  inform:
    - someone@cern.ch
  options:
    - make_ntuple.py
  output: DVNtuple.root

{%- set datasets = [
  (11, 3500, '14', '21r1'),
  (12, 4000, '14', '21'),
  (15, 6500, '15a', '24r2'),
  (16, 6500, '16', '28r2'),
  (17, 6500, '17', '29r2'),
  (18, 6500, '18', '34'),
]%}

{%- for year, energy, reco, strip in datasets %}
  {%- for polarity in ['MagDown', 'MagUp'] %}

My_20{{year}}_{{polarity}}_job:
  input:
    bk_query: /LHCb/Collision{{year}}/Beam{{energy}}GeV-VeloClosed-{{polarity}}/Real Data/Reco{{reco}}/Stripping{{strip}}/90000000/BHADRON.MDST

  {%- endfor %}
{%- endfor %}

```

### Options files

The options files to be used with your jobs must be placed in the same folder as `info.yaml` or a subdirectory of that folder.

### Python environment

## Testing

### Local testing

Local tests can be performed using the `lb-ap` command in the LHCb environment.
See [`LbAPLocal`](https://gitlab.cern.ch/lhcb-dpa/analysis-productions/lbaplocal#lbaplocal) for more details.

### Continuous integration

Every commit that is pushed to this repository is tested using GitLab CI.
The CI logs will show a link which can be used for getting detailed information about the status of tests.

## Submitting

Open a merge request to master using the GitLab web interface.

## Monitoring

The status of a production can be monitored in the LHCbDIRAC web portal on the [`Analysis Productions`](https://lhcb-portal-dirac.cern.ch/DIRAC/?url_state=1|*LHCbDIRAC.AnalysisProductions.classes.AnalysisProductions:,) page.

## Accessing output

Currently the easiest way to access the output is using XRootD.
The page used for [monitoring](#monitoring) can be used for finding the XRootD URLs.

## Technical support

Questions cam be asked on the ["DPA WP2 Analysis Productions" mattermost channel](https://mattermost.web.cern.ch/lhcb/channels/dpa-wp2-analysis-productions).
