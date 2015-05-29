#!/usr/bin/env python
import itertools
from operator import itemgetter
import random
import re

from nltk import classify, NaiveBayesClassifier, pos_tag, word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.classify.scikitlearn import SklearnClassifier

from sklearn import cross_validation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC

def feature_extractor(data):
    """
     Extract features using the N-grams method
     parameter: data (tweet)
     returns: N-gram (bigram) features of the given data
    """
    data = data.decode('utf-8')
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    # tokenize input
    tokens = word_tokenize(data)
    
    # append 'no' and 'not' when they occur to preceeding and succeeding tokens
    tokens_mod = []
    i = 0
    while i < len(tokens):
        curr = tokens[i]
        if curr == 'no' or curr == 'not':
            if i - 1 >= 0:
                tokens_mod[-1] = tokens_mod[-1] + '+' + curr
            if i + 1 <= len(tokens) - 1:
                tokens_mod.append(curr + '+' + tokens[i+1])
                i += 1
        else:
            tokens_mod.append(curr)
        i += 1

    data_mod = ''
    for token in tokens_mod:
        data_mod += ' ' + token

    # build bigram analyzer
    bigram_vectorizer = CountVectorizer(ngram_range=(1, 2),token_pattern=r'\b\w+\b', min_df=1)
    analyze = bigram_vectorizer.build_analyzer()
    bigrams = analyze(data_mod)

    # generate features from bigrams
    features = { bigram:1 for bigram in bigrams }
    return features

def feature_extractor_POS(data):
    """
     Extract features using the POS tags method
     parameter: data (tweet)
     returns: pos-tag features of the given data
    """
    data = data.decode('utf-8')
    features = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    # retrieve pos tags given the tweet
    tags = pos_tag(word_tokenize(data))

    # bag-of-words using the tags
    for tag in tags:
        if tag[1] in features:
            features[tag[1]] += 1
        else:
            features[tag[1]] = 1

    return features

def clean(tweet):
    """
     Clean tweets, remove links and punctuation marks
     parameter: tweet
     returns: cleaned tweet
    """
    clean = re.sub(r'https?:\/\/\w+(\.\w+)*(:\w+)?(/[A-Za-z0-9-_\.]*)* ?', '', tweet)
    clean = re.sub(r'\.\.\.', '', clean)
    clean = re.sub(r',', '', clean)
    return clean

def process_data(positive_file, negative_file):
    """
     Process data from positive and negative files
     parameters: positive and negative files
     returns: feature set, training set, test set, mixed data and size
    """

    datamixed = [(clean(tweet), 'positive') for tweet in positive_file]
    datamixed += [(clean(tweet), 'negative') for tweet in negative_file]
    random.shuffle(datamixed)

    feature_set = [(feature_extractor(tweet), label) for (tweet, label) in datamixed]
    size = int(len(feature_set) * 0.8)
    training_set = feature_set[:size]
    test_set = feature_set[size:]
    processed = [feature_set, training_set, test_set, datamixed, size]
    return processed

def get_fscore(classifier, data):
    """
     Compute precision, recall, f-score
     parameters: a classifier, data to classify
     returns: fscore, precision, recall
    """
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    # predict labels and verify, get values for confusion matrix
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

    # compute precision, recall, f-score
    if (true_positives + false_positives) != 0:
        precision = (true_positives * 1.0) / (true_positives + false_positives)
    if (true_positives + false_negatives) != 0:
        recall = (true_positives * 1.0) / (true_positives + false_negatives)
    if (precision + recall) != 0:
        fscore = 2 * (precision * recall) / (precision + recall)

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

    test_accuracy = classify.accuracy(best_classifier, test_set)
    fscore = get_fscore(best_classifier, test_set)
    accuracy = {'test_accuracy': test_accuracy, 'best_train_accuracy': best_train_accuracy}
    to_return = {'classifier': best_classifier, 'fscore': fscore, 'accuracy': accuracy}
    return to_return

def train():
    """
     Train classifier using just tourism and nontourism files
     parameters: none
     returns: classifier, f-score, accuracy
    """

    # get data from files
    positive_file = open('sentiment_analyzer/positive.txt', 'r')
    negative_file = open('sentiment_analyzer/negative.txt', 'r')

    # retrieve features
    data_set = process_data(positive_file, negative_file)
    feature_set = data_set[0]
    training_set = data_set[1]
    test_set = data_set[2]
    datamixed = data_set[3]
    size = data_set[4]

    # classifiers
    classifier_nb = NaiveBayesClassifier

    # get best classifier from cross-validation
    result = cross_validate(classifier_nb, training_set, test_set)
    classifier = result['classifier']
    fscore = result['fscore']
    accuracy = result['accuracy']['test_accuracy']
    to_return = {'classifier': classifier, 'fscore': fscore, 'accuracy': accuracy}
    return to_return

# display errors for error analysis
# errors = []
# ctr = 0
# for(tweet, label) in datamixed[size:]:
#     # predict labels
#     guess = classifier.classify(feature_extractor(tweet))
#     if guess != label:
#         errors.append((label, guess, tweet))
#     else:
#         ctr += 1
# for (label, guess, tweet) in sorted(errors):
#   print('label=%-8s guess=%-8s tweet=%-30s' % (label, guess, tweet))
