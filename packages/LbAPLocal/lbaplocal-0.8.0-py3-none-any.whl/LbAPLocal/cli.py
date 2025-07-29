###############################################################################
# (c) Copyright 2020-2024 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import importlib.metadata
import os
import re
import shlex
import shutil
import subprocess
from glob import glob
from pathlib import Path
from typing import Iterable

import click
from apd.authentication import get_auth_headers
from LbAPCommon import parse_yaml, render_yaml, validate_yaml

from .utils import (
    LBAPI_HOST,
    available_productions,
    check_production,
    inside_ap_datapkg,
    logging_subprocess_run,
    production_name_type,
    production_to_versions,
    validate_environment,
)


class NaturalOrderGroup(click.Group):
    """Group for showing subcommands in the correct order"""

    def list_commands(self, ctx):
        return self.commands.keys()


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for package in ["LbAPLocal", "LbAPCommon", "LbEnv", "LbDiracWrappers"]:
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            click.secho(f"{package} is not installed", fg="red")
        else:
            click.echo(f"{package} version: {version}")
    ctx.exit()


@click.group(cls=NaturalOrderGroup)
@click.option(
    "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True
)
def main():
    """Command line tool for the LHCb AnalysisProductions"""
    pass


@main.command()
def login():
    """Login to the Analysis Productions API"""
    import requests

    r = requests.get(f"{LBAPI_HOST}/user", **get_auth_headers())
    r.raise_for_status()
    click.secho(f"Logged in successfully as {r.json()['username']}", fg="green")


@main.command()
@click.argument("working_group", type=str, default=None, nargs=1, required=False)
@click.argument(
    "production_name", type=production_name_type, default=None, nargs=1, required=False
)
def versions(working_group: str, production_name: production_name_type) -> None:
    """List the available tags of the Analysis Productions repository by running 'lb-ap versions' \n
    List the available tags for a specific production by running 'lb-ap versions <WORKING_GROUP> <YOUR_PRODUCTION>'
    """
    # TODO the comments below are to facilitate mapping each version to a production but requires some changes
    # in the api website at a later date
    if not production_name:
        # from apd import AnalysisData
        # from apd.ap_info import fetch_wg_info
        # versions_to_productions = {}
        if not working_group:
            raise click.ClickException(
                "version querying currently only works with working group,"
                " and production name specified! lb-ap versions WORKING_GROUP PRODUCTION_NAME"
            )
        #    from LbAPCommon.config import known_working_groups
        #    for wg in known_working_groups:
        #        productions = fetch_wg_info(wg)
        #        for production in productions:
        #            dataset = AnalysisData(wg, production)
        #            for version in dataset.available_tags["versions"]:
        #                versions_to_productions[version] = [wg, production]
        else:
            raise click.ClickException(
                "version querying currently only works with working group,"
                " and production name specified! lb-ap versions WORKING_GROUP PRODUCTION_NAME"
            )

            # productions = fetch_wg_info(wg)
            # for production in productions:
            #    dataset = AnalysisData(wg, production)
            #    for version in dataset.available_tags["versions"]:
            #        versions_to_productions[version] = [wg, production]
        # click.echo(f"The available versions are:")
        # for version, wg_production in versions_to_productions.items():
        #    click.echo(f"{version}: {wg_production[0]} {wg_production[1]}")
    else:
        versions = production_to_versions(working_group, production_name)
        click.echo(f"The available versions for {production_name} are: ")
        for version in versions:
            click.echo(f"    {version}")


