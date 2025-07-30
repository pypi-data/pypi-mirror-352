# Transcript RAG

A small toolkit that embeds transcript files into ChromaDB and allows simple retrieval augmented generation queries. It exposes a command line interface via `transcriptrag`.

## Installation

```bash
pip install transcript-rag
```

## Usage

### Embed transcripts

```bash
transcriptrag embed /path/to/transcripts --collection osce --model all-MiniLM-L6-v2
```

### Ask a question

```bash
transcriptrag ask --collection osce "How does the student greet the patient?" --gen-model gemini-pro
```

The command retrieves relevant chunks from ChromaDB and sends them to the specified generation model. Ensure the appropriate API key is available in your environment for the generation model (e.g., Google Generative AI).

## Publishing to PyPI

1. Install build tools: `pip install build twine`
2. Run `python -m build` to generate distribution files in `dist/`
3. Upload with `twine upload dist/*`

