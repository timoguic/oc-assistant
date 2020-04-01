# Base URLs
BASE_URL = "https://openclassrooms.com"
CSRF_URL = BASE_URL + "/login_ajax"
TOKEN_URL = BASE_URL + "/login_check"

# API URLs
API_BASE_URL = "https://api.openclassrooms.com"
API_ME_URL = API_BASE_URL + "/me"
API_USER_EVENTS = API_BASE_URL + "/users/{}/events"
API_USER_AVAIL = API_BASE_URL + "/users/{}/availabilities"

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

SHORT_WEEKDAYS = [d.lower()[:3] for d in WEEKDAYS]