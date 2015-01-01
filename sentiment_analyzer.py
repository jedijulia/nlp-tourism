#!/usr/bin/env python
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