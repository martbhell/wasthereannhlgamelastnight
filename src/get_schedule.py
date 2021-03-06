""" imports for GCS """

import os
import json

import cloudstorage as gcs
import webapp2  # pylint: disable=import-error

from google.appengine.api import app_identity  # pylint: disable=import-error

DEBUG = False


class GetSchedulePage(webapp2.RequestHandler):
    """Main page for GCS demo application."""

    def get(self):

        """This get() calls the other functions for some reason(tm)."""

        bucket_name = os.environ.get(
            "BUCKET_NAME", app_identity.get_default_gcs_bucket_name()
        )

        bucket = "/" + bucket_name
        version = os.environ["CURRENT_VERSION_ID"].split(".")[0]
        if version == "None":
            filename = bucket + "/schedule"
        else:
            filename = bucket + "/schedule_" + version

        #        if DEBUG:
        #            self.response.write('Demo GCS Application running from Version: '
        #                                + os.environ['CURRENT_VERSION_ID'] + '\n')
        #            self.response.write('Using bucket name: ' + bucket_name + '\n\n')

        self.read_file(filename)

    def read_file(self, filename):
        """ read a file!
            and as a bonus assume content is JSON and return pretty JSON """

        with gcs.open(filename) as cloudstorage_file:
            content = cloudstorage_file.read()
            parsed = json.loads(content)
            self.response.headers["Content-Type"] = "application/json"
            self.response.write(json.dumps(parsed, indent=4, sort_keys=True))


class VersionPage(webapp2.RequestHandler):
    """ Fetch a file and render it."""

    def get(self):
        """ Defines what we do """
        bucket_name = os.environ.get(
            "BUCKET_NAME", app_identity.get_default_gcs_bucket_name()
        )

        bucket = "/" + bucket_name
        version = os.environ["CURRENT_VERSION_ID"].split(".")[0]
        if version == "None":
            filename = bucket + "/updated_schedule"
        else:
            filename = bucket + "/updated_schedule_" + version

        self.read_file(filename)

    def read_file(self, filename):
        """ read a file!
            return it as json!
        """

        with gcs.open(filename) as cloudstorage_file:
            content = {"version": cloudstorage_file.read()}
            # parsed = json.loads(content)
            self.response.headers["Content-Type"] = "application/json"
            # self.response.write(json.dumps(parsed, indent=4, sort_keys=True))
            self.response.write(json.dumps(content))


########## This variable is referenced from app.yaml

GETSCHEDULE = webapp2.WSGIApplication([("/.*", GetSchedulePage)], debug=True)
VERSION = webapp2.WSGIApplication([("/.*", VersionPage)], debug=True)
