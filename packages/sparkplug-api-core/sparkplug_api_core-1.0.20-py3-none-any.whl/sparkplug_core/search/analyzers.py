from elasticsearch_dsl import analyzer

from .token_filters import (
    edge_ngram_filter,
    trigram_filter,
)

edge_ngram = analyzer(
    "edge_ngram",
    tokenizer="standard",
    char_filter=["html_strip"],
    filter=[
        "lowercase",
        "asciifolding",
        edge_ngram_filter,
    ],
)


trigram = analyzer(
    "trigram",
    tokenizer="standard",
    char_filter=["html_strip"],
    filter=[
        "lowercase",
        "asciifolding",
        trigram_filter,
    ],
)
