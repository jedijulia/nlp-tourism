from gensim.corpora import Dictionary, MmCorpus
from gensim.models.ldamodel import LdaModel

symbols = [',', '.', '-', '@']
def clean(word):
    word = word.lower()
    for symbol in symbols:
        word = word.replace(symbol, '')
    return word

id2word = Dictionary.load('scraper/tripadvisor.dict')
mm = MmCorpus('scraper/tripadvisor.mm')
lda = LdaModel(corpus=mm, id2word=id2word, num_topics=100, update_every=1, chunksize=100, passes=1)
topics = lda.print_topics(num_topics=100)

top_words = []

for topic in topics:
    topic = topic.replace('+', '')
    topic_split = topic.split()
    for item in topic_split:
        item = item.strip().split('*')[1]
        top_words.append(clean(item))

f = open('scraper/top_words_lda.txt', 'w')
for word in top_words:
    f.write(word.encode('utf-8') + '\n')
f.close()