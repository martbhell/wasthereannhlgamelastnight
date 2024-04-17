""" Do some testing """

import urllib  # we validate that a website responds properly
from urllib.request import urlopen
import sys  # control exit codes
import json  # validate json
import datetime  # figure out year to have dynamic year testing
import argparse

# this bit should be improvable
#  https://docs.python.org/3/reference/import.html#regular-packages
import os

sys.path.append(os.path.realpath("src/"))

HOST = "https://testing-dot-wasthereannhlgamelastnight.appspot.com"

PARSER = argparse.ArgumentParser(
    prog="e2e_test",
    description="Run some requests to wtangy checking that it is still OK",
)

PARSER.add_argument("--host", help="URL to test, like https://wtangy.se", default=None)
ARGS = PARSER.parse_args()
if ARGS.host:
    HOST = ARGS.host

YESNO = ["YES\n", "NO\n"]

NOW = datetime.datetime.now()
THIS_YEAR = NOW.year
THIS_MONTH = NOW.month
LAST_YEAR = NOW.year - 1
NEXT_YEAR = NOW.year + 1
NEXT_MONTH = NOW.month + 1
BOTH_YEARS = [str(THIS_YEAR), str(LAST_YEAR)]

if 3 < THIS_MONTH < 10:
    print("INFO: returning True because we are in the off-season")
    sys.exit(0)

# This is a list of the basic tests / arguments.
TIME_INTERVALS = [1, 2, 3, 4, 5, 6, 6, 10, 12, 15, 20, 22, 100, 130, 190]
TIMEDELTAS = [NOW + datetime.timedelta(days=i) for i in TIME_INTERVALS]
YESNODATES = []
for D in TIMEDELTAS:
    YESNODATES.append(D.strftime("%Y%m%d"))

YESNODATES = [
    "wingS/" + TIMEDELTAS[7].strftime("%Y%m%d"),
    "wingS/" + TIMEDELTAS[8].strftime("%Y%m%d"),
    TIMEDELTAS[9].strftime("%Y%m%d") + "/wingS",
    "",
    "WINGS",
    "Lak",
    "github_action_e2e_test",
]

# First we define two special URIs where we do some extra testing
ARGS = {
    "00-update_schedule": {
        "url": "update_schedule",
        "test": ["accounts.google.com"],
        "type": "in",
    },
    "00-get_schedule": {"url": "get_schedule", "test": ["teamdates"], "type": "injson"},
    "00-version": {"url": "version", "test": BOTH_YEARS, "type": "in"},
    "01-version": {"url": "version", "test": ["version"], "type": "json"},
}


ALLTEAMS = ["PIT"]

MUSTGETAYES = {}

for team in ALLTEAMS:
    MUSTGETAYES[team] = []
    for DA in TIMEDELTAS:
        MUSTGETAYES[team].append(DA.strftime("%Y%m%d"))

# Add the tests where we want to check that we get at least one yes
#  for each team
for team, value in MUSTGETAYES.items():
    print(team)
    print(value)
    YESCNT = 0
    ALLCNT = 0
    for dstring in value:
        estring = team + "/" + dstring
        try:
            with urlopen(f"{HOST}/{estring}") as response:
                html = response.read()
        except urllib.error.HTTPError as urlliberror:
            print(f"Cannot fetch URL: {urlliberror}")
            sys.exit(67)
        ALLCNT = ALLCNT + 1
        if "YES" in str(html):
            YESCNT = YESCNT + 1
        if ALLCNT == len(value):
            print(
                f"asserting that at least ( {YESCNT} ) one of {str(value)} is YES for {team}"
            )
            try:
                assert YESCNT > 0
                # print(str(YESCNT) + " for " + team)
            except AssertionError:
                print(f"No games found in schedule for {team}")
                sys.exit(5)

# Add the "basic" tests where we should only get a YES or NO
for date in YESNODATES:
    ARGS[date] = {"url": date, "test": YESNO}

for arg, value in ARGS.items():
    try:
        with urlopen(f"{HOST}/{value['url']}") as response:
            html = response.read()
    except urllib.error.HTTPError as urlliberror:
        print(f"Cannot fetch URL: {urlliberror}")
        sys.exit(66)

    if value["test"] == YESNO:
        print(f"asserting {HOST}/{arg} - response code: {response.code}")
        try:
            print(str(html))
            assert "NO" in str(html) or "YES" in str(html)
        except AssertionError:
            print(f"{HOST}/{arg} does not contain 'YES\n or NO\n'")
            sys.exit(3)

    else:
        print(
            f"{arg}: asserting {HOST}/{value['url']} contains {value['test']} - response code: {response.code}"
        )
        try:
            if value["type"] == "in" or value["type"] == "injson":
                # this any loops over tests in ARGS[arg]['test']). There's also an all()
                assert any(anarg in str(html) for anarg in value["test"])
        except AssertionError:
            print("{HOST}/{arg} does not contain {ARGS[arg]}")
            sys.exit(4)
        if value["type"] == "injson":
            try:
                assert json.loads(html)["teamdates"].popitem()
            except KeyError:
                print(f"popitem of JSON on {HOST}/{arg} key {value['test']} failed")
                sys.exit(6)
        if value["type"] == "json":
            try:
                assert json.loads(html)
            except TypeError:
                print("json.dumps of JSON on {HOST}/{arg}")
                sys.exit(7)
