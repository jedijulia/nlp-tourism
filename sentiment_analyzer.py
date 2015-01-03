#!/usr/bin/env python
import random
import re

def clean(tweet):
    clean = re.sub(r'https?:\/\/\w+(\.\w+)*(:\w+)?(/[A-Za-z0-9-_\.]*)* ?', '', tweet)
    clean = re.sub(r'#', '', clean)
    clean = re.sub(r'!', '', clean)
    clean = re.sub(r'\.\.\.', '', clean)
    clean = re.sub(r',', '', clean)
    return clean

def process_data(positive_file, negative_file):
    datamixed = [(clean(tweet), 'positive') for tweet in positive_file]
    datamixed += [(clean(tweet), 'negative') for tweet in negative_file]
    random.shuffle(datamixed)

    feature_set = [(feature_extractor_top_words_weights(tweet), label) for (tweet, label) in datamixed]
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