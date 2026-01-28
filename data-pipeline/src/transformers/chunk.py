from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.models import Grant, GrantChunk


def _chunk_grant(
    grant: Grant, chunk_size: int = 2000, chunk_overlap: int = 200
) -> list[GrantChunk]:
    """Chunk the grant description using LangChain, prefixing the title to the description."""
    grant_chunks = []

    title = grant.title or ""
    description = grant.description or ""

    # Combine title + description for context-aware chunking
    combined_text = f"{title}\n\n{description}"

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
    )

    description_chunks = splitter.split_text(combined_text)

    for idx, chunk_text in enumerate(description_chunks):
        grant_chunk = GrantChunk(
            grant_id=grant.id,
            chunk_id=idx,
            text=chunk_text,
            metadata={
                "title": grant.title,
                "url": grant.url,
                "summary": grant.summary,
                "start_date": grant.start_date,
                "deadline_date": grant.deadline_date,
                "status": grant.status,
                "total_funding_opportunity": grant.total_funding_opportunity,
            },
        )
        grant_chunks.append(grant_chunk)

    return grant_chunks


def chunk_grants(
    cleaned_grants: list[Grant], chunk_size: int = 2000, chunk_overlap: int = 200
) -> list[GrantChunk]:
    """Chunk a list of cleaned grants into GrantChunk objects."""
    chunks = []
    for grant in cleaned_grants:
        grant_chunks = _chunk_grant(
            grant, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        chunks.extend(grant_chunks)
    return chunks
