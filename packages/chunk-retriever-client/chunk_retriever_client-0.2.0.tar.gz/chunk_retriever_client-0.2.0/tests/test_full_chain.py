import pytest
import uuid
from chunk_metadata_adapter import ChunkMetadataBuilder, ChunkType, FlatSemanticChunk
from vector_store_client import create_client as create_vector_client
from chunk_retriever_client.client import ChunkRetrieverClient
from svo_client.chunker_client import ChunkerClient

@pytest.mark.asyncio
async def test_full_chain():
    # 1. Generate source_id and text
    source_id = str(uuid.uuid4())
    text = "def hello_world():\n    print('Hello, World!')"
    builder = ChunkMetadataBuilder(project="TestProject", unit_id="test")

    # 2. Send text to chunker (без source_id)
    async with ChunkerClient(url="http://localhost", port=8009) as svo:
        chunks = await svo.chunk_text(text=text, language="python")
    assert len(chunks) > 0

    # 3. Generate flat metadata for each chunk
    flat_chunks = []
    for i, ch in enumerate(chunks):
        flat = builder.build_flat_metadata(
            text=ch.text,
            source_id=source_id,
            ordinal=i,
            type=ChunkType.CODE_BLOCK,
            language="python"
        )
        flat["start"] = 0
        flat["end"] = len(ch.text)
        # Use validate_and_fill for strict validation and autofill
        obj, err = FlatSemanticChunk.validate_and_fill(flat)
        if err:
            raise AssertionError(f"Invalid metadata for chunk {i}: {err}")
        flat = obj.model_dump()
        # Remove all keys with value None
        flat = {k: v for k, v in flat.items() if v is not None}
        flat_chunks.append(flat)

    # 4. Write chunks to both vector stores
    for db_url in ["http://localhost:3007", "http://localhost:8007"]:
        vclient = await create_vector_client(base_url=db_url)
        for flat in flat_chunks:
            try:
                await vclient.create_text_record(text=flat["text"], metadata=flat)
            except Exception as e:
                import pprint
                pprint.pprint(flat)
                raise AssertionError(f"Vector store error on {db_url}: {e}")
        await vclient._client.aclose()

    # 5. Query retriever
    response, err = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=source_id
    )
    assert err == "" or response is not None
    # Validate all returned chunks
    if response and "chunks" in response:
        for chunk in response["chunks"]:
            FlatSemanticChunk(**chunk)
    # 6. Check that returned chunks match what was written
    returned_texts = {c["text"] for c in response["chunks"]}
    original_texts = {flat["text"] for flat in flat_chunks}
    assert original_texts.issubset(returned_texts) 