from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.models import Grant, GrantChunk


def chunk_grant(grant: Grant) -> list[GrantChunk]:
    """Chunk the grant description using LangChain, prefixing the title to the description."""
    grant_chunks = []

    title = grant.title or ""
    description = grant.description or ""

    # Combine title + description for context-aware chunking
    combined_text = f"{title}\n\n{description}"

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
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
                "start_date": grant.start_date,
                "deadline_date": grant.deadline_date,
                "status": grant.status,
                "total_funding_opportunity": grant.total_funding_opportunity,
            },
        )
        grant_chunks.append(grant_chunk)

    return grant_chunks
