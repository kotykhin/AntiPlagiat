from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from nltk.stem import WordNetLemmatizer
from pydantic import BaseModel
from English import English_Plagiat
from Russian import Russian_Plagiat
from Ukrainian import Ukrainian_Plagiat
import sqlite3
import os
import uvicorn

app = FastAPI()

lemmatizer_eng = WordNetLemmatizer()

origins = [
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    word = lemmatizer_eng.lemmatize("warmup")
    exists = os.path.exists('./topics.db')

    if not exists:
        conn = sqlite3.connect('topics.db')
        conn.execute('''CREATE TABLE Topics
                     (Language TEXT NOT NULL,
                      Topic TEXT NOT NULL,
                      PRIMARY KEY(Language, Topic));''')

        conn.close()


@app.get("/topics/{lang}")
async def root(lang: str):
    conn = sqlite3.connect('topics.db')
    topics = conn.execute(
        f"Select Topic From Topics Where Language = '{lang}'")
    topics_arr = []
    for el in topics:
        topics_arr.append(el[0])
    return {"message": topics_arr}


class RequestBody(BaseModel):
    language: str
    topic: str
    text1: str
    text2: str


def generate_checker(item: RequestBody):
    if item.language == "eng":
        return English_Plagiat(
            item.text1, item.text2, item.topic, lemmatizer_eng)
    if item.language == "rus":
        return Russian_Plagiat(item.text1, item.text2, item.topic)
    if item.language == "ukr":
        return Ukrainian_Plagiat(item.text1, item.text2, item.topic)


def get_message(koef):
    if koef < 35:
        return """These texts have very little similarity coefficient, so it is just accidental similarities."""
    if 35 < koef < 50:
        return """Program can't define plagiat surely, but it seems to be not plagiated text, maybe only some parts of text have similarities."""
    if 35 < koef < 50:
        return """Program can't define plagiat surely, but it seems to be plagiated text, maybe major parts of text have similarities or full text have been plagiated."""
    if koef > 65:
        return """These texts have very big similarity coefficient, so it is plagiated texts."""


@app.post("/check")
async def create_item(item: RequestBody):
    if item.language not in ["eng", "rus", "ukr"]:
        raise HTTPException(
            status_code=500,
            detail="Please pass right langage code. Possible values - eng, rus, ukr")
    checker = generate_checker(item)
    koef, timer = checker.run()
    sim = float(koef * 100)
    mes = get_message(sim)
    return {
        "percent": round(sim, 3),
        "time": round(timer, 3),
        "conclusion": mes
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
