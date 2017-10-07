import logging
import os
import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

debug = True

# plan:
# one, read/list file in the bucket in google cloud storage, grab checksum of file
# two, run the parser (fetch upstream schedule, parse it). We could move the parser into this file or even better import it
# three, write the nhl schedule to a tempfile, calculate checksum
# four, only if checksum is different than the existing one, write to bucket
# five, remove tempfile

class MainPage(webapp2.RequestHandler):
  """Main page for GCS demo application."""

  def get(self):
    """This get calls the other functions for some reason(tm)."""

    bucket_name = os.environ.get('BUCKET_NAME',
                                 app_identity.get_default_gcs_bucket_name())
  
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Demo GCS Application running from Version: '
                        + os.environ['CURRENT_VERSION_ID'] + '\n')
    self.response.write('Using bucket name: ' + bucket_name + '\n\n')

    bucket = '/' + bucket_name
    filename = bucket + '/schedule'
    self.tmp_filenames_to_clean_up = []

    try:
        filename_etag = self.stat_file(filename).etag
        if debug: self.response.write("etag: %s" % filename_etag)
    except gcs.NotFoundError:
        if debug: print "P1"
        pass

    self.create_file(filename)

  def create_file(self, filename):
      """Create a file."""

      self.response.write('Creating file {}\n'.format(filename))

      # The retry_params specified in the open call will override the default
      # retry params for this particular file handle.
      write_retry_params = gcs.RetryParams(backoff_factor=1.1)
      with gcs.open(
          filename, 'w', content_type='text/plain', options={
              'x-goog-acl': 'private', 'x-goog-meta-type': 'schedule'},
              retry_params=write_retry_params) as cloudstorage_file:
                  cloudstorage_file.write('abcde\n')
                  cloudstorage_file.write('f'*1024*4 + '\n')
      self.tmp_filenames_to_clean_up.append(filename)
  
  def stat_file(self, filename):
      """ stat a file
      This returns a CLASS, fetch properties in the results with var.id, not var['id']
      """
      stat = gcs.stat(filename)

      return(stat)

application = webapp2.WSGIApplication([('/.*', MainPage)],
                                      debug=True)
