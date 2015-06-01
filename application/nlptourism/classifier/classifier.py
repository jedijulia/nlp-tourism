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
    """
     Extract features using the bag-of-words method
     parameter: data (tweet)
     returns: bag-of-words features
    """
    data = data.decode('utf-8')
    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    # preprocessing: tokenize, convert to lowercase and lemmatize words
    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    # remove stop words and add words and their frequencies as features
    for word in words:
        if word not in stop_words:
            if word in features:
                features[word] += 1
            else:
                features[word] = 1

    return features

def feature_extractor_top_words(data):
    """
     Extract features using the top words method
     parameter: data (tweet)
     returns: returns features of the given data
    """
    data = data.decode('utf-8')
    # top 15 frequently-ocurring words from the tourism-related twitter corpus
    top_words = ['travel', 'vacation', 'city', 'itsmorefuninthephilippines', 'travel',
                 'boracay', 'philippine', 'view', 'day', 'beach', 'morning', 'resort', 
                 'good', 'cebu', 'island']
    features = {word: 0 for word in top_words}
    lemmatizer = WordNetLemmatizer()

    # preprocessing: tokenize, convert to lowercase and lemmatize words
    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    # remove stop words and add words and their frequencies as features
    for word in words:
        if word in features:
            features[word] += 1

    return features

def feature_extractor_top_words_weights(data):
    """
     Extract features using the top words with weights method
     parameter: data (tweet)
     returns: returns features of the given data
    """
    data = data.decode('utf-8')
    # top 15 frequently-ocurring words from the tourism-related twitter corpus
    top_words = ['travel', 'vacation', 'city', 'itsmorefuninthephilippines', 'travel',
                 'boracay', 'philippine', 'view', 'day', 'beach', 'morning', 'resort', 
                 'good', 'cebu', 'island']
    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    # preprocessing: tokenize, convert to lowercase and lemmatize words
    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    # remove stop words and add words and their frequencies as features
    for word in words:
        if word not in stop_words:
            if word in features:
                # if word is found in the top words list, increase by 1.5 or preferred weight
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
    """
     Extract features using the top words with weights 
     method using words from TripAdvisor
     parameter: data (tweet)
     returns: returns features of the given data
    """
    data = data.decode('utf-8')

    # retrieve file of top 100 frequently-occurring words from TripAdvisor comments
    top_file = open('classifier/top_words.txt', 'r')
    top_words = [word.replace('\n', '') for word in top_file]
    # retrieve file of 100 places from TripAdvisor
    places_file = open('classifier/places.txt', 'r')

    # clean places file
    for place in places_file:
        place = place.replace('\n', '')
        for word in place.split(' '):
            if word != '-':
                top_words.append(word)

    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    # preprocessing: tokenize, convert to lowercase and lemmatize words
    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    # remove stop words and add words and their frequencies as features
    # if word is found in the top words list, increase by 1.5 or preferred weight
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

def feature_extractor_lda_tripadvisor_top_words_weights(data):
    """
     Extract features using the top words with weights method
     using words generated by LDA from TripAdvisor
     parameter: data (tweet)
     returns: N-gram (bigram) features of the given data
    """
    data = data.decode('utf-8')

    # retrieve file of topics and consequent words generated by LDA from TripAdvisor comments
    top_file = open('classifier/top_words_lda.txt', 'r')
    top_words = [word.replace('\n', '') for word in top_file]

    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    # preprocessing: tokenize, convert to lowercase and lemmatize words
    words = [lemmatizer.lemmatize(word.lower()) for word in word_tokenize(data)]

    # remove stop words and add words and their frequencies as features
    # if word is found in the top words list, increase by 1.5 or preferred weight
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
    """
     Clean tweet, remove links and punctuation marks
     parameter: tweet
     returns: cleaned tweet
    """
    clean = re.sub(r'https?:\/\/\w+(\.\w+)*(:\w+)?(/[A-Za-z0-9-_\.]*)* ?', '', tweet)
    clean = re.sub(r'#', '', clean)
    clean = re.sub(r'!', '', clean)
    clean = re.sub(r'\.\.\.', '', clean)
    clean = re.sub(r',', '', clean)
    return clean

