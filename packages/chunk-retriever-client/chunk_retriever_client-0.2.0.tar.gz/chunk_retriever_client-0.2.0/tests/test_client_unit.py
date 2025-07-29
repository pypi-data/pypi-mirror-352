import pytest
import uuid
import asyncio
from chunk_retriever_client.client import ChunkRetrieverClient

@pytest.mark.asyncio
@pytest.mark.parametrize("url,port,source_id,err_substr", [
    ("localhost", 8010, str(uuid.uuid4()), "Invalid URL"),
    ("http://localhost", 70000, str(uuid.uuid4()), "Invalid port"),
    ("http://localhost", 8010, "not-a-uuid", "UUID4"),
    ("http://localhost", 8010, 12345, "uuid.UUID object"),
    ("http://localhost", 8010, uuid.uuid1(), "UUID4"),
])
async def test_invalid_params(url, port, source_id, err_substr):
    resp, err = await ChunkRetrieverClient.find_chunks_by_source_id(url, port, source_id)
    assert resp is None
    assert err_substr in err

@pytest.mark.asyncio
async def test_network_error():
    # Unavailable server
    resp, err = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=9999, source_id=str(uuid.uuid4())
    )
    assert resp is None
    assert "Network error" in err or "timed out" in err or "Server returned status" in err 

@pytest.mark.asyncio
async def test_timeout(monkeypatch):
    class DummyResp:
        async def __aenter__(self): raise asyncio.TimeoutError()
        async def __aexit__(self, *a, **k): pass
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a, **k): pass
        def post(self, *a, **k): return DummyResp()
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **k: DummySession())
    resp, err = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=str(uuid.uuid4())
    )
    assert resp is None
    assert "timed out" in err

@pytest.mark.asyncio
async def test_invalid_json(monkeypatch):
    class DummyResp:
        status = 200
        async def json(self): raise Exception("not json")
        async def __aenter__(self): return self
        async def __aexit__(self, *a, **k): pass
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a, **k): pass
        def post(self, *a, **k): return DummyResp()
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **k: DummySession())
    resp, err = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=str(uuid.uuid4())
    )
    assert resp is None
    assert "Invalid JSON" in err

@pytest.mark.asyncio
async def test_error_key(monkeypatch):
    class DummyResp:
        status = 200
        async def json(self): return {"error": {"message": "fail"}}
        async def __aenter__(self): return self
        async def __aexit__(self, *a, **k): pass
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a, **k): pass
        def post(self, *a, **k): return DummyResp()
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **k: DummySession())
    resp, err = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=str(uuid.uuid4())
    )
    assert resp is None
    assert "fail" in err

@pytest.mark.asyncio
async def test_unexpected_exception(monkeypatch):
    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a, **k): pass
        def post(self, *a, **k): raise Exception("boom")
    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **k: DummySession())
    resp, err = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id=str(uuid.uuid4())
    )
    assert resp is None
    assert "Unexpected error" in err 