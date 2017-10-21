""" imports for GCS """

import os
import json # to parse URL
import urllib2 # to fetch URL
import datetime # to compose URL

import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

DEBUG = True

# plan:
# one, read/list file in the bucket in google cloud storage, grab checksum of file
# two, run the parser (fetch upstream schedule, parse it). We could move the
#  parser into this file or even better import it
#  - moved it into this file, needed some modifications anyway
# three, write the nhl schedule to a tempfile, calculate checksum
# four, only if checksum is different than the existing one, write to bucket
#  - skip four - is there a way to calculate etag? or then have to fetch file,
#    calculate md5sum. Also have to write the JSON so that it's sorted
# five, remove tempfiles
#  - not using any tempfiles

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
        else:
            filename = bucket + '/schedule_' + version

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
            self.create_file(filename, content)
            if DEBUG:
                self.read_file(filename)

    def create_file(self, filename, content):
        """Create a file."""

        self.response.write('Creating file {}\n'.format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        with gcs.open(
            filename, 'w', content_type='application/json', options={
                'x-goog-acl': 'private', 'x-goog-meta-type': 'schedule'},
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
        """ parse the json data into a dict the app is used to. """

        dict_of_keys_and_matchups = {}

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
                dict_of_keys_and_matchups[date].append(twoteams)

        return [dict_of_keys_and_matchups]

    @classmethod
    def make_data_json(cls, teamdates):
        """ turn parsed data into json, end result in JSON should look like:
        {
         "teamdates": { "2017-12-30": [["Boston Bruins", "Ottawa Senators"]], }
        }
        """
        data = {}
        data['teamdates'] = teamdates
        json_data = json.dumps(data)

        return json_data


    def read_file(self, filename):
        """ read a file! """

        self.response.write(
            'Abbreviated file content (first line and last 1K):\n')

        with gcs.open(filename) as cloudstorage_file:
            self.response.write(cloudstorage_file.readline())
            self.response.write(cloudstorage_file.read())

###### Define some variables used to compose a URL

NOW = datetime.datetime.now()
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
