import json

from django.http import HttpResponse
from django.views.generic import TemplateView, View

from models import Tweet

class IndexView(TemplateView):
    template_name = 'phtweetmap/index.html'


class RetrieveTweetsView(View):
    def get(self, *args, **kwargs):
        tweets = Tweet.objects.filter(retrieved=False)
        tweets_list = []
        for tweet in tweets:
            tweet_json = {
                'tweet_id': tweet.tweet_id,
                'user': tweet.user,
                'lat': float(tweet.lat),
                'lng': float(tweet.lng),
                'text': tweet.text,
                'sentiment': tweet.sentiment
            }
            tweets_list.append(tweet_json)
            tweet.retrieved = False
            tweet.save()
        return HttpResponse(json.dumps(tweets_list))