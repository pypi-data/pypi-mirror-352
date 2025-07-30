import typer

from .embedding import embed_transcripts
from .query import ask_question

app = typer.Typer(
    help="Simple toolkit to embed transcripts and query with RAG"
)


@app.command()
def embed(
    folder: str = typer.Argument(
        ..., help="Folder with transcript .txt files"
    ),
    collection: str = typer.Option(
        "transcripts", help="Chroma collection name"
    ),
    model: str = typer.Option("all-MiniLM-L6-v2", help="Embedding model"),
    persist: str = typer.Option(
        "chroma_db", help="Chroma persistence directory"
    ),
    distance: str = typer.Option("cosine", help="Distance metric"),
):
    """Embed transcripts and store them in ChromaDB."""
    embed_transcripts(
        folder_path=folder,
        collection_name=collection,
        model_name=model,
        persist_directory=persist,
        distance=distance,
    )


@app.command()
def ask(
    collection: str = typer.Option(
        "transcripts", help="Chroma collection name"
    ),
    query_text: str = typer.Argument(..., help="Your question"),
    embed_model: str = typer.Option(
        "all-MiniLM-L6-v2", help="Embedding model"
    ),
    gen_model: str = typer.Option("gemini-pro", help="Generation model"),
    persist: str = typer.Option(
        "chroma_db", help="Chroma persistence directory"
    ),
    n_results: int = typer.Option(5, help="Number of documents to retrieve"),
):
    """Query the collection and generate an answer."""
    answer = ask_question(
        collection_name=collection,
        query_text=query_text,
        embed_model=embed_model,
        gen_model=gen_model,
        persist_directory=persist,
        n_results=n_results,
    )
    typer.echo(answer)


if __name__ == "__main__":  # pragma: no cover
    app()
