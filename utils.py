import nltk

nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")
nltk.download("punkt")
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import tree2conlltags
from typing import List
from itertools import islice


def find_entities(text: str) -> List[str]:
    nes = []
    raw_words = word_tokenize(text)
    tags = pos_tag(raw_words)
    ne = nltk.ne_chunk(tags, binary=True)
    iob_tags = tree2conlltags(ne)
    prev_pos = None
    for word, pos, iob in iob_tags:
        if iob == "B-NE":
            nes.append(word)
        elif pos == "NNP":
            if prev_pos == pos:
                nes.append(" ".join([nes.pop(), word]))
            else:
                nes.append(word)
        prev_pos = pos
    return nes


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def annotate(context, start, end):
    pstart, pend = find_paragraph(context, start)
    chunk1 = context[pstart:start]
    chunk2 = context[start:end]
    chunk3 = context[end:pend]
    return f"{chunk1}<mark>{chunk2}</mark>{chunk3}"


def find_paragraph(text, position):
    # Split the text into paragraphs
    paragraphs = text.split("\n")

    # Find the paragraph that contains the given position
    for i, paragraph in enumerate(paragraphs):
        if position < len(paragraph):
            break
        position -= len(paragraph) + 1

    # Determine the start and end positions of the paragraph
    start = sum(len(paragraphs[j]) + 1 for j in range(i))
    end = start + len(paragraphs[i])

    return start, end
