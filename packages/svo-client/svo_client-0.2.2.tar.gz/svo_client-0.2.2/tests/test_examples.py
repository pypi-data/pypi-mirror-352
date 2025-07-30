import pytest
import asyncio
from svo_client.chunker_client import ChunkerClient, ChunkFull
import sys
import types

@pytest.mark.asyncio
async def test_example_usage(monkeypatch):
    # Мокаем методы клиента
    async def fake_chunk_text(self, text, **params):
        return [ChunkFull(uuid="1", text="Hello, ", sha256="x", ordinal=0), ChunkFull(uuid="2", text="world!", sha256="y", ordinal=1)]
    async def fake_health(self):
        return {"status": "ok"}
    async def fake_get_help(self, cmdname=None):
        return {"help": "info"}
    # Подмена методов
    monkeypatch.setattr(ChunkerClient, "chunk_text", fake_chunk_text)
    monkeypatch.setattr(ChunkerClient, "health", fake_health)
    monkeypatch.setattr(ChunkerClient, "get_help", fake_get_help)

    async with ChunkerClient() as client:
        chunks = await client.chunk_text("test")
        assert isinstance(chunks, list)
        assert all(isinstance(c, ChunkFull) for c in chunks)
        text = client.reconstruct_text(chunks)
        assert text == "Hello, world!"
        health = await client.health()
        assert health["status"] == "ok"
        help_info = await client.get_help()
        assert help_info["help"] == "info"

def test_example_usage_handles_validation_error(monkeypatch, capsys):
    import svo_client.examples.example_usage as example_usage
    from chunk_metadata_adapter import SemanticChunk
    def fake_validate_and_fill(data):
        return None, {'error': 'Fake validation error', 'fields': {}}
    monkeypatch.setattr(SemanticChunk, "validate_and_fill", staticmethod(fake_validate_and_fill))
    # Патчим chunk_text, чтобы выбрасывал ValueError
    async def fake_chunk_text(*args, **kwargs):
        raise ValueError("Chunk does not validate against chunk_metadata_adapter.SemanticChunk: Fake validation error")
    class FakeClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def chunk_text(self, *a, **k): return await fake_chunk_text()
        async def health(self): return {"status": "ok"}
        async def get_help(self): return {"help": "info"}
        def reconstruct_text(self, chunks): return ""
    monkeypatch.setattr(example_usage, "ChunkerClient", lambda *a, **k: FakeClient())
    import asyncio
    asyncio.run(example_usage.main())
    out = capsys.readouterr().out
    assert "Validation error:" in out 