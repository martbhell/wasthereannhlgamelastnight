# Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable
# law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and
# limitations under the License.

""" Do some testing """

from __future__ import absolute_import  #
from __future__ import print_function  # python3
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
LAST_YEAR = NOW.year - 1
NEXT_YEAR = NOW.year + 1
BOTH_YEARS = [str(THIS_YEAR), str(LAST_YEAR)]

# This is a list of the basic tests / arguments.
# TODO these dates should be updated to match that we only fetch next X weeks
YESNODATES = [
    str(THIS_YEAR) + "1013",
    str(LAST_YEAR) + "1013",
    str(NEXT_YEAR) + "0316",
    "wingS/" + str(LAST_YEAR) + "1014",
    "wingS/" + str(NEXT_YEAR) + "0315",
    str(NEXT_YEAR) + "0315" + "/wingS",
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
    MUSTGETAYES[team].append(str(THIS_YEAR) + "0327")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "0328")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "1014")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "0805")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "0806")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "1014")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "1015")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "1016")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "1017")
    MUSTGETAYES[team].append(str(THIS_YEAR) + "1018")
    MUSTGETAYES[team].append(str(LAST_YEAR) + "0327")
    MUSTGETAYES[team].append(str(LAST_YEAR) + "0328")
    MUSTGETAYES[team].append(str(LAST_YEAR) + "1014")
    MUSTGETAYES[team].append(str(LAST_YEAR) + "1015")
    MUSTGETAYES[team].append(str(LAST_YEAR) + "1016")
    MUSTGETAYES[team].append(str(LAST_YEAR) + "1017")
    MUSTGETAYES[team].append(str(LAST_YEAR) + "1018")

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
            f"asserting {HOST}/{arg} contains {value['test']} - response code: {response.code}"
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
