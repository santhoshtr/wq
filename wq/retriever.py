from wq.vectorstore import ChromaVectorStore


def retrieve(query: str = "en", n_results=2):
    # embedding_function = SBERTEmbedder()
    # vector_store = ChromaVectorStore(embedding_function=embedding_function)
    vector_store = ChromaVectorStore(embedding_function=None)
    query_result = vector_store.query(query=query, n_results=n_results)
    vector_store = None
    retrieval_results: list[dict] = []
    results_len = len(query_result.get("ids")[0])
    for r in range(0, results_len):
        retrieval_results.append(
            {
                "query": query,
                "score": query_result.get("distances")[0][r],
                "context": query_result.get("documents")[0][r],
                "language": query_result.get("metadatas")[0][r].get("language"),
                "title": query_result.get("metadatas")[0][r].get("title"),
                "html": query_result.get("metadatas")[0][r].get("html"),
                "url": query_result.get("metadatas")[0][r].get("url"),
                "image": query_result.get("metadatas")[0][r].get("thumbnail"),
            }
        )
    return retrieval_results


if __name__ == "__main__":
    import fileinput
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="wikiembedder", description="Query embedding for given wikipedia articles")
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="Files to read, if empty, stdin is used",
    )
    args = parser.parse_args()
    for query in fileinput.input(files=args.files):
        print(retrieve(query, n_results=2))
