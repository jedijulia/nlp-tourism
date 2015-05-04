from __future__ import absolute_import

from celery import shared_task
from django.dispatch import receiver

from classifier.classifier import train, feature_extractor_lda_tripadvisor_top_words_weights
from phtweetmap.models import Tweet
import streamer

@shared_task
def retrieve_tweets():
    classif = train()
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
                # not yet sentiment, just tourism nontourism label, use for testing
                sentiment = classif.classify(feature_extractor_lda_tripadvisor_top_words_weights(text))
                print 'Label: {} || Tweet: {}'.format(sentiment, text)
                tweet_obj = Tweet.objects.create(tweet_id=tweet_id, user=user,
                                                 lat=lat, lng=lng, text=text, 
                                                 sentiment=sentiment)
                tweet_obj.save()
    streamer.stream()
    return None