import json
import random

from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404

from classifier.classifier import train_db, feature_extractor_lda_tripadvisor_top_words_weights
from models import Tweet
from sentiment_analyzer.sentiment_analyzer import train, feature_extractor

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
            tweet.retrieved = True
            tweet.save()
        return HttpResponse(json.dumps(tweets_list))


class TestTweetsView(TemplateView):
    template_name = 'phtweetmap/test.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TestTweetsView, self).get_context_data(*args, **kwargs)
        # train
        tweets_train_tourism = Tweet.objects.filter(classified=True, actual_classification='tourism')
        tweets_train_nontourism = Tweet.objects.filter(classified=True, actual_classification='nontourism')
        train_result = train_db(tweets_train_tourism, tweets_train_nontourism)
        classifier = train_result['classifier']
        context['accuracy'] = train_result['accuracy']
        context['fscore'] = train_result['fscore']
        # test
        tweets = self.randomize_tweets('classifier/data/2015-03-06.happydata.txt', 1)
        tweets_test = []
        for tweet in tweets:
            if not Tweet.objects.filter(tweet_id=tweet['id']) and tweet['coordinates']:
                tweet_id = tweet['id']
                user = tweet['user']['name'].encode('utf-8')
                lat = tweet['coordinates']['coordinates'][1]
                lng = tweet['coordinates']['coordinates'][0]
                text = tweet['text'].encode('utf-8')
                if tweet_id and user and lat and lng and text:
                    classification = classifier.classify(feature_extractor_lda_tripadvisor_top_words_weights(text))
                    tweet_obj = Tweet(tweet_id=tweet_id, user=user,
                                                     lat=lat, lng=lng, text=text, 
                                                     classification=classification)
                    tweet_obj.save()
                    tweets_test.append(tweet_obj)
        context['tweets'] = tweets_test
        return context

    def randomize_tweets(self, filename, lines):
        with open(filename, 'r') as tweets_file:
            tweets = []
            i = 0
            for tweet in tweets_file:
                if i < lines:
                    tweets.append(json.loads(tweet))
                else:
                    j = random.randrange(i)
                    if j < lines:
                        tweets[j] = json.loads(tweet)
                i += 1
            return tweets


class SetClassificationView(View):
    def get(self, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=kwargs['pk'])
        tweet.delete()
        return HttpResponse('')
    # def get(self, *args, **kwargs):
    #     tweet = get_object_or_404(Tweet, pk=kwargs['pk'])
    #     actual_classification = kwargs['actual_classification']
    #     if actual_classification == 'tourism-act':
    #         actual_classification = 'tourism'
    #     else:
    #         actual_classification = 'nontourism'
    #     tweet.actual_classification = actual_classification
    #     tweet.classified = True
    #     tweet.save()
    #     return HttpResponse('')
    # def get(self, *args, **kwargs):
    #     tweet = get_object_or_404(Tweet, pk=kwargs['pk'])
    #     actual_classification = kwargs['actual_classification']
    #     if actual_classification == 'tourism-act':
    #         actual_classification = 'tourism'
    #         tweet.actual_classification = actual_classification
    #         tweet.classified = True
    #         tweet.save()
    #     else:
    #         tweet.delete()
    #     return HttpResponse('')


class TestSystemView(TemplateView):
    template_name = 'phtweetmap/test_system.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TestSystemView, self).get_context_data(*args, **kwargs)
        # train
        tweets_train_tourism = Tweet.objects.filter(classified=True, actual_classification='tourism')
        tweets_train_nontourism = Tweet.objects.filter(classified=True, actual_classification='nontourism')
        
        train_result = train_db(tweets_train_tourism, tweets_train_nontourism)
        classifier = train_result['classifier']
        context['accuracy'] = train_result['accuracy']
        context['fscore'] = train_result['fscore']

        train_sentiment_result = train()
        sentiment_analyzer = train_sentiment_result['classifier']
        context['accuracy_sentiment'] = train_sentiment_result['accuracy']
        context['fscore_sentiment'] = train_sentiment_result['fscore']

        # test
        tweets = []
        with open('classifier/system_tourism.txt', 'r') as tweets_file:
            for tweet in tweets_file:
                tweets.append(tweet)
        with open('classifier/system_nontourism.txt', 'r') as tweets_file:
            for tweet in tweets_file:
                tweets.append(tweet)
        random.shuffle(tweets)

        tweet_dict = {}
        for tweet in tweets:
            classification = classifier.classify(feature_extractor_lda_tripadvisor_top_words_weights(tweet))
            if classification == 'tourism':
                classification = sentiment_analyzer.classify(feature_extractor(tweet))
            tweet_dict[tweet] = classification

        context['tweets'] = tweet_dict
        return context