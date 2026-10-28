import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

class DocumentRetriever:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def index_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        self.chunks = chunks
        corpus = [self._tokenize(chunk["text"]) for chunk in chunks]
        if corpus:
            self.bm25 = BM25Okapi(corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        indexed_scores = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in indexed_scores[:top_k]:
            if score > 0.0:
                results.append(self.chunks[idx])

        if not results and self.chunks:
            results = self.chunks[:top_k]

        return results