def process_data(tourism_file, nontourism_file):
    """
     Process data from tourism and nontourism files
     parameter: tourism and nontourism files
     returns: feature set, training set, test set, mixed data and size
    """
    # label tweets from tourism file as tourism and add to datamixed
    datamixed = [(clean(tweet), 'tourism') for tweet in tourism_file]
    # label tweets from nontourism file as nontourism and add to datamixed
    datamixed += [(clean(tweet), 'nontourism') for tweet in nontourism_file]
    random.shuffle(datamixed) # shuffle data

    # construct feature set using specified feature extractor
    feature_set = [(feature_extractor_lda_tripadvisor_top_words_weights(tweet), label) for (tweet, label) in datamixed]
    
    # divide set, 80% training set, 20% test set
    size = int(len(feature_set) * 0.8)
    training_set = feature_set[:size]
    test_set = feature_set[size:]
    processed = [training_set, test_set, datamixed, size, feature_set]
    return processed

def process_data_db(tourism_file, nontourism_file, tourism_tweets, nontourism_tweets):
    """
     Process data from files and db (generated by manual verification 
        and validation in the web app)
     parameter: tourism and nontourism files, tourism and nontourism tweet objects
     returns: feature set, training set, test set, mixed data and size
    """
    # label and add data from tourism and nontourism files
    datamixed = [(clean(tweet), 'tourism') for tweet in tourism_file]
    datamixed += [(clean(tweet), 'nontourism') for tweet in nontourism_file]

    # label, encode and clean tourism_tweets and nontourism-tweets (from db)
    datamixed += [ (clean(tweet.text.encode('utf-8')) , 'tourism') for tweet in tourism_tweets]
    datamixed += [(clean(tweet.text.encode('utf-8')), 'nontourism') for tweet in nontourism_tweets]

    # shuffle data
    random.shuffle(datamixed)

    # construct feature set using specified feature extractor
    feature_set = [(feature_extractor_lda_tripadvisor_top_words_weights(tweet), label) for (tweet, label) in datamixed]
    
    # divide set, 80% training set, 20% test set
    size = int(len(feature_set) * 0.8)
    training_set = feature_set[:size]
    test_set = feature_set[size:]
    processed = [training_set, test_set, datamixed, size, feature_set]
    return processed

def get_fscore(classifier, data):
    """
     Retrieve precision, recall, f-score given a classifier and data to test on
     parameter: a classifier, data
     returns: f-score, precision, recall
    """
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    # predict labels and verify, get values for confusion matrix
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

    # compute precision, recall, f-score
    if (true_positives + false_positives) != 0:
        precision = (true_positives * 1.0) / (true_positives + false_positives)
    if (true_positives + false_negatives) != 0:
        recall = (true_positives * 1.0) / (true_positives + false_negatives)
    if (precision + recall) != 0:
        fscore = 2 * (precision * recall) / (precision + recall)

    # print 'Precision: ' + str(precision)
    # print 'Recall: ' + str(recall)
    # print 'F-score: ' + str(fscore)
    performance = {'fscore': fscore, 'precision': precision, 'recall': recall}
    return performance

