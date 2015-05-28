"""
 Celery task for streaming tweets, labeling and storing them
"""
from __future__ import absolute_import

from celery import shared_task
from django.dispatch import receiver

from classifier.classifier import train, feature_extractor_lda_tripadvisor_top_words_weights
from phtweetmap.models import Tweet
from sentiment_analyzer.sentiment_analyzer import train, feature_extractor
import streamer

# stream tweets
@shared_task
def retrieve_tweets():
    classif = train()
    # called when a new tweets is retrieved from streaming
    @receiver(streamer.tweet_retrieved)
    def my_callback(sender, **kwargs):
        tweet = kwargs['tweet']
        if tweet['coordinates']:
            tweet_id = tweet['id']
            user = tweet['user']['name'].encode('utf-8')
            lat = tweet['coordinates']['coordinates'][1]
            lng = tweet['coordinates']['coordinates'][0]
            text = tweet['text'].encode('utf-8') 
            if tweet_id and user and lat and lng and text:
                # classify tweets (tourism or nontourism)
                classification = classif.classify(feature_extractor_lda_tripadvisor_top_words_weights(text))
                # for tourism-related tweets, classify as being positive or negative
                if classification == 'tourism'
                    sentiment = sentiment_analyzer.classify(feature_extractor(tweet))
                    print 'Label: {} || Tweet: {}'.format(sentiment, text)
                    # create Tweet object and save to db
                    tweet_obj = Tweet.objects.create(tweet_id=tweet_id, user=user,
                                                     lat=lat, lng=lng, text=text,
                                                     classification=classification, 
                                                     sentiment=sentiment)
                    tweet_obj.save()
    # call streamer
    streamer.stream()
    return None