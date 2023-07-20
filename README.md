# W?

An experimental natural language based querying system for Wikipedia.

![Screenshot_20230720_161157](https://github.com/santhoshtr/wq/assets/161672/3292b03f-0920-47a1-8913-f2715cca8795)

## How does it work?

* Vector embedddings of sections of Wikipedia articles are prepared and stored
* Calculate the vector embedding for the given query
* Do a vector search in the vector store with Hierarchical Navigable Small World (HNSW) to find vectors that are similar
* Retrieve the corresponding article and narrowed down section
* Use the narrowed down context with an LLM to articulate the answer.

## How to run?

Use the `.env.example` to setup environment variables in a `.env` file.

Install dependencies in a virtual env:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run:

```
uvicorn app:app
```

Open the link provided by gunicorn.

### Using docker

Clone the repository, build the docker image and run it.

```bash
docker build -t wq .
docker run -dp 80:8989 wq:latest
```

Open http://0.0.0.0:8989/ using browser