@main.command()
@click.argument("working_group", type=str, nargs=1)
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("version", type=str, nargs=1)
@click.argument("branch_name", type=str, nargs=1)
@click.option(
    "--clone-type", type=click.Choice(["ssh", "https", "krb5"]), default="ssh"
)
def clone(
    working_group: str,
    production_name: production_name_type,
    version: str,
    branch_name: str,
    clone_type: str = "ssh",
) -> None:
    """Clone the AnalysisProductions repository and do lb-ap checkout
    with the specified version, production and branch name."""
    if version not in production_to_versions(working_group, production_name):
        raise click.ClickException(
            f"Version {version} does not correspond to the {production_name} production!."
        )
    click.secho(
        f"Cloning AnalysisProductions, changing {production_name} to that,"
        f" of {version} and checking out the {branch_name} branch.",
        fg="yellow",
    )
    if clone_type == "ssh":
        clone_url = "ssh://git@gitlab.cern.ch:7999/lhcb-datapkg/AnalysisProductions.git"
    elif clone_type == "https":
        clone_url = "https://gitlab.cern.ch/lhcb-datapkg/AnalysisProductions.git"
    elif clone_type == "krb5":
        clone_url = "https://:@gitlab.cern.ch:8443/lhcb-datapkg/AnalysisProductions.git"
    else:
        raise NotImplementedError(clone_type)
    _run_git("clone", clone_url)
    if os.path.isdir("./AnalysisProductions"):
        os.chdir("./AnalysisProductions")
        _checkout(
            working_group, production_name, version, branch_name, allow_deletes=True
        )
    else:
        raise click.ClickException(
            f"Cloning the repository failed! Check you have the correct permissions,"
            f" to clone via {clone_type} or choose a different clone type [ssh, https, krb5]"
        )


@main.command()
@click.argument("working_group", type=str, nargs=1)
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("version", type=str, nargs=1)
@click.argument("branch_name", type=str, nargs=1)
@click.option("--allow-deletes/--no-allow-deletes", default=False)
def checkout(
    working_group: str,
    production_name: production_name_type,
    version: str,
    branch_name: str,
    allow_deletes: bool,
) -> None:
    """Clean out the current copy of the specified production and clone the production from the specified version \n
    List the available tags for a specific production by running 'lb-ap versions <YOUR_PRODUCTION>'
    """
    _checkout(
        working_group,
        production_name,
        version,
        branch_name,
        allow_deletes=allow_deletes,
    )


def _checkout(
    working_group: str,
    production_name: production_name_type,
    version: str,
    branch_name: str,
    *,
    allow_deletes: bool,
):
    inside_ap_datapkg()
    repo_dir = Path.cwd()
    if version not in production_to_versions(working_group, production_name):
        raise click.ClickException(
            f"Version {version} does not correspond to the {working_group} {production_name} production!"
        )

    proc = _run_git("status", "--porcelain")
    if proc.stdout.strip():
        raise click.ClickException(
            f"Current git repository is not clean: {proc.stdout}"
        )
    _run_git("fetch", "origin", "--tags")
    _run_git("checkout", "-b", branch_name, "origin/master")

    for child in repo_dir.iterdir():
        if child.name.lower() != production_name.lower():
            continue
        if allow_deletes:
            shutil.rmtree(child)
        else:
            raise FileExistsError(
                f"{child.name} already exists in {repo_dir}. If you're ABSOLUTELY "
                "sure you want to delete it, run this command with --allow-deletes."
            )

    proc = _run_git("ls-tree", "-d", version, printing=False)
    for line in proc.stdout.strip().splitlines():
        _, git_prod_name = line.decode().split("\t")
        if git_prod_name.lower() == production_name.lower():
            break
    else:
        raise click.ClickException(
            f"Failed to find match for {production_name} in {version}"
        )
    click.secho(f"Found match for {production_name} -> {git_prod_name} in {version}!")

    click.secho(f"Checking out the {version} version of {production_name}", fg="yellow")
    _run_git("checkout", version, "--", git_prod_name)
    _run_git("commit", "-m", f"Restore {git_prod_name} from {version}")


def _run_git(
    *args: Iterable[str], printing: bool = True
) -> subprocess.CompletedProcess:
    """Run a git command and return the output."""
    cmd = ("git",) + args
    click.secho(f"Running {shlex.join(cmd)}", bold=True)
    proc = logging_subprocess_run(cmd, printing=printing)
    if proc.returncode != 0:
        raise click.ClickException(f"Failed to run git command: {proc.args}")
    return proc


