#!/usr/bin/env python
import json
import gzip
import tweepy

import django.dispatch

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

tweet_retrieved = django.dispatch.Signal(providing_args=["tweet"])

class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        decoded = json.loads(data)
        tweet_retrieved.send(sender=self.__class__, tweet=decoded)

def stream():
    stream = tweepy.streaming.Stream(auth, StdOutListener())
    stream.filter(locations=[116.87,5.62,128.44,19.68], languages=['en'])
