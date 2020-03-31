"""Console script for oc_assistant."""
import sys
import click

import os
import requests

from oc_assistant.connector import OcConnector

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    Use `add` to add availabilities.
    Use `rem` to remove availabilities.
    """
    username = os.environ.get("OC_USERNAME", None)
    password = os.environ.get("OC_PASSWORD", None)

    if not (username and password):
        try:
            with open("oc-credentials.txt", "r") as fp:
                try:
                    username, password, *_ = [line.strip() for line in fp.read().split()]
                except ValueError:
                    click.secho("!!! Cannot find credentials in file", fg="red")
        except (FileNotFoundError, PermissionError):
            pass

    if ctx.invoked_subcommand:
        ctx.obj = OcConnector(username=username, password=password)
    else:
        click.echo("Please use --help for usage.")

@main.command()
@click.argument("day_of_week")
@click.argument("start_hour")
@click.argument("end_hour")
@click.argument("nb_weeks", default=1)
@click.pass_obj
def add(connector, day_of_week, start_hour, end_hour, nb_weeks):
    """
    Create available slots on every `day_of_week`.
    Ranges from `start_hour` to `end_hour - 1`, repeats for `nb_weeks`.

    Day of week:
    can be a number (0-6, with 0 = Monday),
    a short day name (mon, tue, wed) or a full day name (Monday, Tuesday, ...)

    Start / end hours:
    "18 23" will book a block, starting at 6PM and ending at 11PM (last meeting @ 10PM)
    """

    day_of_week = OcConnector._weekday_from_fuzzy(day_of_week)

    # Check for integer values
    values_to_check = (start_hour, end_hour, nb_weeks)
    if any(map(lambda v: not str(v).isdigit(), values_to_check)):
        raise ValueError("Invalid value.")
    else:
        start_hour, end_hour, nb_weeks = list(map(int, values_to_check))

    click.echo(
        f"+++ Creating {nb_weeks} week{('', 's')[nb_weeks>1]} of availabilities: ",
        nl=False,
    )
    click.echo(f"every {WEEKDAYS[day_of_week]}, {start_hour}:00-{end_hour}:00.")
    connector.set_recur_day(day_of_week, start_hour, end_hour, nb_weeks)


@main.command()
@click.argument("dow")
@click.argument("starth")
@click.argument("endh")
@click.argument("nb_weeks", default=1)
def rem(dow, starth, endh, nb_weeks):
    """
    Removes repeating slots for every `day_of_week`, from `starth` to `endh - 1`.
    Repeats for `nb_weeks`.

    Day of week:
    can be a number (0-6, with 0 = Monday),
    a short day name (mon, tue, wed) or a full day name (Monday, Tuesday, ...)

    Start / end hours:
    "18 23" will remove any block starting between 6PM and 10PM.
    """
    c = OcConnector(username=USERNAME, password=PASSWORD)
    c.remove_recur_day(dow, int(starth), int(endh), int(nb_weeks))


@main.command()
@click.pass_obj
def check(connector):
    if connector.authenticated:
        click.secho(f"=== All good. Your OC user id is {connector.user_id}.", fg="green")
    else:
        click.secho(f"!!! Something went wrong.", fg="red")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
