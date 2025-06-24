"""Do some testing"""

import argparse
import datetime  # figure out year to have dynamic year testing
import json  # validate json

# this bit should be improvable
#  https://docs.python.org/3/reference/import.html#regular-packages
import os
import sys  # control exit codes
import urllib  # we validate that a website responds properly
from urllib.request import urlopen

sys.path.append(os.path.realpath("src/"))

## Setting up some settings and stuff to test

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

# This is a list of the basic tests / arguments.
TIME_INTERVALS = [0, 1, 2, 3, 4, 5, 6, 6, 10, 12, 15, 20, 22, 100, 130, 190]
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

####


def test_2():
    """Add the tests where we want to check that we get at least one yes
     for each team
    We only test one team.."""
    yes_cnt = 0
    all_cnt = 0
    for key, value in MUSTGETAYES.items():
        print(key)
        print(value)
        for dstring in value:
            estring = key + "/" + dstring
            try:
                with urlopen(f"{HOST}/{estring}") as response:
                    html = response.read()
            except urllib.error.HTTPError as urlliberror:
                print(f"Cannot fetch URL: {urlliberror}")
                sys.exit(67)
            all_cnt = all_cnt + 1
            if "YES" in str(html):
                yes_cnt = yes_cnt + 1
            if all_cnt == len(value):
                print(
                    f"asserting that at least ( {yes_cnt} ) one of {str(value)} is YES for {key}"
                )
                try:
                    assert yes_cnt > 0
                    # print(str(yes_cnt) + " for " + key)
                except AssertionError:
                    # If there's any YES in any test, maybe that's enough to pass?
                    print(f"No games found in schedule for {key}")
                    return False
                    # sys.exit(5)
    return True


def fetch_html(url):
    """Get HTML"""
    try:
        with urlopen(url) as response:
            return response.read(), response.code
    except urllib.error.HTTPError as e:
        print(f"Cannot fetch URL: {e}")
        sys.exit(66)


def assert_yesno_response(arg, html, code):
    """You must decide"""
    print(f"asserting {HOST}/{arg} - response code: {code}")
    print(str(html))
    if not ("YES" in str(html) or "NO" in str(html)):
        print(f"{HOST}/{arg} does not contain 'YES' or 'NO'")
        sys.exit(3)


def assert_in_response(arg, html, test_values):
    """Strings are important"""
    if not any(val in str(html) for val in test_values):
        print(f"{HOST}/{arg} does not contain expected values: {test_values}")
        sys.exit(4)


def assert_injson_response(arg, html, test_values):
    """JSON popitem please"""
    try:
        data = json.loads(html)
        assert data["teamdates"].popitem()
    except (KeyError, AssertionError):
        print(f"popitem of JSON on {HOST}/{arg} key {test_values} failed")
        if not 6 <= THIS_MONTH <= 9:
            sys.exit(8)
        else:
            print("Not failing popitem, we are in the off-season")


def assert_json_response(arg, html):
    """Also JSON please"""
    try:
        json.loads(html)
    except TypeError:
        print(f"json.loads failed on {HOST}/{arg}")
        sys.exit(7)


def test_3():
    """Add the 'basic' tests where we should only get a YES or NO"""
    for date in YESNODATES:
        ARGS[date] = {"url": date, "test": YESNO}

    for arg, value in ARGS.items():
        url = f"{HOST}/{value['url']}"
        html, code = fetch_html(url)

        if value["test"] == YESNO:
            assert_yesno_response(arg, html, code)
            continue

        print(
            f"{arg}: asserting {url} contains {value['test']} - response code: {code}"
        )

        if value["type"] in ("in", "injson"):
            assert_in_response(arg, html, value["test"])
        if value["type"] == "injson":
            assert_injson_response(arg, html, value["test"])
        if value["type"] == "json":
            assert_json_response(arg, html)


###########
test_3()

TEST2_RESULTS = test_2()

if not TEST2_RESULTS and 3 < THIS_MONTH < 10:
    print(f"INFO: Not failing the failed ({TEST2_RESULTS}) - we are in the off-season")
    sys.exit(0)
if not TEST2_RESULTS:
    print(f"ERROR: Failing because ({TEST2_RESULTS})")
    sys.exit(5)

###########
