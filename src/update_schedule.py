""" imports for GCS """

import os
import json # to parse URL
import urllib2 # to fetch URL
import datetime # to compose URL
from jsondiff import diff # to show difference between json content pylint: disable=import-error

import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import mail

DEBUG = True

class MainPage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    def get(self):
        """This get() calls the other functions for some reason(tm)."""

        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Demo GCS Application running from Version: '
                            + os.environ['CURRENT_VERSION_ID'] + '\n')
        self.response.write('Using bucket name: ' + bucket_name + '\n\n')

        version = os.environ['CURRENT_VERSION_ID'].split('.')[0]
        bucket = '/' + bucket_name
        if version == "None":
            filename = bucket + '/schedule'
            updated_filename = bucket + '/updated_schedule'
        else:
            filename = bucket + '/schedule_' + version
            updated_filename = bucket + '/updated_schedule_' + version

        # This _etag is currently unused, could be used to reduce writes to
        #  only when the schedule is updated (and to notify of updates)
        try:
            filename_etag = self.stat_file(filename).etag
            if DEBUG:
                self.response.write("etag: %s \n" % filename_etag)
        except gcs.NotFoundError:
            if DEBUG:
                print "P1"

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
                    self.response.write('Not updating schedule - it is current.\n')
                except gcs.NotFoundError:
                    self.create_file(updated_filename, FOR_UPDATED)
                    last_updated = self.read_file(updated_filename)
                self.response.write("Last updated: %s\n" % last_updated)
            else:
                print "Changes: %s" % (diff(json.loads(old_content), json.loads(content)))
                self.response.write("Diff: %s" % diff(json.loads(old_content), json.loads(content)))
                self.create_file(filename, content)
                self.create_file(updated_filename, FOR_UPDATED)
                # Only send e-mails outside playoffs
                #  (potential spoilers - games are removed from the schedule)
                if CURRENT_MONTH < 4 and CURRENT_MONTH > 6:
                    self.send_an_email(diff(json.loads(old_content), json.loads(content)), True)

    def create_file(self, filename, content):
        """Create a file."""

        self.response.write('Creating file {}\n'.format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        with gcs.open(
            filename, 'w', content_type='application/json', options={
                'x-goog-acl': 'project-private', 'x-goog-meta-type': 'schedule'},
            retry_params=write_retry_params) as cloudstorage_file:
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
        totalgames = jsondata['totalGames']

        if totalgames == 0:
            self.response.write('ERROR parsing data, 0 games found')
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

        dates = jsondata['dates']
        for key in dates:
            date = key['date']
            dict_of_keys_and_matchups[date] = []
            games = key['games']
            for game in games:
                twoteams = []
                teams = game['teams']
                twoteams.append(teams['away']['team']['name'])
                twoteams.append(teams['home']['team']['name'])
                twoteams_sorted = sorted(twoteams)
                dict_of_keys_and_matchups[date].append(twoteams_sorted)
                dict_of_keys_and_matchups_s[date] = sorted(dict_of_keys_and_matchups[date])

        return [dict_of_keys_and_matchups_s]

    @classmethod
    def make_data_json(cls, teamdates):
        """ turn parsed data into json, end result in JSON should look like:
        {
         "teamdates": { "2017-12-30": [["Boston Bruins", "Ottawa Senators"]], }
        }
        """
        data = {}
        data['teamdates'] = teamdates
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
    def send_an_email(cls, message, admin=False):
        """ send an e-mail, optionally to the admin """
        #https://cloud.google.com/appengine/docs/standard/python/refdocs/google.appengine.api.mail

        sender_address = '{}@appspot.gserviceaccount.com'.format(app_identity.get_application_id())

        to_email = os.environ['USER_EMAIL']
        to_name = to_email

        if admin or to_email is None or to_email == "":
            mail.send_mail_to_admins(sender=sender_address,
                                     subject="NHL schedule changed A",
                                     body="changes: %s" % (message))
        else:
            mail.send_mail(sender=sender_address,
                           to="%s <%s>" % (to_name, to_email),
                           subject="NHL schedule changed",
                           body="changes: %s" % (message))

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

URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s" % (START_DATE, END_DATE) # pylint: disable=line-too-long

########## This variable is referenced from app.yaml

APPLICATION = webapp2.WSGIApplication([('/.*', MainPage)],
                                      debug=True)
