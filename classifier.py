#!/usr/bin/env python
from operator import itemgetter
import random

from logreg import LogReg

from nltk import classify, NaiveBayesClassifier, word_tokenize, WordNetLemmatizer
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.corpus import stopwords

import numpy as np

from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

def feature_extractor(data):
    data = data.decode('utf-8')
    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    for word in words:
        if word not in stop_words:
            if word in features:
                features[word] += 1
            else:
                features[word] = 1

    return features

def process_data(tourism_file, nontourism_file):
    datamixed = [(tweet, 'tourism') for tweet in tourism_file]
    datamixed += [(tweet, 'nontourism') for tweet in nontourism_file]
    random.shuffle(datamixed)

    feature_set = [(feature_extractor(tweet), label) for (tweet, label) in datamixed]
    size = int(len(feature_set) * 0.8)
    training_set = feature_set[:size]
    test_set = feature_set[size:]

    return [training_set, test_set, datamixed, size, feature_set]

def get_fscore(classifier, data):
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    for(tweet, label) in data:
        guess = classifier.classify(tweet)
        if guess == 'tourism' and label == 'tourism':
            true_positives += 1
        elif guess == 'tourism' and label == 'nontourism':
            false_positives += 1
        elif guess == 'nontourism' and label == 'nontourism':
            true_negatives += 1
        else:
            false_negatives += 1

    precision = (true_positives * 1.0) / (true_positives + false_positives)
    recall = (true_positives * 1.0) / (true_positives + false_negatives)
    if (precision + recall) != 0:
        fscore = 2 * (precision * recall) / (precision + recall)
    else:
        fscore = 0
    print 'Precision: ' + str(precision)
    print 'Recall: ' + str(recall)
    print 'F-score: ' + str(fscore)
    return fscore


# get data from files
tourism_file = open('tourism.txt', 'r')
nontourism_file = open('nontourism.txt', 'r')

# retrieve features
data_set = process_data(tourism_file, nontourism_file)
training_set = data_set[0]
test_set = data_set[1]
datamixed = data_set[2]
size = data_set[3]
feature_set = data_set[4]

print 'training set size: ' + str(len(training_set))
print 'test set size: ' + str(len(test_set))

# classifiers

classifier_nb = NaiveBayesClassifier
classifier_lr = SklearnClassifier(LogisticRegression())
classifier_svm = SklearnClassifier(LinearSVC())
pipeline = Pipeline([('tfidf', TfidfTransformer()),
                     ('nb', MultinomialNB())])
classifier_multinb = SklearnClassifier(pipeline)
classifier_logreg = LogReg


# 10-fold cross validation
chosen_classif = classifier_lr
if chosen_classif == classifier_logreg:
    is_logreg = True 
else:
    is_logreg = False
best_accuracy = 0.0
best_classifier = None
k_fold = cross_validation.KFold(len(training_set), n_folds=10)
for train_indices, test_indices in k_fold:
    if is_logreg:
        chosen_classif = classifier_logreg()
    train = itemgetter(*train_indices)(training_set)
    test = itemgetter(*test_indices)(training_set)
    if is_logreg:
        chosen_classif.train(train)
        classifier = chosen_classif
    else:
        classifier = chosen_classif.train(train)
    print '--------------------------------'
    print 'training set accuracy:' + str(classify.accuracy(classifier, train))
    accuracy = classify.accuracy(classifier, test)
    if accuracy > best_accuracy:
        best_classifier = classifier
        best_accuracy = accuracy
    print 'Cross validation set accuracy: ' + str(accuracy)
    get_fscore(classifier, test)
print 'Best classifier accuracy: ' + str(classify.accuracy(best_classifier, test_set))

# show errors
# errors = []
# ctr = 0
# for(tweet, label) in datamixed[size:]:
#     guess = classifier.classify(feature_extractor(tweet))
#     if guess != label:
#         errors.append((label, guess, tweet))
#     else:
#         ctr += 1 
# print 'number correct: ' + str(ctr)
# for (label, guess, tweet) in sorted(errors):
#   print('correct=%-8s guess=%-8s name=%-30s' % (label, guess, tweet))