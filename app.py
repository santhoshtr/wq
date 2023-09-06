import os
import urllib

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from wq.retriever import retrieve
from wq.types import RetrievalResult

load_dotenv()

project_dir = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/api/r")
async def retrieve_context(request: Request) -> list[RetrievalResult]:
    request_obj: dict = await request.json()
    request_obj.get("language", "en")
    query: str = request_obj.get("query").strip()
    n_results = request_obj.get("n_results", 2)
    return retrieve(query=query, n_results=n_results)


@app.post("/api/chat")
async def chat_api(request: Request) -> Response:
    from wq.llm import llm_prompt_streamer

    request_obj: dict = await request.json()
    prompt: str = request_obj.get("prompt")
    prompt = prompt.strip()
    return StreamingResponse(llm_prompt_streamer(prompt), media_type="text/event-stream")


@app.post("/telegram")
async def webhook(request: Request):
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    data = await request.json()

    chat_id = data["message"]["chat"]["id"]
    if "text" not in data["message"]:
        return

    text = data["message"]["text"]
    if text == "/start":
        response_msg = "Hi!, I am Wikipedia bot. Ask me anything!"
        await httpx.AsyncClient().get(f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={response_msg}")
        return data
    question = text
    results = retrieve(query=question, n_results=1)
    if len(results) == 0:
        response_msg = "Sorry, Could not find answer for that question."
        payload = {"chat_id": chat_id, "text": response_msg}
        await httpx.AsyncClient().get(f"{BASE_URL}/sendMessage", params=payload)
    else:
        result: RetrievalResult = results[0]
        wiki_url = f"https://{result.wikicode}.wikipedia.org/wiki/{urllib.parse.quote(result.title)}"
        response_msg = f"""
From {result.title} article of Wikipedia:

{BeautifulSoup(result.content_html).get_text()}

Read more: {wiki_url}
        """
        # Refer: https://core.telegram.org/bots/api#formatting-options
        payload = {"chat_id": chat_id, "text": response_msg}
        await httpx.AsyncClient().get(f"{BASE_URL}/sendMessage", params=payload)
    return data


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
