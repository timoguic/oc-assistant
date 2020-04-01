"""Connector module."""
import os
import time
import requests
import click
import json

from datetime import datetime, timedelta
from dateutil.tz import tzlocal, tzutc
from dateutil.parser import isoparse

from oc_assistant.constants import *
from oc_assistant.utils import CustomUtils as utils


class OcConnector:
    def __init__(self, username=None, password=None, save_token=True, force_auth=False):
        """ Constructor """
        self._access_token = None
        self.save_token = save_token
        self.session = requests.Session()
        self.authenticated = self._authenticate(username, password, force_auth)

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, val):
        """ Updates the requests headers when setting the access token """
        self._access_token = val
        self.session.headers.update({"Authorization": "Bearer {}".format(val)})

    def _authenticate_from_file(self):
        try:
            # Get values from the local JSON file
            with open("bearer-token.json", "r") as fp:
                data = json.load(fp)
                # Looks like the token is still valid
                if isoparse(data["expiration_date"]) > datetime.now(tzlocal()):
                    click.echo("<<< Found token in file.")
                    self.access_token = data["token"]
                    self.user_id = data["user_id"]
                    return True
        except (FileNotFoundError, PermissionError):
            # Well, let's authenticate on the website then
            return False

    def _authenticate(self, username, password, force_auth=False):
        """
        Tries to authenticate.
        Raises RuntimeError if it fails.
        """

        if not force_auth:
            success = self._authenticate_from_file()

            if success:
                return True
            else:
                if not (username and password):
                    raise RuntimeError("No username / password provided.")

        # CSRF token
        click.echo("+++ Fetching CSRF token... ", nl=False)
        data = self.session.get(CSRF_URL).json()
        csrf = data["csrf"]
        click.echo("OK!")

        # Build auth payload
        data = {
            "_username": username,
            "_password": password,
            "_csrf_token": csrf,
        }

        click.echo("+++ Logging in... ", nl=False)

        # Not sure why, but it seems to be needed
        time.sleep(0.2)

        # Post data
        self.session.post(TOKEN_URL, data=data)

        # We did not find the `access_token` cookie. :sad:
        if not "access_token" in self.session.cookies.get_dict():
            return False

        click.echo("OK!")

        # Update the token
        self.access_token = self.session.cookies["access_token"]

        # We need the user ID to request the API
        click.echo("+++ Fetching user ID... ", nl=False)

        user_data = self.session.get(API_ME_URL).json()
        self.user_id = user_data["id"]

        click.echo(f"{self.user_id} - OK!")

        # We want to save the token to the file
        if self.save_token:
            # It usually expires in 1 hour == 3600s
            # Let's use 3500 to be on the safe side
            expiration_date = datetime.now(tzlocal()) + timedelta(seconds=3500)

            # Data to persist
            data = {
                "token": self.access_token,
                "expiration_date": expiration_date.isoformat(),
                "user_id": self.user_id,
            }
            with open("bearer-token.json", "w") as fp:
                json.dump(data, fp)
                click.echo("~~~ Saved token.")
        
        return True

    def get_events(self):
        """
        Requests the API to get calendar events with attendees.
        Returns dict.
        """

        api_data = self.session.get(API_USER_EVENTS.format(self.user_id)).json()
        data = list()

        for idx, event in enumerate(api_data):
            if not "attendees" in event:
                continue

            attendees = event["attendees"]
            student = attendees[0]["displayName"]
            start_date = isoparse(event["startDate"])
            end_date = isoparse(event["endDate"])

            str_date = datetime.strftime(start_date, "%d-%m-%Y")
            str_start_time = datetime.strftime(start_date, "%H:%M")
            str_end_time = datetime.strftime(end_date, "%H:%M")
            data.append((student, str_date, str_start_time, str_end_time))

        return data

    def _book_slot(self, day, start_time):
        hour = start_time
        date_start = datetime(
            day.year, day.month, day.day, hour, 0, tzinfo=tzlocal()
        )

        # The last hour of the day will get us to day:24:00 - change to day+1:00:00
        # Python idiosyncrasies with ISO8601
        if hour == 23:
            day = day + timedelta(days=1)
            hour = -1

        date_end = datetime(
            day.year, day.month, day.day, hour + 1, 0, tzinfo=tzlocal()
        )

        data = {
            "startDate": date_start.astimezone(tzutc()).isoformat(),
            "endDate": date_end.astimezone(tzutc()).isoformat(),
        }

        r = self.session.post(API_USER_AVAIL.format(self.user_id), json=data)
        if r.status_code in (200, 201, 204):
            return True

        return False

    @staticmethod
    def _validate_start_end(start_time, end_time):
        if start_time > end_time:
            raise ValueError("Start time must be before end time.")
        if start_time < 0 or end_time < 0:
            raise ValueError("Start / end time cannot be < 0.")
        if start_time > 24 or end_time > 24:
            raise ValueError("Start / end time cannot be > 24.")

    def book_series(self, day_of_week, start_time, end_time, nb_weeks):
        self._validate_start_end(start_time, end_time)

        # Book slots
        for next_day in utils.get_next_weekday_from_int(day_of_week, nb_weeks):
            click.echo(
                f"+++ Adding availability for {datetime.strftime(next_day, '%d-%m-%Y')}... ",
                nl=False,
            )

            day = datetime.date(next_day)
            # Loop through the range
            for hour in range(start_time, end_time):
                if self._book_slot(day, hour):
                    click.echo(f"{hour}:00 ", nl=False)
                else:
                    click.echo("! ", nl=False)

            click.echo("OK!")
    
    def release_series(self, day, start_time, end_time, nb_weeks):
        self._validate_start_end(start_time, end_time)

        days = [d for d in utils.get_next_weekday_from_int(day, nb_weeks)]
        days = list(map(datetime.date, days))

        availabilities = self.session.get(API_USER_AVAIL.format(self.user_id)).json()

        for avail in availabilities:
            # This does not seem like something we want
            if not "availabilityId" in avail:
                continue

            # Get local time
            avail_dt = isoparse(avail["startDate"]).astimezone(tzlocal())

            # Get date
            avail_date = datetime.date(avail_dt)

            # Slot is in the range -> delete
            if avail_date in days and start_time <= avail_dt.hour <= end_time - 1:
                # Get ID
                avail_id = avail["availabilityId"]

                delete_url = f"{API_BASE_URL}/availabilities/{avail_id}"
                r = self.session.delete(delete_url)

                if r.status_code in (200, 201, 204):
                    click.echo(f"{avail_dt:%d-%m-%Y@%H:%M} ", nl=False)
                else:
                    click.echo("! ", nl=False)

        click.echo("OK!")


    
