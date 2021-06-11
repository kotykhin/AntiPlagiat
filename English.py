import contractions
from plagiat import Anti_Plagiat
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
from nltk.corpus import wordnet as wn


class English_Plagiat(Anti_Plagiat):
    def __init__(self, text1, text2, topic, lemmatizer):
        super().__init__(text1, text2, topic, "eng")
        self.pos_arr = list()
        self.english_lemmatizer = lemmatizer

    def make_contractions(self, text):
        contracted_sentences = contractions.fix(text)
        return contracted_sentences

    def remove_stopwords(self, text1, text2):
        stop_words = set(stopwords.words('english'))
        new_sentences1 = list(
            filter(lambda x: x[0] not in stop_words or x[0] == ".", text1))
        new_sentences2 = list(
            filter(lambda x: x[0] not in stop_words or x[0] == ".", text2))
        return new_sentences1, new_sentences2

    def tagger(self, sentences1, sentences2):
        self.pos_text1 = []
        self.pos_text2 = []
        for sent in nltk.sent_tokenize(sentences1):
            definer = nltk.pos_tag(
                nltk.word_tokenize(sent),
                tagset="universal")
            self.pos_text1 += definer
        for sent in nltk.sent_tokenize(sentences2):
            definer = nltk.pos_tag(
                nltk.word_tokenize(sent),
                tagset="universal")
            self.pos_text2 += definer

    def lemmatizer(self, words_array1, words_array2):
        lemm = []
        for arr in [words_array1, words_array2]:
            lematized_array = []
            for el in arr:
                word = ""
                if el[1] == "NOUN":
                    word = self.english_lemmatizer.lemmatize(el[0], wn.NOUN)
                elif el[1] == "VERB":
                    word = self.english_lemmatizer.lemmatize(el[0], wn.VERB)
                elif el[1] == "ADJ":
                    word = self.english_lemmatizer.lemmatize(el[0], wn.ADJ)
                elif el[1] == "ADV":
                    word = self.english_lemmatizer.lemmatize(el[0], wn.ADV)
                elif el[1] == ".":
                    word = "."
                else:
                    word = el[0]
                lematized_array.append((word, self.pos_to_short(el[1])))
            lemm.append(lematized_array)
        return lemm[0], lemm[1]

    def pos_to_short(self, pos):
        if pos == "NOUN":
            return "n"
        if pos == "VERB":
            return "v"
        if pos == "ADJ":
            return "a"
        if pos == "ADV":
            return "r"
        if pos == ".":
            return "."

    def replace_synonyms(self, text_arr1, text1_arr2):
        synonyms = []
        for arr in [text_arr1, text1_arr2]:
            new_text = []
            for tup in arr:
                if tup[1] == ".":
                    new_text.append(tup[0])
                    continue
                syns = wn.synsets(tup[0])
                same_pos = list(filter(lambda w: w.pos() == tup[1], syns))
                if len(same_pos) == 0:
                    new_text.append(tup[0])
                    continue
                name = same_pos[0].name().split(".")[0]
                new_text.append(name)
            synonyms.append(new_text)
        return synonyms[0], synonyms[1]

    def stemming(self, text: list) -> list:
        return list(map(lambda x: self.english_stemmer.stem(x), text))


if __name__ == '__main__':
    f1 = open("text_test1.txt", "r", encoding="utf-8")
    f2 = open("text_test2.txt", "r", encoding="utf-8")
    lemmatizer_eng = WordNetLemmatizer()
    word = lemmatizer_eng.lemmatize("warmup")
    ee = English_Plagiat(f1.read(), f2.read(), "check", lemmatizer_eng)
    f1.close()
    f2.close()
    ee.run()
