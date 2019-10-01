Backend / Development notes
===========================

https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu

because I forget:

not keeping the testing instance running when it's not necessary, for manual development:
<pre>
gcloud init ## to change to wtangy project
# recreate testing instance? see .travis.yml
# if deploying to a clean datastore/appengine remember to modify env_variables.yml and upload it manually to the datastore (you'll need to exclude it from .gcloudignore file)
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

curl http://localhost:8080
</pre>

maybe the cloudstorage library in lib/ shouldn't/doesn't have to be in here?

## This has been gold for setting up travis:

https://github.com/GoogleCloudPlatform/continuous-deployment-demo

not all is relevant anymore or has changed, but do pay attention to:
 - gcloud config set project $name
