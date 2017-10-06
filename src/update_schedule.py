import logging
import os
import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

# let's update the schedule!

class MainPage(webapp2.RequestHandler):
  """Main page for GCS demo application."""

  def get(self):
    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())
  
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
    self.response.write('Using bucket name: ' + bucket_name + '\n\n')
  

app = webapp2.WSGIApplication([('/', MainPage)],
                                      debug=True)
