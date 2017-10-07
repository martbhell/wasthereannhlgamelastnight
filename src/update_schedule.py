# imports for GCS

import logging
import os
import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

# for NHL parsing
import json # to parse URL
import urllib2 # to fetch URL
import datetime # to compose URL

debug = True

# plan:
# one, read/list file in the bucket in google cloud storage, grab checksum of file
# two, run the parser (fetch upstream schedule, parse it). We could move the parser into this file or even better import it
#  - moved it into this file, needed some modifications anyway
# three, write the nhl schedule to a tempfile, calculate checksum
# four, only if checksum is different than the existing one, write to bucket
#  - skip four - is there a way to calculate etag? or then have to fetch file, calculate md5sum. Also have to write the JSON so that it's sorted
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

    bucket = '/' + bucket_name
    filename = bucket + '/schedule'

    # This _etag is currently unused, could be used to reduce writes to only when the schedule is updated
    #  (and to notify of updates)
    try:
        filename_etag = self.stat_file(filename).etag
        if debug: self.response.write("etag: %s \n" % filename_etag)
    except gcs.NotFoundError:
        if debug: print "P1"
        pass

    # composing a URL 
    now = datetime.datetime.now()
    [ current_month, current_year ] = now.month, now.year
    last_year = current_year - 1
    next_year = current_year + 1
    # if now is before August we get last year from September until July
    if current_month < 8:
      start_date = "%s-09-01" % last_year
      end_date = "%s-07-01" % current_year
    # if now is in or after August we get this year from September until July
    else:
      start_date = "%s-09-01" % current_year
      end_date = "%s-07-01" % next_year

    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate=%s&endDate=%s' % (start_date, end_date)
    [ totalGames, jsondata ] = self.fetch_upstream_schedule(url)

    if totalGames == 0:
      pass
    else:
      self.response.write("Total Games: %s\n" % totalGames)
      [ datelist, teamdates ] = self.parse_schedule(jsondata)
      content = self.make_data_json(datelist,teamdates)
      self.create_file(filename, content)
      if debug: self.read_file(filename)

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
  
  def stat_file(self, filename):
      """ stat a file
      This returns a CLASS, fetch properties in the results with var.id, not var['id']
      """
      stat = gcs.stat(filename)

      return(stat)

  def fetch_upstream_schedule(self, url):
      """ geturl a file and do some health checking
      """

      page = urllib2.urlopen(url)
      jsondata = json.loads(page.read())
      totalGames = jsondata['totalGames']

      if totalGames == 0:
          self.response.write('ERROR parsing data, 0 games found')
          self.response.set_status(500)
	  return(totalGames, False)

      else:
          return(totalGames,jsondata)

  def parse_schedule(self, jsondata):
      """ parse the json data into set(list) and dict the app is used to. """

      dict_of_keys_and_matchups = {}
      list_of_dates = []      

      dates = jsondata['dates']
      for key in dates:
        date = key['date']
        dict_of_keys_and_matchups[date] = []
        list_of_dates.append(date)
        games = key['games']
        for game in games:
          twoteams = []
          teams = game['teams']
          twoteams.append(teams['away']['team']['name'])
          twoteams.append(teams['home']['team']['name'])
          dict_of_keys_and_matchups[date].append(twoteams)

      return([set(list_of_dates), dict_of_keys_and_matchups])

  def make_data_json(self, lines, teamdates):
      """ turn parsed data into json, end result in JSON should look like:
      {
       "dates": [ "2017-10-08", "2017-10-09" ],
       "teamdates": { "2017-12-30": [["Boston Bruins", "Ottawa Senators"]], "2017-12-21": [["Boston Bruins", "Ottawa Senators"]] }
      }
      """
      data = {}
      data['dates'] = list(lines) # can't be a set
      data['teamdates'] = teamdates
      json_data = json.dumps(data)

      return(json_data)


  def read_file(self, filename):
    self.response.write(
        'Abbreviated file content (first line and last 1K):\n')

    with gcs.open(filename) as cloudstorage_file:
        self.response.write(cloudstorage_file.readline())
        self.response.write(cloudstorage_file.read())

application = webapp2.WSGIApplication([('/.*', MainPage)],
                                      debug=True)
