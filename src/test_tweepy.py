""" Test tweeting with tweepy """

import os
import tweepy

api_key = os.environ["API_KEY"]
api_secret_key = os.environ["API_SECRET_KEY"]
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

# Authenticate to Twitter
auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

# Create a tweet
# msgsize: 1577
#  changes: {u'teamdates': {u'2019-09-29': {delete: [2]}}}
# if msgsize > 1600:
#    api.update_status(real_message)
# else:
api.update_status(
    "Testing https://wtangy.se - did your team play last night? Try out https://wtangy.se/DETROIT"
)
