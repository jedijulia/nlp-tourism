import json

from nltk import FreqDist
from nltk.corpus import stopwords

items = json.loads(open('tourism/tripadvisor_items.json').read())
places = []
contents = []
words = []
stop_words = stopwords.words('english')
symbols = ['&', '-', ' ', '']

for item in items:
    if len(item['place']) > 1:
        places.append(item['place'][1].replace('\n', ''))
    contents.extend(' '.join(item['content']).split(' '))

for word in contents:
    word = word.lower()
    if word not in stop_words and word not in symbols:
        words.append(word)

fdist = FreqDist(words)
top_words = fdist.most_common(102)
for word in top_words:
    print word[0]

f = open('places.txt', 'w')
for place in places:
    f.write(place + '\n')
f.close()

f = open('top_words.txt', 'w')
for word in top_words:
    f.write(word[0].encode('utf-8') + '\n')
f.close()
