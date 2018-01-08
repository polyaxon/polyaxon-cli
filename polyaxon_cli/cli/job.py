# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import click
import sys

from polyaxon_client.exceptions import PolyaxonHTTPError, PolyaxonShouldExitError

from polyaxon_cli.cli.experiment import get_experiment_or_local
from polyaxon_cli.cli.project import get_project_or_local
from polyaxon_cli.managers.job import JobManager
from polyaxon_cli.utils.clients import PolyaxonClients
from polyaxon_cli.utils.formatting import (
    Printer,
    dict_tabulate,
    get_meta_response,
    list_dicts_to_tabulate,
)


def get_job_or_local(experiment=None):
    return experiment or JobManager.get_config_or_raise().sequence


@click.group()
@click.option('--project', '-p', type=str, help="The project name, e.g. 'mnist' or 'adam/mnist'")
@click.option('--experiment', '-xp', type=int, help="The sequence number of the experiment")
@click.option('--job', '-j', type=int, help="The job sequence.")
@click.pass_context
def job(ctx, project, experiment, job):
    """Commands for jobs."""
    user, project_name = get_project_or_local(project)
    experiment = get_experiment_or_local(experiment)
    job = get_job_or_local(job)
    ctx.obj = ctx.obj or {}
    ctx.obj['user'] = user
    ctx.obj['project_name'] = project_name
    ctx.obj['experiment'] = experiment
    ctx.obj['job'] = job


@job.command()
@click.pass_context
def get(ctx):
    """Get job.

    Uses [Caching](/polyaxon_cli/introduction#Caching)

    Examples:

    \b
    ```bash
    $ polyaxon job --job=1 --experiment=1 get
    ```

    \b
    ```bash
    $ polyaxon job --job=1 --project=project_name get
    ```
    """
    user, project_name, experiment, job = (ctx.obj['user'],
                                           ctx.obj['project_name'],
                                           ctx.obj['experiment'],
                                           ctx.obj['job'])
    try:
        response = PolyaxonClients().job.get_job(user, project_name, experiment, job)
        # Set caching
        JobManager.set_config(response)
    except (PolyaxonHTTPError, PolyaxonShouldExitError) as e:
        Printer.print_error('Could not get job `{}`.'.format(job))
        Printer.print_error('Error message `{}`.'.format(e))
        sys.exit(1)

    response = Printer.add_status_color(response.to_light_dict(humanize_values=True))
    Printer.print_header("Job info:")
    dict_tabulate(response)


@job.command()
@click.pass_context
def statuses(ctx):
    """Get job status.

    Uses [Caching](/polyaxon_cli/introduction#Caching)

    Examples:

    \b
    ```bash
    $ polyaxon job -xp 1 -j 2 statuses
    ```
    """
    user, project_name, experiment, job = (ctx.obj['user'],
                                           ctx.obj['project_name'],
                                           ctx.obj['experiment'],
                                           ctx.obj['job'])
    try:
        response = PolyaxonClients().job.get_statuses(user, project_name, experiment, job)
    except (PolyaxonHTTPError, PolyaxonShouldExitError) as e:
        Printer.print_error('Could not get status for job `{}`.'.format(job))
        Printer.print_error('Error message `{}`.'.format(e))
        sys.exit(1)

    meta = get_meta_response(response)
    if meta:
        Printer.print_header('Statuses for Job `{}`.'.format(job))
        Printer.print_header('Navigation:')
        dict_tabulate(meta)
    else:
        Printer.print_header('No statuses found for job `{}`.'.format(job))

    objects = list_dicts_to_tabulate([Printer.handle_statuses(o.to_light_dict(humanize_values=True))
                                      for o in response['results']])
    if objects:
        Printer.print_header("Statuses:")
        objects.pop('job', None)
        dict_tabulate(objects, is_list_dict=True)


@job.command()
@click.pass_context
def resources(ctx):
    """Get job resources.

    Uses [Caching](/polyaxon_cli/introduction#Caching)

    Examples:

    \b
    ```bash
    $ polyaxon job -j 2 resources
    ```
    """
    user, project_name, experiment, job = (ctx.obj['user'],
                                           ctx.obj['project_name'],
                                           ctx.obj['experiment'],
                                           ctx.obj['job'])
    try:
        PolyaxonClients().job.resources(user,
                                        project_name,
                                        experiment,
                                        job,
                                        message_handler=Printer.resources)
    except (PolyaxonHTTPError, PolyaxonShouldExitError) as e:
        Printer.print_error('Could not get resources for job `{}`.'.format(job))
        Printer.print_error('Error message `{}`.'.format(e))
        sys.exit(1)


@job.command()
@click.pass_context
def logs(ctx):
    """Get job logs.

    Uses [Caching](/polyaxon_cli/introduction#Caching)

    Examples:

    \b
    ```bash
    $ polyaxon job -xp 3 -j 2 logs
    ```

    \b
    ```bash
    $ polyaxon job logs
    ```
    """
    user, project_name, experiment, job = (ctx.obj['user'],
                                           ctx.obj['project_name'],
                                           ctx.obj['experiment'],
                                           ctx.obj['job'])

    def message_handler(log_line):
        Printer.log(log_line['log_line'])

    try:
        PolyaxonClients().job.logs(user,
                                   project_name,
                                   experiment,
                                   job,
                                   message_handler=message_handler)
    except (PolyaxonHTTPError, PolyaxonShouldExitError) as e:
        Printer.print_error('Could not get logs for job `{}`.'.format(job))
        sys.exit(1)