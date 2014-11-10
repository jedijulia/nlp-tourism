#!/usr/bin/env python
import random

from nltk import classify, NaiveBayesClassifier, word_tokenize, WordNetLemmatizer
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.corpus import stopwords

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

def feature_extractor(data):
    data = data.decode('utf-8')
    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    for word in words:
        if word not in stop_words:
            features[word] = True

    return features

def process_data(tourism_file, nontourism_file):
    datamixed = [(tweet, 'tourism') for tweet in tourism_file]
    datamixed += [(tweet, 'nontourism') for tweet in nontourism_file]
    random.shuffle(datamixed)

    feature_set = [(feature_extractor(tweet), label) for (tweet, label) in datamixed]
    size = int(len(feature_set) * 0.7)
    training_set = feature_set[:size]
    test_set = feature_set[size:]

    return [training_set, test_set, datamixed, size]


# get data from files
tourism_file = open('tourism.txt', 'r')
nontourism_file = open('nontourism.txt', 'r')

# retrieve features
data_set = process_data(tourism_file, nontourism_file)
training_set = data_set[0]
test_set = data_set[1]
datamixed = data_set[2]
size = data_set[3]

print 'training set size: ' + str(len(training_set))
print 'test set size: ' + str(len(test_set))

# classify
classifier = NaiveBayesClassifier.train(training_set)
classifier_lr = SklearnClassifier(LogisticRegression()).train(training_set)
classifier_svm = SklearnClassifier(LinearSVC()).train(training_set)
print classify.accuracy(classifier, test_set)

# show errors
errors = []
for(tweet, label) in datamixed[size:]:
    guess = classifier.classify(feature_extractor(tweet))
    if guess != label:
        errors.append((label, guess, tweet))

for (label, guess, tweet) in sorted(errors):
  print('correct=%-8s guess=%-8s name=%-30s' % (label, guess, tweet))