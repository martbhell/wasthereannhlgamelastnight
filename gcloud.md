Backend / Development notes
===========================

https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu

because I forget:

<pre>
gcloud app deploy cron.yaml # deploy the cron to update gs:/bucket/schedule which is a JSON
gcloud app deploy -v master # name the version rather than dynamic to not hit the limit
</pre>

debugging / development (set debug = True in wasthereannhlgamelastnight.py first ):

<pre>
sudo apt-get install google-cloud-sdk-app-engine-python

/usr/lib/google-cloud-sdk/bin/dev_appserver.py

curl http://localhost:8080
</pre>

maybe the cloudstorage library in lib/ shouldn't/doesn't have to be in here?
