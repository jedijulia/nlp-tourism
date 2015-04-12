#!/usr/bin/env python
import fileinput
import json
import random

#(head -100 data.txt ) > data_min.txt
# cat data_min.txt | ./processor.py > twitter_data.js
sentiments = ['positive', 'negative']

objects = []

for line in fileinput.input():
    decoded = json.loads(line)
    tweet_id = decoded['id']
    user = decoded['user']['name'].encode('utf-8')
    coordinates = decoded['coordinates']
    text = decoded['text'].encode('utf-8')
    sentiment = random.choice(sentiments)
    if tweet_id and user and coordinates and text and sentiment: 
        obj = {'id': tweet_id, 'user': user, 'coordinates': coordinates, 'text': text, 'sentiment': sentiment}
        objects.append(obj)

print json.dumps(objects)