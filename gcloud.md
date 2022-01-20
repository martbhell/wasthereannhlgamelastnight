Backend / Development notes
===========================

https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu

because I forget:

not keeping the testing instance running when it's not necessary, for manual development:
<pre>
gcloud init ## to change to wtangy project
# recreate testing instance? see .travis.yml
gcloud app deploy -v testing --no-promote
# 
</pre>
and just deploying
<pre>
gcloud app deploy cron.yaml # deploy the cron to update gs:/bucket/schedule which is a JSON
gcloud app deploy -v master # name the version rather than dynamic to not hit the limit
</pre>

debugging / development (set debug = True in wasthereannhlgamelastnight.py or update_schedule.py first ):

<pre>
sudo apt-get install google-cloud-sdk-app-engine-python

/usr/lib/google-cloud-sdk/bin/dev_appserver.py

# or like this to bind to an IP and port you can reach from outside WSL
$ dev_appserver.py app.yaml --host ip_from_wsl --port=9999

curl http://localhost:8080
</pre>

maybe the cloudstorage library in lib/ shouldn't/doesn't have to be in here?

## This has been gold for setting up travis:

https://github.com/GoogleCloudPlatform/continuous-deployment-demo

not all is relevant anymore or has changed, but do pay attention to:
 - gcloud config set project $name
## Twitter

Create these files in the bucket

  - API_KEY.TXT
  - API_SECRET_KEY.TXT
  - ACCESS_TOKEN.TXT
  - ACCESS_SECRET_TOKEN.TXT

https://cloud.google.com/appengine/docs/standard/python3/configuration-files does not mention includes: 

Googling told me using GCS or one could even play with Google KMS https://cloud.google.com/security-key-management for extra Fun!

Files created in GCS with names "API_KEY.TXT" and that specific file extensions turns them into "text/plain" content type. Make sure you create the files like `echo -n SECRET > API_KEY.TXT` or you might end up with newlines in the file.

To test the notifications:
- download the schedule
- modify it
- upload it
- run /update_schedule

Or use test_tweepy.py and set bash environment variables
