#!/usr/bin/env python
from operator import itemgetter
import random
import re

from logreg import LogReg

import matplotlib.pyplot as plt

from nltk import classify, NaiveBayesClassifier, word_tokenize, WordNetLemmatizer
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.corpus import stopwords

import numpy as np

from sklearn import cross_validation
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
            if word in features:
                features[word] += 1
            else:
                features[word] = 1

    return features

def feature_extractor_top_words(data):
    data = data.decode('utf-8')
    top_words = ['travel', 'vacation', 'city', 'itsmorefuninthephilippines', 'travel',
                 'boracay', 'philippine', 'view', 'day', 'beach', 'morning', 'resort', 
                 'good', 'cebu', 'island']
    features = {word: 0 for word in top_words}
    lemmatizer = WordNetLemmatizer()

    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    for word in words:
        if word in features:
            features[word] += 1

    return features

def feature_extractor_top_words_weights(data):
    data = data.decode('utf-8')
    top_words = ['travel', 'vacation', 'city', 'itsmorefuninthephilippines', 'travel',
                 'boracay', 'philippine', 'view', 'day', 'beach', 'morning', 'resort', 
                 'good', 'cebu', 'island']
    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    for word in words:
        if word not in stop_words:
            if word in features:
                if word in top_words:
                    features[word] += 1.5
                else:
                    features[word] += 1
            else:
                if word in top_words:
                    features[word] = 1.5
                else:
                    features[word] = 1

    return features

def feature_extractor_tripadvisor_top_words_weights(data):
    data = data.decode('utf-8')

    top_file = open('scraper/top_words.txt', 'r')
    top_words = [word.replace('\n', '') for word in top_file]
    places_file = open('scraper/places.txt', 'r')

    for place in places_file:
        place = place.replace('\n', '')
        for word in place.split(' '):
            if word != '-':
                top_words.append(word)

    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    for word in words:
        if word not in stop_words:
            if word in features:
                if word in top_words:
                    features[word] += 1.5
                else:
                    features[word] += 1
            else:
                if word in top_words:
                    features[word] = 1.5
                else:
                    features[word] = 1

    return features

def clean(tweet):
    clean = re.sub(r'https?:\/\/\w+(\.\w+)*(:\w+)?(/[A-Za-z0-9-_\.]*)* ?', '', tweet)
    clean = re.sub(r'#', '', clean)
    clean = re.sub(r'!', '', clean)
    clean = re.sub(r'\.\.\.', '', clean)
    clean = re.sub(r',', '', clean)
    return clean

def process_data(tourism_file, nontourism_file):
    datamixed = [(clean(tweet), 'tourism') for tweet in tourism_file]
    datamixed += [(clean(tweet), 'nontourism') for tweet in nontourism_file]
    random.shuffle(datamixed)

    feature_set = [(feature_extractor_tripadvisor_top_words_weights(tweet), label) for (tweet, label) in datamixed]
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
classifier_logreg = LogReg

# plot curves
data_size = 20
data_sizes = []
accuracies = []
train_accuracies = []
while data_size <= 600:
    curr_data_set = feature_set[:data_size]
    curr_size = int(len(curr_data_set) * 0.8)
    train = curr_data_set[:curr_size]
    test = curr_data_set[curr_size:]
    accuracy = cross_validate(classifier_svm, train, test) # need to set classifier here, currently svm
    data_sizes.append(data_size)
    accuracies.append(accuracy[0])
    train_accuracies.append(accuracy[1])
    data_size += 50

plt.plot(data_sizes, accuracies)
plt.plot(data_sizes, train_accuracies)
plt.xlabel('Dataset Size')
plt.ylabel('Accuracy')
plt.show()

# # test individual
# result = cross_validate(classifier_svm, training_set, test_set) # need to set classifier here, currently lr
# classifier = result[2]

# # show errors
# errors = []
# ctr = 0
# for(tweet, label) in datamixed[size:]:
#     guess = classifier.classify(feature_extractor_tripadvisor_top_words_weights(tweet))
#     if guess != label:
#         errors.append((label, guess, tweet))
#     else:
#         ctr += 1
# for (label, guess, tweet) in sorted(errors):
#   print('label=%-8s guess=%-8s tweet=%-30s' % (label, guess, tweet))