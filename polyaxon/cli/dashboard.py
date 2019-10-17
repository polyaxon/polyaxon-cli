# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import sys

import click

from polyaxon.logger import clean_outputs
from polyaxon.schemas.cli.client_configuration import ClientConfig


@click.command()
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Automatic yes to prompts. "
    'Assume "yes" as answer to all prompts and run non-interactively.',
)
@click.option(
    "--url", is_flag=True, default=False, help="Print the url of the dashboard."
)
@clean_outputs
def dashboard(yes, url):
    """Open dashboard in browser."""
    dashboard_url = "{}/app".format(ClientConfig().host)
    if url:
        click.echo(dashboard_url)
        sys.exit(0)
    if not yes:
        click.confirm(
            "Dashboard page will now open in your browser. Continue?",
            abort=True,
            default=True,
        )

    click.launch(dashboard_url)