#!/usr/bin/env python
import json
import gzip
import tweepy

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

class StdOutListener(tweepy.StreamListener):
	def on_data(self, data):
		decoded = json.loads(data)
		try:
			f = gzip.open('happydata.txt.gz', 'a')
			f.write(json.dumps(decoded) + '\n')
		except Exception, e:
			print 'error opening file ' + str(e)
			print decoded['text']
		finally:
			f.close()

	def on_error(self, status):
		print 'error:' + str(status)

stream = tweepy.streaming.Stream(auth, StdOutListener())
stream.filter(locations=[116.87,5.62,128.44,19.68], languages=['en'])
