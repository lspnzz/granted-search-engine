import sys
import os
import math
from src.transformers.augment import extract_total_budget
from src.models import GrantMetadata
from src.loaders.vectorstore import _create_pinecone_chunk_record
from src.models import GrantChunk

# Add current directory to path
sys.path.append(os.getcwd())


def test_extract_total_budget():
    print("Testing extract_total_budget...")

    # Test None
    assert extract_total_budget(None) is None, "Should return None for None input"

    # Test NaN float
    assert (
        extract_total_budget(float("nan")) is None
    ), "Should return None for NaN float"

    # Test empty string
    assert extract_total_budget("") is None, "Should return None for empty string"

    # Test random text
    assert (
        extract_total_budget("invalid json") is None
    ), "Should return None for invalid json"

    print("extract_total_budget passed!")


def test_metadata_serialization():
    print("Testing metadata serialization...")

    # specific case causing error
    budget = extract_total_budget(None)  # Should be None

    metadata = GrantMetadata(
        title="Test Grant",
        url="http://example.com",
        start_date="2023-01-01",
        deadline_date="2023-12-31",
        status="Open",
        total_funding_opportunity=budget,
    )

    # Create a dummy GrantChunk
    chunk = GrantChunk(
        grant_id="123", chunk_id=1, text="Sample text", metadata=metadata
    )

    # Serialize using logic from vectorstore.py
    # logic: metadata = chunk.metadata.model_dump(exclude_none=True)

    dumped = chunk.metadata.model_dump(exclude_none=True)

    print(f"Dumped metadata: {dumped}")

    assert (
        "total_funding_opportunity" not in dumped
    ), "total_funding_opportunity should be excluded if None"

    print("Metadata serialization passed!")


if __name__ == "__main__":
    try:
        test_extract_total_budget()
        test_metadata_serialization()
        pass
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)
