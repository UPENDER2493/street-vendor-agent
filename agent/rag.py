"""
Lightweight RAG (Retrieval-Augmented Generation) layer.

Why TF-IDF instead of embeddings?
- Zero external downloads / zero API cost for retrieval -> works instantly, offline, and is fast
  enough for a knowledge base of this size (a handful of markdown docs).
- Easy to explain to judges/mentors: "we chunk our trusted docs, TF-IDF rank them against the
  vendor's question, and hand the top chunks to IBM Granite as grounding context" -- a clean,
  demonstrable RAG pipeline without hiding behind a black-box embedding call.
- Swappable later: if you want vector embeddings, you can replace `TfidfVectorizer` with a
  watsonx.ai embeddings call (see README for a note on this) without touching the rest of the app.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")


@dataclass
class Chunk:
    source: str
    heading: str
    text: str


def _split_into_chunks(filepath: str) -> list[Chunk]:
    """Split a markdown file into chunks along its '##' headings."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    source = os.path.basename(filepath)
    # Split on level-2 headings, keep the heading text with its section
    parts = re.split(r"\n(?=## )", content)
    chunks: list[Chunk] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        heading_match = re.match(r"^#{1,2}\s*(.+)", part)
        heading = heading_match.group(1).strip() if heading_match else source
        # Keep chunks a reasonable size; further split very long sections on '###'
        if len(part) > 1800:
            subparts = re.split(r"\n(?=### )", part)
            for sp in subparts:
                sp = sp.strip()
                if sp:
                    chunks.append(Chunk(source=source, heading=heading, text=sp))
        else:
            chunks.append(Chunk(source=source, heading=heading, text=part))
    return chunks


class KnowledgeBase:
    """Loads all knowledge_base/*.md files, chunks them, and answers TF-IDF similarity queries."""

    def __init__(self, kb_dir: str = KB_DIR):
        self.kb_dir = kb_dir
        self.chunks: list[Chunk] = []
        for fname in sorted(os.listdir(kb_dir)):
            if fname.endswith(".md"):
                self.chunks.extend(_split_into_chunks(os.path.join(kb_dir, fname)))

        self._texts = [c.text for c in self.chunks]
        self._vectorizer = TfidfVectorizer(stop_words="english", max_features=4000)
        self._matrix = self._vectorizer.fit_transform(self._texts) if self._texts else None

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.05) -> list[Chunk]:
        if not self._texts:
            return []
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        ranked_idx = scores.argsort()[::-1]
        results = []
        for idx in ranked_idx[:top_k]:
            if scores[idx] >= min_score:
                results.append(self.chunks[idx])
        return results

    def format_context(self, chunks: list[Chunk]) -> str:
        if not chunks:
            return ""
        blocks = []
        for c in chunks:
            blocks.append(f"[Source: {c.source} | {c.heading}]\n{c.text}")
        return "\n\n---\n\n".join(blocks)


_kb_instance: KnowledgeBase | None = None


def get_kb() -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
