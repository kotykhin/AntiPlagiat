from fastapi import HTTPException
from src.LanguagesImplementation.English import English_Plagiat
from src.LanguagesImplementation.Russian import Russian_Plagiat
from src.LanguagesImplementation.Ukrainian import Ukrainian_Plagiat
from nltk.stem import WordNetLemmatizer
import nltk
import sqlite3
import os

lemmatizer_eng = WordNetLemmatizer()


def init_nltk():
    nltk.download('brown')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('universal_tagset')


def init_db():
    exists = os.path.exists('./topics.db')

    if not exists:
        conn = sqlite3.connect('topics.db')
        conn.execute('''CREATE TABLE Topics
                     (Language TEXT NOT NULL,
                      Topic TEXT NOT NULL,
                      PRIMARY KEY(Language, Topic));''')

        conn.close()


def language_check(language: str):
    if language not in ["eng", "rus", "ukr"]:
        raise HTTPException(
            status_code=500,
            detail="Please pass right langage code. Possible values - eng, rus, ukr")


def get_topics(language):
    language_check(language)
    conn = sqlite3.connect('topics.db')
    topics = conn.execute(
        f"Select Topic From Topics Where Language = '{language}'")
    topics_arr = []
    for el in topics:
        topics_arr.append(el[0])
    return topics_arr


def generate_checker(
        language: str, text1: str, text2: str, topic: str):
    if language == "eng":
        return English_Plagiat(
            text1, text2, topic, lemmatizer_eng)
    if language == "rus":
        return Russian_Plagiat(text1, text2, topic)
    if language == "ukr":
        return Ukrainian_Plagiat(text1, text2, topic)


def get_message(koef):
    if koef < 35:
        return """These texts have very little similarity coefficient, so it is just accidental similarities."""
    if 35 < koef < 50:
        return """Program can't define plagiat surely, but it seems to be not plagiated text, maybe only some parts of text have similarities."""
    if 35 < koef < 50:
        return """Program can't define plagiat surely, but it seems to be plagiated text, maybe major parts of text have similarities or full text have been plagiated."""
    if koef > 65:
        return """These texts have very big similarity coefficient, so it is plagiated texts."""
