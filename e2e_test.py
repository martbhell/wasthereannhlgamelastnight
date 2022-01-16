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

# this bit should be improvable
#  https://docs.python.org/3/reference/import.html#regular-packages
import os

sys.path.append(os.path.realpath("src/"))
from NHLHelpers import (
    get_all_teams,
)  # pylint: disable=import-error,wrong-import-position

HOST = "https://testing-dot-wasthereannhlgamelastnight.appspot.com"

YESNO = ["YES\n", "NO\n"]

NOW = datetime.datetime.now()
THIS_YEAR = NOW.year
LAST_YEAR = NOW.year - 1
NEXT_YEAR = NOW.year + 1
BOTH_YEARS = [str(THIS_YEAR), str(LAST_YEAR)]

# This is a list of the basic tests / arguments.
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
    "travis_e2e_test",
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


# ALLTEAMS = sorted(list(get_all_teams().keys()))
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
for team in MUSTGETAYES:
    YESCNT = 0
    ALLCNT = 0
    for dstring in MUSTGETAYES[team]:
        estring = team + "/" + dstring
        try:
            response = urlopen(f"{HOST}/{estring}")
        except urllib.error.HTTPError as urlliberror:
            print(f"Cannot fetch URL: {urlliberror}")
            sys.exit(67)
        html = response.read()
        ALLCNT = ALLCNT + 1
        if "YES" in str(html):
            YESCNT = YESCNT + 1
        if ALLCNT == len(MUSTGETAYES[team]):

            print(
                f"asserting that at least ( {YESCNT} ) one of {str(MUSTGETAYES[team])} is YES for {team}"
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

for arg in ARGS:
    try:
        response = urlopen(f"{HOST}/{ARGS[arg]['url']}")
    except urllib.error.HTTPError as urlliberror:
        print(f"Cannot fetch URL: {urlliberror}")
        sys.exit(66)
    html = response.read()

    if ARGS[arg]["test"] == YESNO:
        print(f"asserting {HOST}/{arg} - response code: {response.code}")
        try:
            print(str(html))
            assert "NO" in str(html) or "YES" in str(html)
        except AssertionError:
            print(f"{HOST}/{arg} does not contain 'YES\n or NO\n'")
            sys.exit(3)

    else:
        print(
            f"asserting {HOST}/{arg} contains {ARGS[arg]['test']} - response code: {response.code}"
        )
        try:
            if ARGS[arg]["type"] == "in" or ARGS[arg]["type"] == "injson":
                # this any loops over tests in ARGS[arg]['test']). There's also an all()
                assert any(anarg in str(html) for anarg in ARGS[arg]["test"])
        except AssertionError:
            print("{HOST}/{arg} does not contain {ARGS[arg]}")
            sys.exit(4)
        if ARGS[arg]["type"] == "injson":
            try:
                assert json.loads(html)["teamdates"].popitem()
            except KeyError:
                print(f"popitem of JSON on {HOST}/{arg} key {ARGS[arg]['test']} failed")
                sys.exit(6)
        if ARGS[arg]["type"] == "json":
            try:
                assert json.loads(html)
            except TypeError:
                print("json.dumps of JSON on {HOST}/{arg}")
                sys.exit(7)
