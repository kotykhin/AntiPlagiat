from src.plagiat import Anti_Plagiat
from nltk.corpus import stopwords


class Ukrainian_Plagiat(Anti_Plagiat):
    def __init__(self, text1, text2, topic):
        super().__init__(text1, text2, topic, "ukr")
        self.pos_arr = list()

    def remove_stopwords(self, text1, text2):
        stop_words = set(stopwords.words('ukrainian'))
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
                    self.ukrainian_lemmatizer.parse(el)[0].normal_form)
            lemm.append(lematized_array)
        return lemm[0], lemm[1]

    def stemming(self, text: list) -> list:
        return list(map(lambda x: self.ukrainian_stemmer.stem_word(x), text))


if __name__ == '__main__':
    f1 = open("text_ukr.txt", "r", encoding="utf-8")
    f2 = open("ukr2.txt", "r", encoding="utf-8")
    ee = Ukrainian_Plagiat(f1.read(), f2.read(), "dd")
    f1.close()
    f2.close()
    # ee.run()
