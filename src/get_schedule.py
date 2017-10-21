""" imports for GCS """

import os
import json

import cloudstorage as gcs # pylint: disable=import-error
import webapp2 # pylint: disable=import-error

from google.appengine.api import app_identity # pylint: disable=import-error

DEBUG = False

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
        if DEBUG:
            self.response.write('Demo GCS Application running from Version: '
                                + os.environ['CURRENT_VERSION_ID'] + '\n')
            self.response.write('Using bucket name: ' + bucket_name + '\n\n')

        bucket = '/' + bucket_name
        filename = bucket + '/schedule_' + version

        self.read_file(filename)

    def read_file(self, filename):
        """ read a file!
            and as a bonus assume content is JSON and return pretty JSON """

        with gcs.open(filename) as cloudstorage_file:
            content = cloudstorage_file.read()
            parsed = json.loads(content)
            self.response.write(json.dumps(parsed, indent=4, sort_keys=True))

########## This variable is referenced from app.yaml

APPLICATION = webapp2.WSGIApplication([('/.*', MainPage)],
                                      debug=True)