@main.command()
@click.argument("production_name", type=production_name_type, default="", nargs=1)
def list(production_name):
    """List the available production folders by running 'lb-ap list' \n
    List the available productions for a specific production by running 'lb-ap list <YOUR_PRODUCTION>'
    """
    inside_ap_datapkg()

    if production_name:
        # Check if production exists
        check_production(production_name)
        click.echo(f"The available jobs for {production_name} are: ")

        # Get rendered yaml and find all the production names
        with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
            raw_yaml = fp.read()
        job_data = parse_yaml(render_yaml(raw_yaml))
        for job_name in job_data:
            click.echo(f"* {job_name}")
    else:
        click.echo("The available productions are: ")
        for folder in available_productions():
            click.echo(f"* {folder}")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
def render(production_name):
    """Render the info.yaml for a given production"""
    inside_ap_datapkg()

    # Check if production exists
    check_production(production_name)

    # Get rendered yaml and print
    click.secho(f"Rendering info.yaml for {production_name}", fg="green")
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    render = render_yaml(raw_yaml)
    click.echo(render)
    try:
        job_data = parse_yaml(render)
        warnings = validate_yaml(job_data, ".", production_name)
    except Exception:
        click.secho("Rendered YAML has errors!", fg="red")
        click.secho(f'See "lb-ap validate {production_name}" for details', fg="red")
        raise click.ClickException("Failed to parse and validate YAML")
    else:
        for warning in warnings or []:
            click.secho(f"WARNING: {warning}", fg="yellow")
        click.secho("YAML parsed and validated successfully", fg="green")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
def validate(production_name):
    """Validate the configuration for a given production"""
    inside_ap_datapkg()

    # Check if production exists
    check_production(production_name)

    # Get rendered yaml and print
    click.secho(f"Rendering info.yaml for {production_name}", fg="green")
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    render = render_yaml(raw_yaml)

    try:
        job_data = parse_yaml(render)
    except Exception as e:
        click.secho("Error parsing YAML!", fg="red")
        raise click.ClickException(str(e))
    else:
        click.secho("YAML parsed successfully", fg="green")

    try:
        warnings = validate_yaml(job_data, ".", production_name)
    except Exception as e:
        click.secho("Error validating YAML!", fg="red")
        raise click.ClickException(str(e))
    else:
        for warning in warnings or []:
            click.secho(f"WARNING: {warning}", fg="yellow")
        click.secho("YAML validated successfully", fg="green")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, nargs=1)
