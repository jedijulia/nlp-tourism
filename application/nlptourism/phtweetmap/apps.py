from django.apps import AppConfig
from django.dispatch import receiver

from classifier.classifier import train, feature_extractor_lda_tripadvisor_top_words_weights
import streamer

class PhtweetmapAppConfig(AppConfig):
    name = 'phtweetmap'
    verbose_name = "Philippine Tourism Tweet Map"
    flag = False
    def ready(self):
        classif = train()
        @receiver(streamer.tweet_retrieved)
        def my_callback(sender, **kwargs):
            tweet = kwargs['tweet']['text'].encode('utf-8')
            label = classif.classify(feature_extractor_lda_tripadvisor_top_words_weights(tweet))
            print 'Label: {} || Tweet: {}'.format(label, tweet)
        streamer.stream()