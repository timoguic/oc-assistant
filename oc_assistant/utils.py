import os
from datetime import datetime, timedelta

from .constants import *

class CustomUtils:
    @staticmethod
    def get_username_password():
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

        return username, password

    @staticmethod
    def get_weekday_from_fuzzy_str(value):
        if not isinstance(value, str):
            value = str(value)

        if value.isdigit():
            value = int(value)
            if 0 <= value <= 6:
                return value
            else:
                raise ValueError("Invalid day: " + value)

        if value.title() in WEEKDAYS:
            return WEEKDAYS.index(value.title())

        if value.lower() in SHORT_WEEKDAYS:
            return SHORT_WEEKDAYS.index(value.lower())

    @staticmethod
    def check_int_values(*values):
        if any(map(lambda v: not str(v).isdigit(), values)):
            raise ValueError("Invalid value.")
        else:
            return list(map(int, values))

    @staticmethod
    def get_next_weekday_from_int(day, repeat=1):
        """
        Compute the next day whose weekday (int) is value.
        """

        today = datetime.today()
        # Thank you Stack Overflow
        next_day = today + timedelta(days=(day - today.weekday() + 7) % 7)
        current = 0

        while current < repeat:
            yield next_day
            next_day = next_day + timedelta(days=7)
            current = current + 1