@click.option("--validate/--no-validate", default=True)
@click.option(
    "-i",
    "--dependent-input",
    default=None,
    nargs=1,
    help="Run the test on a specific input file by passing either an LFN or a path to a local file",
)
@click.option(
    "-n",
    "--n-events",
    default=None,
    nargs=1,
    type=int,
    help="Run the test on specified number of events",
)
def test(production_name, job_name, dependent_input, n_events, validate):
    """Execute a job locally"""
    inside_ap_datapkg()

    # Check if production exists
    check_production(production_name)

    # validate test environment
    if validate:
        validate_environment()

    from .log_parsing import show_log_advice
    from .testing import prepare_test

    out_dir, prodrun_config_path = prepare_test(
        production_name, job_name, dependent_input, n_events
    )

    cmd = ["lb-prod-run", prodrun_config_path, "--verbose"]
    click.secho(f"Starting application with: {shlex.join(cmd)}", fg="green")
    result = logging_subprocess_run(cmd, cwd=out_dir)

    (out_dir / "stdout.log").write_bytes(result.stdout)
    (out_dir / "stderr.log").write_bytes(result.stderr)

    click.secho("Summary of log messages:", fg="green")
    show_log_advice(
        b"\n".join([result.stdout, result.stderr]).decode(errors="backslashreplace")
    )

    if result.returncode != 0:
        raise click.ClickException("Execution failed, see above for details")

    # Obtain the right output file name
    with open(os.path.join(production_name, "info.yaml"), "rt") as fp:
        raw_yaml = fp.read()
    # TODO do we really need to redo parsing and validating when prepare test already does it?
    prod_data = parse_yaml(render_yaml(raw_yaml))
    yaml_warnings = validate_yaml(prod_data, ".", production_name)
    try:
        job_data = prod_data[job_name]
    except KeyError:
        raise click.ClickException(
            f"Job {job_name} is not found for production {production_name}!"
        )
    output_file = job_data["output"][0]

    # Validating Gaudi options
    test_ntuple_path = out_dir / f"00012345_00006789_1.{output_file}"
    for file_path in glob(str(out_dir / "*")):
        if re.match(
            str(test_ntuple_path),
            file_path,
            re.IGNORECASE,
        ):
            test_ntuple_path = file_path
            break
    else:
        raise click.ClickException(
            "ERROR: The expected output file does not exist!\n"
            f"Expected: {test_ntuple_path}"
        )

    errors, warnings = [], []
    # TODO: This hasn't been updated to work with lb-prod-run
    click.secho("Options parsing is currently unavailable", fg="yellow")
    # if ".root" in test_ntuple_path.lower():
    #     errors, warnings = do_options_parsing(
    #         # TODO
    #         env_cmd,
    #         out_dir,
    #         join(out_dir, "output.pkl"),
    #         test_ntuple_path,
    #         job_name,
    #         prod_data,
    #     )
    warnings.extend(yaml_warnings or [])
    for warning in warnings or []:
        click.secho(f"WARNING: {warning}", fg="yellow")

    if errors:
        raise click.ClickException(
            "Found the following errors when parsing the options:"
            + "\n  * "
            + "\n  * ".join(errors)
        )
    if not any([warnings, errors]):
        click.secho(
            "No problems found while validating the options and output file!",
            fg="green",
        )

    # The functionality of job-dependent job testing relies on out_dir being written
    # in the line below as the final word so please be careful if changing the below line
    click.secho(f"Success! Output can be found in {out_dir}", fg="green")


@main.command()
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, nargs=1)
@click.option("--validate/--no-validate", default=True)
@click.option(
    "-i",
    "--dependent-input",
    default=None,
    nargs=1,
    help="Run the test on a specific input file by passing either an LFN or a path to a local file",
)
def debug(production_name, job_name, dependent_input, validate):
    """Start an interactive session inside the job's environment"""
    inside_ap_datapkg()
    check_production(production_name)
    if validate:
        validate_environment()

    from .testing import enter_debugging, prepare_test

    enter_debugging(*prepare_test(production_name, job_name, dependent_input))


@main.command()
@click.argument("pipeline_id", type=int, nargs=1)
@click.argument("production_name", type=production_name_type, nargs=1)
@click.argument("job_name", type=str, nargs=1)
@click.argument("test_id", type=str, nargs=1, default="latest")
@click.option("--validate/--no-validate", default=True)
def reproduce(pipeline_id, production_name, job_name, test_id, validate):
    """Reproduce an existing online test locally"""
    if validate:
        validate_environment()

    from .testing import enter_debugging, prepare_reproduce

    enter_debugging(*prepare_reproduce(pipeline_id, production_name, job_name, test_id))


@main.command()
@click.argument("log_fn", type=click.Path(exists=True))
@click.option(
    "--suppress",
    type=int,
    default=5,
    show_default=True,
    help="Minimum number of instances required to show ERROR and WARNING messages",
)
def parse_log(log_fn, suppress):
    """Read a Gaudi log file and extract information"""

    from .log_parsing import show_log_advice

    with open(log_fn, "rt") as fp:
        log_text = fp.read()

    click.echo(f"Summary of log messages in: {log_fn}")
    show_log_advice(log_text, suppress)
