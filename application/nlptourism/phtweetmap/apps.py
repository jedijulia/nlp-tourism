from django.apps import AppConfig
from django.dispatch import receiver

from classifier.classifier import train, feature_extractor_lda_tripadvisor_top_words_weights
from models import Tweet
import streamer

class PhtweetmapAppConfig(AppConfig):
    name = 'phtweetmap'
    verbose_name = "Philippine Tourism Tweet Map"
    flag = False
    def ready(self):
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