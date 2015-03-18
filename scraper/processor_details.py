import json

from gensim import corpora
from nltk.corpus import stopwords

def clean(word):
    word = word.lower()
    for symbol in symbols:
        word = word.replace(symbol, '')
    return word

items = json.loads(open('tourism/tripadvisor_details_items.json').read())
stopwords = stopwords.words('english')
texts = []
symbols = ['&', '-', ' ', '', '...', '---', '(', ')', '?', '!']

for item in items:
    contents = ''
    details = ''
    if len(item['place']) > 1:
        place = item['place'][1].replace('\n', '')
    for content in item['content']:
        contents += ' ' + content.replace('\n', '')
    for detail in item['details']:
        details += ' ' + detail.replace('\n', '')
    combined = place + ' ' + contents + ' ' + details
    curr = []
    for word in combined.split():
        word = clean(word)
        if word not in stopwords and word not in symbols:
            curr.append(word)
    texts.append(curr)

dictionary = corpora.Dictionary(texts)
dictionary.save('tripadvisor.dict')
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('tripadvisor.mm', corpus)