def cross_validate(classifier, training_set, test_set):
    """
     Performs 10-fold cross validation
     parameters: a classifier, training set, test set
     returns: best classifier, f-score, accuracy
    """
    chosen_classif = classifier
    best_accuracy = 0.0
    best_train_accuracy = None
    best_classifier = None

    # retrieve indices of data to be used as training and test sets in cross-validation
    k_fold = cross_validation.KFold(len(training_set), n_folds=10)

    # loop through tweets with those indices
    for train_indices, test_indices in k_fold:

        # retrieve training and test (cross validation) sets
        train = itemgetter(*train_indices)(training_set)
        test = itemgetter(*test_indices)(training_set)
        
        classifier = chosen_classif.train(train)
        train_accuracy = classify.accuracy(classifier, train)
        
        if len(test_indices) == 1:
            test = (test,)

        # retrieve accuracy
        accuracy = classify.accuracy(classifier, test)

        # if accuracy is greater than the best accuracy, store as best classifier
        if accuracy > best_accuracy:
            best_classifier = classifier
            best_accuracy = accuracy
            best_train_accuracy = train_accuracy
        fscore = get_fscore(classifier, test)
    
    test_accuracy = classify.accuracy(best_classifier, test_set)
    accuracy = {'test_accuracy': test_accuracy, 'best_train_accuracy': best_train_accuracy}
    to_return = {'classifier': best_classifier, 'fscore': fscore, 'accuracy': accuracy}
    return to_return

def train():
    """
     Train classifier using just tourism and nontourism files
     parameters: none
     returns: classifier
    """
    # get data from files
    tourism_file = open('classifier/tourism.txt', 'r')
    nontourism_file = open('classifier/nontourism.txt', 'r')

    # retrieve features
    data_set = process_data(tourism_file, nontourism_file)
    training_set = data_set[0]
    test_set = data_set[1]
    datamixed = data_set[2]
    size = data_set[3]
    feature_set = data_set[4]

    # classifiers
    classifier_nb = NaiveBayesClassifier
    classifier_lr = SklearnClassifier(LogisticRegression())
    classifier_svm = SklearnClassifier(LinearSVC())

    # get best classifier from cross-validation
    classifier = cross_validate(classifier_svm, training_set, test_set)['classifier'] # set classifier
    return classifier

def train_db(tourism_tweets, nontourism_tweets):
    """
     Train classifier using tourism and nontourism files and data from db
     parameter: tourism and nontourism-related tweets
     returns: classifier, f-score, accuracy
    """
    # get data from files
    tourism_file = open('classifier/tourism.txt', 'r')
    nontourism_file = open('classifier/nontourism.txt', 'r')

    # retrieve features
    data_set = process_data_db(tourism_file, nontourism_file, tourism_tweets, nontourism_tweets)
    training_set = data_set[0]
    test_set = data_set[1]
    datamixed = data_set[2]
    size = data_set[3]
    feature_set = data_set[4]

    # classifiers
    classifier_nb = NaiveBayesClassifier
    classifier_lr = SklearnClassifier(LogisticRegression())
    classifier_svm = SklearnClassifier(LinearSVC())

    # test using a specified classifier
    result = cross_validate(classifier_svm, training_set, test_set) # set classifier
    classifier = result['classifier']
    fscore = result['fscore']
    accuracy = result['accuracy']['test_accuracy']

    to_return = {'classifier': classifier, 'fscore': fscore, 'accuracy': accuracy}

    plotfile = open('phtweetmap/plotdata/tw-tripadvisor-lda-svm.txt', 'w')

    # loop through increasing data sizes
    data_size = 20
    while data_size <= 1215:
        curr_data_set = feature_set[:data_size]
        curr_size = int(len(curr_data_set) * 0.8)
        train = curr_data_set[:curr_size]
        test = curr_data_set[curr_size:]
        accuracy = cross_validate(classifier_svm, train, test)['accuracy'] # set classifier

        # write train and test accuracies onto file
        plotfile.write(str(data_size) + ' ' + str(accuracy['test_accuracy']) +  ' ' + str(accuracy['best_train_accuracy']) + '\n')

        data_size += 50
    plotfile.close()

    # display errors for error analysis
    errors = []
    ctr = 0
    for(tweet, label) in datamixed[size:]:
        # predict labels
        guess = classifier.classify(feature_extractor(tweet))
        if guess != label:
            errors.append((label, guess, tweet))
        else:
            ctr += 1

    # print errors: actual label, wrong guess and tweet
    for (label, guess, tweet) in sorted(errors):
      print('label=%-8s guess=%-8s tweet=%-30s' % (label, guess, tweet))

    return to_return