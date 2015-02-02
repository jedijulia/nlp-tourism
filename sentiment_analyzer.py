#!/usr/bin/env python
from operator import itemgetter
import random
import re

from nltk.corpus import stopwords

from sklearn import cross_validation

def clean(tweet):
    clean = re.sub(r'https?:\/\/\w+(\.\w+)*(:\w+)?(/[A-Za-z0-9-_\.]*)* ?', '', tweet)
    return clean

def process_data(positive_file, negative_file):
    datamixed = [(clean(tweet), 'positive') for tweet in positive_file]
    datamixed += [(clean(tweet), 'negative') for tweet in negative_file]
    random.shuffle(datamixed)

    feature_set = [(feature_extractor_top_words_weights(tweet), label) for (tweet, label) in datamixed]
    size = int(len(feature_set) * 0.8)
    training_set = feature_set[:size]
    test_set = feature_set[size:]
    return [feature_set, training_set, test_set, datamixed, size]

def get_fscore(classifier, data):
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    for(tweet, label) in data:
        guess = classifier.classify(tweet)
        if guess == 'positive' and label == 'positive':
            true_positives += 1
        elif guess == 'positive' and label == 'negative':
            false_positives += 1
        elif guess == 'negative' and label == 'negative':
            true_negatives += 1
        else:
            false_negatives += 1

    precision = 0
    recall = 0
    fscore = 0

    if (true_positives + false_positives) != 0:
        precision = (true_positives * 1.0) / (true_positives + false_positives)
    if (true_positives + false_negatives) != 0:
        recall = (true_positives * 1.0) / (true_positives + false_negatives)
    if (precision + recall) != 0:
        fscore = 2 * (precision * recall) / (precision + recall)

    print 'Precision: ' + str(precision)
    print 'Recall: ' + str(recall)
    print 'F-score: ' + str(fscore)
    return fscore

# 10-fold cross validation
def cross_validate(classifier, training_set, test_set):
    chosen_classif = classifier
    if chosen_classif == classifier_logreg:
        is_logreg = True 
    else:
        is_logreg = False
    best_accuracy = 0.0
    best_train_accuracy = None
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
        train_accuracy = classify.accuracy(classifier, train)
        print 'Training set accuracy:' + str(train_accuracy)
        if len(test_indices) == 1:
            test = (test,)
        accuracy = classify.accuracy(classifier, test)
        if accuracy > best_accuracy:
            best_classifier = classifier
            best_accuracy = accuracy
            best_train_accuracy = train_accuracy
        print 'Cross validation set accuracy: ' + str(accuracy)
        get_fscore(classifier, test)
    print 'Best classifier CV accuracy: ' + str(best_accuracy)
    test_accuracy = classify.accuracy(best_classifier, test_set)
    print 'Best classifier accuracy: ' + str(test_accuracy)
    print 'Best classifier precision recall fscore: '
    print get_fscore(best_classifier, test_set)
    return [test_accuracy, best_train_accuracy, best_classifier]

# get data from files
tourism_file = open('positive.txt', 'r')
nontourism_file = open('negative.txt', 'r')

# retrieve features
data_set = process_data(tourism_file, nontourism_file)
feature_set = data_set[0]
training_set = data_set[1]
test_set = data_set[2]

print 'training set size: ' + str(len(training_set))
print 'test set size: ' + str(len(test_set))
