from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from src.plagiatService import generate_checker, get_message, get_topics, init_db, init_nltk, language_check

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_nltk()
    init_db()


@app.get("/topics/{lang}")
async def root(lang: str):
    language_check(lang)
    topics_arr = get_topics()
    return {"message": topics_arr}


class RequestBody(BaseModel):
    language: str
    topic: str
    text1: str
    text2: str


@app.post("/check")
async def create_item(item: RequestBody):
    language_check()
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
    uvicorn.run(app, host="127.0.0.1", port=8080)
