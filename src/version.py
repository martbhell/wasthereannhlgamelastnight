""" imports for GCS """

import os
#import json

import cloudstorage as gcs # pylint: disable=import-error
import webapp2 # pylint: disable=import-error

from google.appengine.api import app_identity # pylint: disable=import-error

DEBUG = False

class MainPage(webapp2.RequestHandler):
    """ Fetch a file and render it."""

    def get(self):

        bucket_name = os.environ.get('BUCKET_NAME',
                                     app_identity.get_default_gcs_bucket_name())

        bucket = '/' + bucket_name
        version = os.environ['CURRENT_VERSION_ID'].split('.')[0]
        if version == "None":
            filename = bucket + '/updated_schedule'
        else:
            filename = bucket + '/updated_schedule_' + version

        self.read_file(filename)

    def read_file(self, filename):
        """ read a file! """

        with gcs.open(filename) as cloudstorage_file:
            content = cloudstorage_file.read()
            #parsed = json.loads(content)
            #self.response.headers['Content-Type'] = 'application/json'
            #self.response.write(json.dumps(parsed, indent=4, sort_keys=True))
            self.response.write(content)

########## This variable is referenced from app.yaml

APPLICATION = webapp2.WSGIApplication([('/.*', MainPage)],
                                      debug=True)
