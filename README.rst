============
OC Assistant
============

Python package to facilitate interaction with OC website.

* Requires Python3 and Pip
* Free software: GNU General Public License v3


Features
--------

Set up your username and password in a text file called `oc-credentials.txt`.
You can also use an environment variable: `OC_USERNAME` and `OC_PASSWORD`.
Another option is to use `oc_assistant check` - if no username/password combinations are found, the program will prompt for them and save it to the `oc-credentials.txt` file.

**USE AT YOUR OWN RISK.**

* `pip install --user oc-assistant`
* `oc_assistant check`: will try to connect to the API. Asks for username/password if not known.
* `oc_assistant add fri 10 16 4`: adds availabilities on Fridays from 10:00 to 16:00, recurring for 4 weeks
* `oc_assistant add Monday 10 24 8`: adds availabilities on Mondays from 10:00 to midnight, recurring for 8 weeks
* `oc_assistant add 3 10 16`: adds availabilities next Wednesday (= day #3) from 10:00 to 16:00
* `oc_assistant rem fri 10 18 8`: removes any availabilities on Fridays from 10:00 to 18:00 for the next 8 weeks

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
