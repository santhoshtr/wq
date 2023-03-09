# W?

An experimental natural language based querying system for Wikipedia. Questions are generated using gpt-3.5-turbo model by OpenAI

## How to run?

Provide OPENAI_API_KEY as environment value. An easy way to do this is to create a file nameed `.env` and add a line like this:

```
OPENAI_API_KEY=your-key-goes-here
```

Install dependencies in a virtual env:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run:

```
gunicorn
```

Open the link provided by gunicorn.

