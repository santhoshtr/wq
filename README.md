# W?

An experimental natural language based querying system for Wikipedia. Questions are generated using gpt-3.5-turbo model by OpenAI

## How to run?

Provide OPENAI_API_KEY as environment value. An easy way to do this is to create a file nameed `.env` and add a line like this:

```
OPENAI_API_KEY=your-key-goes-here
```

Install dependencies in a virtual env:

```
sudo apt install redis
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

