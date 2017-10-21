# Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable
# law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and
# limitations under the License.


import urllib2
import logging

HOST='https://testing-dot-wasthereannhlgamelastnight.appspot.com'

ARGS= [ '', 'WINGS', 'Lak', 'travis_e2e_test', '20171012', 'WINGS/20171012', '20171013/WINGS', 'update_schedule', 'get_schedule') ]

for arg in ARGS:
  response = urllib2.urlopen("{}/%s".format(HOST) % arg)
  html = response.read()
  if arg != "update_schedule":
    print "asserting %s/%s - response code: %s" % (HOST,arg,response.code)
    assert(html == "NO\n" or html == "YES\n")
  elif arg != "get_schedule":
    print "asserting %s/%s - response code: %s" % (HOST,arg,response.code)
  else:
    print "asserting %s/%s - response code: %s" % (HOST,arg,response.code)
    assert("accounts.google.com" in html)
