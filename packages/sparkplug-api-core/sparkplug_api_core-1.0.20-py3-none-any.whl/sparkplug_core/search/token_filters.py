from elasticsearch_dsl.analysis import token_filter

edge_ngram_filter = token_filter(
    "edge_ngram_filter",
    type="edge_ngram",
    min_gram=1,
    max_gram=10,
)


trigram_filter = token_filter(
    "trigram_filter",
    type="ngram",
    min_gram=3,
    max_gram=3,
)
