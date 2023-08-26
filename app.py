import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from wq.llm import llm_prompt_streamer
from wq.retriever import retrieve
from wq.types import RetrievalResult

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


def get_languages():
    return ["en", "es"]


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
    request_obj: dict = await request.json()
    prompt: str = request_obj.get("prompt")
    prompt = prompt.strip()
    return StreamingResponse(llm_prompt_streamer(prompt), media_type="text/event-stream")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
