import pymorphy2
from nltk.stem import SnowballStemmer
from uk_stemmer import UkStemmer
from wiki_ru_wordnet import WikiWordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import re
import math
import time
from string import punctuation
from datetime import datetime
import requests
import json


class Anti_Plagiat():
    """
    Check two docs whether plagiat or not
    """
    wikiwordnet = WikiWordnet()
    russian_lemmatizer = pymorphy2.MorphAnalyzer()
    ukrainian_lemmatizer = pymorphy2.MorphAnalyzer(lang='uk')
    english_stemmer = SnowballStemmer("english")
    russian_stemmer = SnowballStemmer("russian")
    ukrainian_stemmer = UkStemmer()
    tf_idf_vectorizer = TfidfVectorizer()

    elastic_api_url = "http://localhost:9200"

    def __init__(self, text1, text2, topic, language):
        # check elastic work
        res = requests.get(self.elastic_api_url + '/').json()
        self.raw_text1, self.raw_text2 = text1, text2
        self.language = language
        self.topic = topic

    def make_contractions(self, text):
        return text

    def remove_stopwords(self, text1, text2):
        return text1, text2

    def remove_URL(self, sample):
        return re.sub(r"http\S+", "", sample)

    def replace_synonyms(self, text_arr1, text_arr2):
        return text_arr1, text_arr2

    def lemmatizer(self, words_array: list) -> list:
        # overriden in language classes
        return words_array

    def stemming(self, text: str) -> str:
        # overriden in language classes
        return text

    def tagger(self, text1, text2):
        self.pos_text1 = text1
        self.pos_text2 = text2

    def make_cleaning(self):
        text1 = self.remove_URL(self.raw_text1)
        text2 = self.remove_URL(self.raw_text2)

        contracted_sentences1 = self.make_contractions(text1)
        contracted_sentences1 = contracted_sentences1.lower()
        contracted_sentences2 = self.make_contractions(text2)
        contracted_sentences2 = contracted_sentences2.lower()

        new_sentence1 = re.sub(r"[!?:;0-9]|\.+|…+",
                               ' . ', contracted_sentences1)
        new_sentence2 = re.sub(r"[!?:;0-9]|\.+|…+",
                               ' . ', contracted_sentences2)

        punct = re.sub(r"[!?:;]|\.+|…+", '', punctuation)
        punct = punct.replace('-', '\-')
        punct += "—«»№”“"

        new_sentence1 = re.sub(rf"\s|\n|\r|[{punct}]+", ' ', new_sentence1)
        new_sentence2 = re.sub(rf"\s|\n|\r|[{punct}]+", ' ', new_sentence2)

        self.tagger(new_sentence1, new_sentence2)
        new_sentences1 = self.pos_text1
        new_sentences2 = self.pos_text2

        new_sentences1, new_sentences2 = self.remove_stopwords(
            new_sentences1, new_sentences2)
        new_lem1, new_lem2 = self.lemmatizer(new_sentences1, new_sentences2)
        after_syn1, after_syn2 = self.replace_synonyms(new_lem1, new_lem2)
        clean_text1 = self.stemming(after_syn1)
        clean_text2 = self.stemming(after_syn2)
        self.formatted_text1 = ' '.join(map(str, clean_text1))
        self.formatted_text2 = ' '.join(map(str, clean_text2))

    def check_if_topic_exist(self):
        conn = sqlite3.connect('topics.db')
        exist = conn.execute(
            f"Select Count(*) From Topics Where Language = '{self.language}' and Topic = '{self.topic}'")
        for el in exist:
            if el[0] == 0:
                conn.execute(
                    f"Insert INTO Topics(Language,Topic) Values('{self.language}','{self.topic}')")
                conn.commit()
                conn.close()
                return False
            break
        conn.close()
        return True

    def create_index_elastic(self):
        data = {
            "mappings": {
                "properties": {
                    "text": {
                        "type": "text",
                        "term_vector": "yes",
                        "store": "true",
                        "analyzer": "fulltext_analyzer"
                    }
                }
            },
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                },
                "analysis": {
                    "analyzer": {
                        "fulltext_analyzer": {
                            "type": "custom",
                            "tokenizer": "whitespace",
                            "filter": [
                                "lowercase"
                            ]
                        }
                    }
                }
            }
        }
        ansr = requests.put(self.elastic_api_url +
                            f'/{self.topic}_{self.language}', json.dumps(data),
                            headers={"content-type": "application/json"})
        print(ansr.content.decode())

    def put_doc_to_elastic_index(self, id, text):
        body = {"text": text}
        param = {"refresh": "true"}
        ansr = requests.put(
            self.elastic_api_url + f'/{self.topic}_{self.language}/_doc/{id}',
            json.dumps(body),
            headers={"content-type": "application/json"}, params=param)
        print(ansr.content.decode())

    def get_milliseconds_now(self):
        t0 = datetime(1, 1, 1)
        now = datetime.utcnow()
        return (now - t0).total_seconds() * 100

    def check_words(self) -> float:
        exist = self.check_if_topic_exist()
        if not exist:
            self.create_index_elastic()
        id2 = int(self.get_milliseconds_now())
        id1 = id2 - 1
        self.put_doc_to_elastic_index(
            id1, re.sub(r"\.+", '', self.raw_text1))
        self.put_doc_to_elastic_index(
            id2, re.sub(r"\.+", '', self.raw_text2))
        data = {
            "fields": ["text"],
            "term_statistics": "true",
            "field_statistics": "true"
        }

        text1_stat = requests.get(
            self.elastic_api_url +
            f'/{self.topic}_{self.language}/_termvectors/{id1}',
            data=json.dumps(data),
            headers={"content-type": "application/json"})
        text2_stat = requests.get(
            self.elastic_api_url +
            f'/{self.topic}_{self.language}/_termvectors/{id2}',
            data=json.dumps(data),
            headers={"content-type": "application/json"})

        terms_dict = {}
        item_dict1 = json.loads(text1_stat.content)
        item_dict2 = json.loads(text2_stat.content)

        count_docs1 = item_dict1["term_vectors"]["text"]["field_statistics"]["doc_count"]
        count_docs2 = item_dict2["term_vectors"]["text"]["field_statistics"]["doc_count"]

        count_words1 = len(item_dict1["term_vectors"]["text"]["terms"])
        count_words2 = len(item_dict1["term_vectors"]["text"]["terms"])
        for w, value in item_dict1["term_vectors"]["text"]["terms"].items():

            if w in item_dict2["term_vectors"]["text"]["terms"]:
                sec = item_dict2["term_vectors"]["text"]["terms"][w]
                est1 = (value["term_freq"] / count_words1) / (count_docs1 /
                                                              value["doc_freq"])
                est2 = (sec["term_freq"] / count_words2) / (count_docs2 /
                                                            sec["doc_freq"])
                terms_dict[w] = [est1, est2]
            else:
                est1 = (value["term_freq"] / count_words1) / (count_docs1 /
                                                              value["doc_freq"])
                terms_dict[w] = [est1, 0]

        for w, value in item_dict2["term_vectors"]["text"]["terms"].items():
            if w not in terms_dict:
                est = (value["term_freq"] / count_words2) / (count_docs2 /
                                                             value["doc_freq"])
                terms_dict[w] = [0, est]
            else:
                continue
        numerator = 0
        denomirator_doc1 = 0
        denomirator_doc2 = 0

        for tup in terms_dict.values():
            numerator += tup[0] * tup[1]
            denomirator_doc1 += tup[0] ** 2
            denomirator_doc2 += tup[1] ** 2

        denomirator = math.sqrt(
            denomirator_doc1) * math.sqrt(denomirator_doc2)

        return numerator / denomirator

    def run(self):
        start_time = time.time()
        self.make_cleaning()
        koef_words = self.check_words()
        timer = time.time() - start_time
        return koef_words, timer
