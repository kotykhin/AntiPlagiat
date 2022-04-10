from src.plagiat import Anti_Plagiat
from nltk.corpus import stopwords


class Russian_Plagiat(Anti_Plagiat):
    def __init__(self, text1, text2, topic):
        super().__init__(text1, text2, topic, "rus")
        self.pos_arr = list()

    def remove_stopwords(self, text1, text2):
        stop_words = set(stopwords.words('russian'))
        new_sentences1 = list(
            filter(lambda x: x[0] not in stop_words or x[0] == ".", text1))
        new_sentences2 = list(
            filter(lambda x: x[0] not in stop_words or x[0] == ".", text2))
        return new_sentences1, new_sentences2

    def lemmatizer(self, words_array1, words_array2):
        lemm = []
        for arr in [words_array1, words_array2]:
            lematized_array = []
            for el in arr:
                lematized_array.append(
                    self.russian_lemmatizer.parse(el)[0].normal_form)
            lemm.append(lematized_array)
        return lemm[0], lemm[1]

    def replace_synonyms(self, text_arr1, text_arr2):
        for i in range(len(text_arr1)):
            synsets = self.wikiwordnet.get_synsets(text_arr1[i])
            if len(synsets) == 0:
                continue
            current_synset = synsets[0]
            for synonym in current_synset.get_words():
                text_arr1[i] = synonym.lemma()
                continue
        for i in range(len(text_arr2)):
            synsets = self.wikiwordnet.get_synsets(text_arr2[i])
            if len(synsets) == 0:
                continue
            current_synset = synsets[0]
            for synonym in current_synset.get_words():
                text_arr2[i] = synonym.lemma()
                continue
        return text_arr1, text_arr2

    def stemming(self, text: list) -> list:
        return list(map(lambda x: self.russian_stemmer.stem(x), text))


if __name__ == '__main__':
    f1 = open("text3.txt", "r", encoding="utf-8")
    f2 = open("text4.txt", "r", encoding="utf-8")
    ee = Russian_Plagiat(f1.read(), f2.read(), "dd")
    f1.close()
    f2.close()
    # ee.run()
    a = []
    b = []
    syns = ee.wikiwordnet.get_synsets("собака")
    w = syns[0].get_words()[0].lemma()
    synss = ee.wikiwordnet.get_synsets("пёс")
    for s in synss:
        for el in s.get_words():
            b.append(el.lemma())
    print("")
