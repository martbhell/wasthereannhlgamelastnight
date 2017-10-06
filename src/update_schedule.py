import logging
import os
import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

# plan:
# one, read/list file in the bucket in google cloud storage, grab checksum of file
# two, run the parser (fetch upstream schedule, parse it). We could move the parser into this file or even better import it
# three, write the nhl schedule to a tempfile, calculate checksum
# four, only if checksum is different than the existing one, write to bucket
# five, remove tempfile

class MainPage(webapp2.RequestHandler):
  """Main page for GCS demo application."""

  def get(self):
    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())
  
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
    self.response.write('Using bucket name: ' + bucket_name + '\n\n')
  

application = webapp2.WSGIApplication([('/.*', MainPage)],
                                      debug=True)
