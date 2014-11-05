#!/usr/bin/env python
import random

from nltk import classify, NaiveBayesClassifier, word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords


def feature_extractor(data):
    data = data.decode('utf-8')
    features = {}
    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    for word in words:
        if word not in stopwords:
            features[word] = True

    return features

tourism_file = open('tourism.txt', 'r')
nontourism_file = open('nontourism.txt', 'r')

datamixed = [(tweet, 'tourism') for tweet in tourism_file]
datamixed += [(tweet, 'nontourism') for tweet in nontourism_file]
random.shuffle(datamixed)

lemmatizer = WordNetLemmatizer()
stopwords = stopwords.words('english')

feature_set = [(feature_extractor(tweet), label) for (tweet, label) in datamixed]
size = int(len(feature_set) * 0.7)
training_set = feature_set[:size]
test_set = feature_set[size:]

print 'training set size: ' + str(len(training_set))
print 'test set size: ' + str(len(test_set))

classifier = NaiveBayesClassifier.train(training_set)

print classify.accuracy(classifier, test_set)