import json
import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from wq.embedding import get_embedder
from wq.llm import llm_qa_streamer, llm_prompt_streamer

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
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/api/r")
async def retrieve_context(request: Request) -> Response:
    request_obj: dict = await request.json()
    print(request_obj)
    request_obj.get("language", "en")
    query: str = request_obj.get("query").strip()
    results = get_embedder().search(query, 1)
    result = results[0]
    responsejson: dict = json.dumps(
        {
            "query": result.get("query"),
            "score": result.get("score"),
            "context": result.get("context"),
            "language": result.get("language"),
            "title": result.get("title"),
        }
    )
    response: Response = Response(content=responsejson, media_type="application/json")
    return response


@app.post("/api/q")
async def qa(request: Request) -> Response:
    request_obj: dict = await request.json()
    context: str = request_obj.get("context", "en")
    request_obj.get("language", "en")
    query: str = request_obj.get("query").strip()
    return StreamingResponse(
        llm_qa_streamer(query, context),
        media_type='text/event-stream'
    )

@app.post("/api/chat")
async def qa(request: Request) -> Response:
    request_obj: dict = await request.json()
    prompt: str = request_obj.get("prompt")
    prompt = prompt.strip()
    return StreamingResponse(
        llm_prompt_streamer(prompt),
        media_type='text/event-stream'
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
