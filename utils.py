import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import tree2conlltags
from typing import List
from itertools import islice

def find_entities(text:str)->List[str]:
  nes=[]
  raw_words= word_tokenize(text)
  tags=pos_tag(raw_words)
  ne = nltk.ne_chunk(tags,binary=True)
  iob_tags = tree2conlltags(ne)
  prev_pos = None
  for (word, pos, iob) in iob_tags:
    if iob == "B-NE":
      nes.append(word)
    elif pos=="NNP":
      if prev_pos == pos:
        nes.append(" ".join([nes.pop(),word]))
      else:
        nes.append(word)
    prev_pos=pos
  return nes

def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())