""" imports for GCS """

import os
import json # to parse URL
import urllib2 # to fetch URL
import datetime # to compose URL

import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

DEBUG = True

class MainPage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    def get(self):

        """This get() calls the other functions for some reason(tm)."""

        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())

        version = os.environ['CURRENT_VERSION_ID'].split('.')[0]
        if version == "None":
            version = "master"

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Demo GCS Application running from Version: '
                            + os.environ['CURRENT_VERSION_ID'] + '\n')
        self.response.write('Using bucket name: ' + bucket_name + '\n\n')

        bucket = '/' + bucket_name
        filename = bucket + '/schedule_' + version

        self.read_file(filename)

    def stat_file(self, filename):
        """ stat a file
        This returns a CLASS, fetch properties in the results with var.id, not var['id']
        """
        stat = gcs.stat(filename)
        return stat

    def read_file(self, filename):
        """ read a file! """


        with gcs.open(filename) as cloudstorage_file:
            content = cloudstorage_file.read()
            parsed = json.loads(content)
            self.response.write(json.dumps(parsed, indent=4, sort_keys=True))

########## This variable is referenced from app.yaml

APPLICATION = webapp2.WSGIApplication([('/.*', MainPage)],
                                      debug=True)
