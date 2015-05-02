from django.apps import AppConfig
from django.dispatch import receiver

import streamer

class PhtweetmapAppConfig(AppConfig):
    name = 'phtweetmap'
    verbose_name = "Philippine Tourism Tweet Map"
    flag = False
    def ready(self):
        @receiver(streamer.tweet_retrieved)
        def my_callback(sender, **kwargs):
            print kwargs['tweet']
        streamer.stream()