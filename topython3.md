 - https://codelabs.developers.google.com/codelabs/cloud-gae-python-migrate-1-flask#3

 - remove /lib
 - add flask to requirements
 - new libs to access google cloud storage - https://cloud.google.com/appengine/docs/standard/python3/using-cloud-storage
 - pip3 install -t lib -r requirements.txt
 - then we change webapp2 with Flask

 - make a new main.py and add decorators
   - maybe use http://exploreflask.com/en/latest/views.html to get vars nicely out of urls
   - and stop allowing wtangy.se/DETROIT/20220104 and /20220104/DETROIT at the same time
