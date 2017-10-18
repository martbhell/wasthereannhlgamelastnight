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

ARGS= [ 'WINGS', 'Lak', 'foo', '20171012', 'WINGS/20171012', '20171013/WINGS', 'update_schedule' ]

for arg in ARGS:
  response = urllib2.urlopen("{}/%s".format(HOST) % arg)
  html = response.read()
  print response.code
  if arg != "update_schedule":
    assert(html == "NO\n" or html == "YES\n")
  else:
    assert("accounts.google.com" in html)
