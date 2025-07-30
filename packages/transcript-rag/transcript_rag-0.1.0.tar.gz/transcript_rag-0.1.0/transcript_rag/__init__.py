"""Transcript RAG package."""

from .embedding import embed_transcripts
from .query import ask_question

__all__ = ["embed_transcripts", "ask_question"]
