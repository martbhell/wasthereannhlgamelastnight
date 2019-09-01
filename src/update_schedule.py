""" imports for GCS """
# coding=utf-8

from __future__ import print_function  # python3
import os
import json  # to parse URL
import urllib2  # to fetch URL
import datetime  # to compose URL
import sys # for get_size
from jsondiff import diff  # to show difference between json content

import cloudstorage as gcs
import webapp2  # pylint: disable=import-error

from google.appengine.api import app_identity  # pylint: disable=import-error
from google.appengine.api import mail  # pylint: disable=import-error

DEBUG = True


class MainPage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    def get(self):
        """This get() calls the other functions for some reason(tm)."""

        bucket_name = os.environ.get(
            "BUCKET_NAME", app_identity.get_default_gcs_bucket_name()
        )

        self.response.headers["Content-Type"] = "text/plain"
        self.response.write(
            "Wtangy AppEngine GCS running from Version: "
            + os.environ["CURRENT_VERSION_ID"]
            + "\n"
        )

        version = os.environ["CURRENT_VERSION_ID"].split(".")[0]
        bucket = "/" + bucket_name
        if version == "None":
            filename = bucket + "/schedule"
            updated_filename = bucket + "/updated_schedule"
        else:
            filename = bucket + "/schedule_" + version
            updated_filename = bucket + "/updated_schedule_" + version

        self.response.write("Using object: " + filename + "\n\n")

        # This _etag is currently unused, could be used to reduce writes to
        #  only when the schedule is updated (and to notify of updates)
        try:
            filename_etag = self.stat_file(filename).etag
            if DEBUG:
                self.response.write("etag: %s \n" % filename_etag)
        except gcs.NotFoundError:
            if DEBUG:
                print("P1")

        [totalgames, jsondata] = self.fetch_upstream_schedule(URL)

        if totalgames == 0:
            pass
        else:
            self.response.write("Total Games: %s\n" % totalgames)
            [teamdates] = self.parse_schedule(jsondata)
            content = self.make_data_json(teamdates)
            try:
                old_content = self.read_file(filename)
            except gcs.NotFoundError:
                self.create_file(filename, content)
                old_content = self.read_file(filename)
            if old_content == content:
                try:
                    last_updated = self.read_file(updated_filename)
                    self.response.write("Not updating schedule - it is current.\n")
                except gcs.NotFoundError:
                    self.create_file(updated_filename, FOR_UPDATED)
                    last_updated = self.read_file(updated_filename)
                self.response.write("Last updated: %s\n" % last_updated)
            else:
                print(
                    "Changes: %s" % (diff(json.loads(old_content), json.loads(content)))
                )
                self.response.write(
                    "Diff: %s\n" % diff(json.loads(old_content), json.loads(content))
                )
                self.create_file(filename, content)
                self.create_file(updated_filename, FOR_UPDATED)
                # Only send e-mails outside playoffs
                #  (potential spoilers - games are removed from the schedule)
                if CURRENT_MONTH < 4 or CURRENT_MONTH > 6:
                    self.send_an_email(
                        diff(json.loads(old_content), json.loads(content)), True
                    )
                self.response.set_status(202)

    def create_file(self, filename, content):
        """Create a file."""

        self.response.write("Creating file {}\n".format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        with gcs.open(
            filename,
            "w",
            content_type="application/json",
            options={"x-goog-acl": "project-private", "x-goog-meta-type": "schedule"},
            retry_params=write_retry_params,
        ) as cloudstorage_file:
            cloudstorage_file.write(content)

    @classmethod
    def stat_file(cls, filename):
        """ stat a file
        This returns a CLASS, fetch properties in the results with var.id, not var['id']
        """
        stat = gcs.stat(filename)
        return stat

    def fetch_upstream_schedule(self, url):
        """ geturl a file and do some health checking
        """

        page = urllib2.urlopen(url)
        jsondata = json.loads(page.read())
        totalgames = jsondata["totalGames"]

        if totalgames == 0:
            self.response.write("ERROR parsing data, 0 games found")
            self.response.set_status(500)
            return (totalgames, False)
        return (totalgames, jsondata)

    @classmethod
    def parse_schedule(cls, jsondata):
        """ parse the json data into a dict the app is used to.
            as a bonus we also sort things
        """

        dict_of_keys_and_matchups = {}
        dict_of_keys_and_matchups_s = {}

        dates = jsondata["dates"]
        for key in dates:
            date = key["date"]
            dict_of_keys_and_matchups[date] = []
            games = key["games"]
            for game in games:
                twoteams = []
                teams = game["teams"]
                # sorry, you can't query montre(withaccent)alcanadiens, all the hard coded bits in the main parser
                #  wasthereannhlgamelastnight.py has MTL without the acute accent
                # without the encode('utf-8') the replace of a unicode gives a unicode error
                # Silmarillionly, mainparser has St Louis Blues, not St. Louis Blues as in the NHL schema
                twoteams.append(teams["away"]["team"]["name"].encode('utf-8').replace('Montr\xc3\xa9al', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
                twoteams.append(teams["home"]["team"]["name"].encode('utf-8').replace('Montr\xc3\xa9al', 'Montreal').replace('St. Louis Blues', 'St Louis Blues'))
                twoteams_sorted = sorted(twoteams)
                dict_of_keys_and_matchups[date].append(twoteams_sorted)
                dict_of_keys_and_matchups_s[date] = sorted(
                    dict_of_keys_and_matchups[date]
                )

        return [dict_of_keys_and_matchups_s]

    @classmethod
    def make_data_json(cls, teamdates):
        """ turn parsed data into json, end result in JSON should look like:
        {
         "teamdates": { "2017-12-30": [["Boston Bruins", "Ottawa Senators"]], }
        }
        """
        data = {}
        data["teamdates"] = teamdates
        json_data = json.dumps(data, sort_keys=True)

        return json_data

    @classmethod
    def read_file(cls, filename):
        """ read and return a file! """

        with gcs.open(filename) as cloudstorage_file:
            read1 = cloudstorage_file.readline()
            cloudstorage_file.read()
            return read1

    @classmethod
    def get_size(cls, obj, seen=None):
        """Recursively finds size of objects
        https://goshippo.com/blog/measure-real-size-any-python-object/

        >>> get_size({ "hello": [2,3,[1,2,[2,3]]] })
        674
        >>> get_size({ "hello": [2,3,[1,2,[2,3]]], "hello2": [2,3,4,5] })
        869
        >>> get_size({})
        280
        """
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([cls.get_size(v, seen) for v in obj.values()])
            size += sum([cls.get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += cls.get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([cls.get_size(i, seen) for i in obj])
        return size


    @classmethod
    def send_an_email(cls, message, admin=False):
        """ send an e-mail, optionally to the admin """
        # https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.mail

        sender_address = "{}@appspot.gserviceaccount.com".format(
            app_identity.get_application_id()
        )

        to_email = os.environ["USER_EMAIL"]
        to_name = to_email

        real_message = message
        msgsize = cls.get_size(real_message)
        # size of 2019-2020 schedule was 530016, unclear how large the jsondiff was 2018->2019
        #  50000 is less than 65490 which was in the log of the update
        #  if we change all "Rangers" to "Freeezers" the changes to restore 2019-2020 was 106288
        if msgsize > 150000:
            real_message = "Msgsize is %s, see /get_schedule - Hello new season?" % msgsize

        if admin or to_email is None or to_email == "":
            mail.send_mail_to_admins(
                sender=sender_address,
                subject="NHL schedule changed A",
                body="msgsize: %s \n changes: %s" % (msgsize, real_message),
            )
        else:
            mail.send_mail(
                sender=sender_address,
                to="%s <%s>" % (to_name, to_email),
                subject="NHL schedule changed",
                body="msgsize: %s \n changes: %s" % (msgsize, real_message),
            )

###### Define some variables used to compose a URL

NOW = datetime.datetime.now()
FOR_UPDATED = str(NOW.isoformat())
[CURRENT_MONTH, CURRENT_YEAR] = NOW.month, NOW.year
LAST_YEAR = CURRENT_YEAR - 1
NEXT_YEAR = CURRENT_YEAR + 1
# if now is before August we get last year from September until July
if CURRENT_MONTH < 8:
    START_DATE = "%s-09-01" % LAST_YEAR
    END_DATE = "%s-07-01" % CURRENT_YEAR
# if now is in or after August we get this year from September until July
else:
    START_DATE = "%s-09-01" % CURRENT_YEAR
    END_DATE = "%s-07-01" % NEXT_YEAR

URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s" % (
    START_DATE,
    END_DATE,
)  # pylint: disable=line-too-long

########## This variable is referenced from app.yaml

APPLICATION = webapp2.WSGIApplication([("/.*", MainPage)], debug=True)
