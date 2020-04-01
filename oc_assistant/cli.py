"""Console script for oc_assistant."""
import sys
import click

import os
import requests

from oc_assistant.connector import OcConnector
from oc_assistant.utils import CustomUtils as utils
from oc_assistant.constants import *

@click.group()
def main():
    """
    Use `add` to add availabilities.
    Use `rem` to remove availabilities.
    """

    pass


def do_add_rem(day_of_week, start_hour, end_hour, nb_weeks, callback_attr, message):
    # Validate arguments
    day_of_week = utils.get_weekday_from_fuzzy_str(day_of_week)
    start_hour, end_hour, nb_weeks = utils.check_int_values(start_hour, end_hour, nb_weeks)

    # Connector
    username, password = utils.get_username_password()
    connector = OcConnector(username, password)

    click.echo(
        f"+++ {message} {nb_weeks} week{('', 's')[nb_weeks>1]} of availabilities: ",
        nl=False,
    )
    click.echo(f"every {WEEKDAYS[day_of_week]}, {start_hour}:00-{end_hour}:00.")

    callback = getattr(connector, callback_attr)
    callback(day_of_week, start_hour, end_hour, nb_weeks)


@main.command()
@click.argument("day_of_week")
@click.argument("start_hour")
@click.argument("end_hour")
@click.argument("nb_weeks", default=1)
def add(day_of_week, start_hour, end_hour, nb_weeks):
    """
    Create available slots on every `day_of_week`.
    Ranges from `start_hour` to `end_hour - 1`, repeats for `nb_weeks`.

    Day of week:
    can be a number (0-6, with 0 = Monday),
    a short day name (mon, tue, wed) or a full day name (Monday, Tuesday, ...)

    Start / end hours:
    "18 23" will book a block, starting at 6PM and ending at 11PM (last meeting @ 10PM)
    """

    do_add_rem(day_of_week, start_hour, end_hour, nb_weeks, callback_attr="book_series", message="Adding")

@main.command()
@click.argument("day_of_week")
@click.argument("start_hour")
@click.argument("end_hour")
@click.argument("nb_weeks", default=1)
def rem(day_of_week, start_hour, end_hour, nb_weeks):
    """
    Removes repeating slots for every `day_of_week`, from `starth` to `endh - 1`.
    Repeats for `nb_weeks`.

    Day of week:
    can be a number (0-6, with 0 = Monday),
    a short day name (mon, tue, wed) or a full day name (Monday, Tuesday, ...)

    Start / end hours:
    "18 23" will remove any block starting between 6PM and 10PM.
    """
    
    do_add_rem(day_of_week, start_hour, end_hour, nb_weeks, callback_attr="release_series", message="Removing")

@main.command()
def check():
    # Connector
    username, password = utils.get_username_password()
    if not (username and password):
        from getpass import getpass

        click.secho("!!! No username / password found.", fg="red")
        username = input("Enter your OC username:")
        password = getpass("Enter your OC password (display hidden):")

        with open("oc-credentials.txt", "w") as fp:
            fp.write(f"{username}\n{password}")

        click.secho("~~~ Ok. Please run the program again.")
        sys.exit(0)
        
    connector = OcConnector(username, password)

    if connector.authenticated:
        click.secho(f"=== All good. Your OC user id is {connector.user_id}.", fg="green")
    else:
        click.secho(f"!!! Something went wrong.", fg="red")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
