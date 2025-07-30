import pytest
import asyncio
from svo_client.chunker_client import ChunkerClient, ChunkFull, Token, SV
from typing import List
import aiohttp
import sys
import types
import uuid
from datetime import datetime, timezone
from chunk_metadata_adapter import SemanticChunk

def make_valid_chunk(**overrides):
    # Автоматически формируем валидный чанк по модели SemanticChunk
    fields = SemanticChunk.model_fields
    base = {}
    for k in fields:
        if k == "uuid":
            base[k] = str(uuid.uuid4())
        elif k == "type":
            base[k] = "DocBlock"
        elif k == "text":
            base[k] = "Hello, "
        elif k == "sha256":
            base[k] = "a" * 64  # валидный sha256
        elif k == "language":
            base[k] = "en"
        elif k == "created_at":
            base[k] = datetime.now(timezone.utc).isoformat()
        elif k == "status":
            base[k] = "new"
        elif k == "start":
            base[k] = 0
        elif k == "end":
            base[k] = 6
        elif k == "metrics":
            base[k] = {}
        elif k == "links":
            base[k] = []
        elif k == "tags":
            base[k] = []  # всегда список
        elif k == "embedding":
            base[k] = [1.0]
        elif k == "role":
            base[k] = "user"
        elif k == "project":
            base[k] = "proj"
        elif k == "task_id":
            base[k] = "task"
        elif k == "subtask_id":
            base[k] = "subtask"
        elif k == "unit_id":
            base[k] = "unit"
        elif k == "source_id":
            base[k] = str(uuid.uuid4())
        elif k == "source_path":
            base[k] = "/path"
        elif k == "source_lines":
            base[k] = [1, 2]
        elif k == "ordinal":
            base[k] = 0
        elif k == "chunking_version":
            base[k] = "1.0"
        elif k == "summary":
            base[k] = "summary"
        else:
            base[k] = None
    base.update(overrides)
    # Добавляем вложенные структуры для теста
    base["tokens"] = [{"text": base["text"]}]
    base["block"] = [{"text": base["text"]}]
    base["sv"] = {"subject": {"text": base["text"]}, "verb": {"text": "is"}}
    return base

@pytest.mark.asyncio
async def test_chunk_text_and_reconstruct(monkeypatch):
    fake_chunks = [
        make_valid_chunk(text="Hello, ", ordinal=0, embedding=[1.0], sha256="x"),
        make_valid_chunk(text="world!", ordinal=1, embedding=[2.0], sha256="y")
    ]
    class FakeResponse:
        def __init__(self, data): self._data = data
        async def json(self): return {"result": {"chunks": self._data}}
        def raise_for_status(self): pass
    class FakeSession:
        def __init__(self): self.last_url = None; self.last_json = None
        def post(self, url, json):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse(fake_chunks)
                async def __aexit__(self_, exc_type, exc, tb): pass
            self.last_url = url; self.last_json = json
            return _Ctx()
        def get(self, url):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse({"openapi": "3.0.2"})
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    # chunk_text
    chunks = await client.chunk_text("Hello, world!")
    assert isinstance(chunks, list)
    assert all(isinstance(c, ChunkFull) for c in chunks)
    assert chunks[0].text == "Hello, "
    assert chunks[1].text == "world!"
    # reconstruct_text
    text = client.reconstruct_text(chunks)
    assert text == "Hello, world!"
    # Проверка вложенных структур
    assert isinstance(chunks[0].tokens[0], Token)
    assert isinstance(chunks[0].sv, SV)
    assert chunks[0].sv.subject.text == "Hello, "
    assert chunks[1].sv.verb.text == "is"

@pytest.mark.asyncio
async def test_get_openapi_schema(monkeypatch):
    class FakeResponse:
        async def json(self): return {"openapi": "3.0.2"}
        def raise_for_status(self): pass
    class FakeSession:
        def get(self, url):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    schema = await client.get_openapi_schema()
    assert schema["openapi"] == "3.0.2"

@pytest.mark.asyncio
async def test_get_help(monkeypatch):
    class FakeResponse:
        async def json(self): return {"result": {"commands": {"chunk": {}}}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    help_info = await client.get_help()
    assert "commands" in help_info["result"]

@pytest.mark.asyncio
async def test_health(monkeypatch):
    class FakeResponse:
        async def json(self): return {"result": {"success": True}}
        def raise_for_status(self): pass
    class FakeSession:
        def post(self, url, json):
            class _Ctx:
                async def __aenter__(self_): return FakeResponse()
                async def __aexit__(self_, exc_type, exc, tb): pass
            return _Ctx()
        async def close(self): pass
    client = ChunkerClient()
    client.session = FakeSession()
    health = await client.health()
    assert health["result"]["success"] is True

# Интеграционный тест (если сервер доступен)
@pytest.mark.asyncio
async def test_chunk_text_integration():
    try:
        async with ChunkerClient() as client:
            chunks = await client.chunk_text("Integration test.")
            assert isinstance(chunks, list)
            assert all(isinstance(c, ChunkFull) for c in chunks)
            if chunks:
                assert hasattr(chunks[0], "text")
    except aiohttp.ClientConnectorError:
        pytest.skip("Chunker server not available for integration test.")

def test_parse_chunk_validation_error(monkeypatch):
    # Подделываем validate_and_fill, чтобы всегда возвращать ошибку
    from chunk_metadata_adapter import SemanticChunk
    def fake_validate_and_fill(data):
        return None, {'error': 'Fake validation error', 'fields': {}}
    monkeypatch.setattr(SemanticChunk, "validate_and_fill", staticmethod(fake_validate_and_fill))
    from svo_client.chunker_client import ChunkerClient  # импорт после monkeypatch!
    client = ChunkerClient()
    invalid_chunk = make_valid_chunk()
    try:
        client.parse_chunk(invalid_chunk)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Fake validation error" in str(e) 