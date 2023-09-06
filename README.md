# W?

An experimental natural language based querying system for Wikipedia.

## How does it work?

The basic approach is as follows:

* Vector embedddings of sections of Wikipedia articles are prepared and stored
* Calculate the vector embedding for the given query
* Do a vector search in the vector store with Hierarchical Navigable Small World (HNSW) to find vectors that are similar
* Retrieve the corresponding article and narrowed down section

Note that we are not using an LLM here as usual RAG approach do. This experiment is to see if "Retrieval is all you need".

For searching in Wikipedia using natural language questions, getting the context paragraph and link to read more about from original wikipedia article is more useful than
articulated single sentence answer. My reasoning behind this is:

1. LLMs are not 100% free from hallucination. Removing hallucination from answer articulation is compute intensive, costly and not guaranteed.
2. Wikipedia is known for its exploratory characteristics. It is always more useful to give content as such and freedom to learn and explore is well suited to Wikipedia than deadend single sentence answers.

### Embedding

The primary way to injest articles to embedding store is by feeding a list of articles to `wq.injest` module. Then article are split into sections, and sections are split to sentences. For each sentence, embedding is calculated. Along with article metadata, sentence embeddings are stored.

The embedding model I used is E5. For English experiments I used e5-small-v2 with ONNX optimization. The multilingual-e5 supports about 100 languages and I did some experiments on it too. The results vary per language. The base, and large variants of e5 require more compute time even with ONNX optimization.

I also tried with Ctranslate2 inference optimization of e5 models. However, there are some bugs in my implementation.

Keeping the articles in sync with Wikipedia: When somebody search a question and if we don't get an answer from the retrieval step, I search the actual wikipedia with the same query, get the relevant titles, embed it and try retrieval again. This makes the system ready to accept any questions. Another approach that I am thinking is to refresh the article from Wiki if  a new revision exist whenever that article is hit by a search.

I don't see a reason to have prebuilt vectorstore for every article in wikipedia and updated all the time when an edit happens. If the time taken for embedding an article is fast enough, we can do embedding insert/update and retrieval on demand. However, in a real production situation, I might be wrong about this theory.

### Embedding storage

Currently Redis is used. Latest version of Redis has native vector embedding storage and KNN search. From testing it is very reliable and performant.

## Known issues

Splitting content into sentences and doing embedding query on just sentences has some issues. The embedders might be able to accept more tokens than what is present in one sentence. Sentences are often semantically incomplete, especially with co-references. This will affect semantic retrieval.

My current thinking is, we can create embedding for multiple sentences at a time. For example, use 2 or 3 sentences together. This might help the co-reference issue. However if we use many sentences, it will affect the retrieval quality. The tokens present in these sentences will also go beyond the input size of tokenizers causing clipping.

Also, general clean up issues - such as skipping references section and external links from embedding.

How to feed table and list content to embedding so that they are semantically complete?  One approach is to prefix Article title and section title for each entry in the list. If this works, why not feed wikidata props and values to embedding for each article?

## Telegram Bot

To make the application a real chatbot, I added a telegram bot integrated. Please contact me to get the link to the bot.

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

### Add Wikipedia articles to Vector store

Pass the titles to the `wq.injest` module.  You may prepare a textfile with titles and pipe to the script as well.

```bash
echo "Oxygen" | python -m wq.injest
```

### Using docker

Clone the repository, build the docker image and run it.

```bash
docker build -t wq .
docker run -dp 80:8989 wq:latest
```

Open http://0.0.0.0:8989/ using browser

