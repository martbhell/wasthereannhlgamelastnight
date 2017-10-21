# Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable
# law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and
# limitations under the License.

""" Do some testing """

import urllib2
import sys
import json

HOST = 'https://testing-dot-wasthereannhlgamelastnight.appspot.com'

YESNO = ["YES\n", "NO\n"]

ARGS = {
    '':                 {"test": YESNO},
    'WINGS':            {"test": YESNO},
    'Lak':              {"test": YESNO},
    'travis_e2e_test':  {"test": YESNO},
    '20171012':         {"test": YESNO},
    'WINGS/20171013':   {"test": YESNO},
    'WINGS/20171014':   {"test": YESNO},
    'update_schedule':  {"test": 'accounts.google.com', "type": "in"},
    'get_schedule':     {"test": 'teamdates', "type": "injson"},
}

for arg in ARGS:
    try:
        response = urllib2.urlopen("{}/%s".format(HOST) % arg)
    except urllib2.HTTPError as urlliberror:
        print "Cannot fetch URL: %s" % urlliberror
        sys.exit(66)
    html = response.read()

    if ARGS[arg]['test'] == YESNO:
        print "asserting %s/%s - response code: %s" % (HOST, arg, response.code)
        try:
            assert html == "NO\n" or html == "YES\n"
        except AssertionError:
            print "%s/%s does not contain %s" % (HOST, arg, "YES\n or NO\n")
            sys.exit(3)

    else:
        print "asserting %s/%s contains %s- response code: %s" % (HOST, arg, ARGS[arg]['test'], response.code) # pylint: disable=line-too-long
        try:
            if ARGS[arg]['type'] == "in" or ARGS[arg]['type'] == "injson":
                assert ARGS[arg]['test'] in html
        except AssertionError:
            print "%s/%s does not contain %s" % (HOST, arg, ARGS[arg])
            sys.exit(1)
        if ARGS[arg]['type'] == "injson":
            try:
                assert json.loads(html)['teamdates'].popitem()
            except KeyError:
                print "popitem of JSON on %s/%s key %s failed" % (HOST, arg, ARGS[arg]['test'])
                sys.exit(1)
