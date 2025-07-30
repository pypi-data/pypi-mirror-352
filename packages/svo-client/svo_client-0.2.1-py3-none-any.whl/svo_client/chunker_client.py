"""Async client for SVO semantic chunker microservice."""

__version__ = "0.2.1"

import aiohttp
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class Token(BaseModel):
    text: str
    lemma: Optional[str] = None
    pos: Optional[str] = None
    head: Optional[int] = None
    deprel: Optional[str] = None
    id: Optional[int] = None
    sent_id: Optional[str] = None

class SV(BaseModel):
    subject: Optional[Token] = None
    verb: Optional[Token] = None

class ChunkFull(BaseModel):
    uuid: str
    source_id: Optional[str] = None
    ordinal: Optional[int] = None
    sha256: str
    text: str
    summary: Optional[str] = None
    language: Optional[str] = None
    type: Optional[str] = None
    source_path: Optional[str] = None
    source_lines_start: Optional[int] = None
    source_lines_end: Optional[int] = None
    project: Optional[str] = None
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None
    status: Optional[str] = None
    unit_id: Optional[str] = None
    created_at: Optional[str] = None
    tags: Optional[Any] = None
    role: Optional[str] = None
    link_parent: Optional[str] = None
    link_related: Optional[str] = None
    quality_score: Optional[float] = None
    coverage: Optional[float] = None
    cohesion: Optional[float] = None
    boundary_prev: Optional[float] = None
    boundary_next: Optional[float] = None
    used_in_generation: Optional[bool] = None
    feedback_accepted: Optional[int] = None
    feedback_rejected: Optional[int] = None
    start: Optional[int] = None
    end: Optional[int] = None
    sv: Optional[SV] = None
    score: Optional[float] = None
    embedding: Optional[List[float]] = None
    tokens: Optional[List[Token]] = None
    block: Optional[List[Token]] = None

class ChunkerClient:
    def __init__(self, url: str = "http://localhost", port: int = 8009):
        self.base_url = f"{url.rstrip('/')}: {port}"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def get_openapi_schema(self) -> Any:
        url = f"{self.base_url}/openapi.json"
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()

    def parse_chunk(self, chunk: Dict[str, Any]) -> ChunkFull:
        tokens = [Token(**t) for t in chunk.get("tokens", [])] if chunk.get("tokens") else None
        block = [Token(**t) for t in chunk.get("block", [])] if chunk.get("block") else None
        sv = None
        if chunk.get("sv"):
            sv = SV(**{
                k: Token(**v) if v else None
                for k, v in chunk["sv"].items()
            })
        chunk_full = ChunkFull(
            **{k: v for k, v in chunk.items() if k not in ("tokens", "block", "sv")},
            tokens=tokens,
            block=block,
            sv=sv
        )
        # Validate with SemanticChunk from chunk_metadata_adapter
        try:
            from chunk_metadata_adapter import SemanticChunk
            _, err = SemanticChunk.validate_and_fill({k: v for k, v in chunk.items() if k in SemanticChunk.model_fields})
            if err:
                raise ValueError(f"Chunk does not validate against chunk_metadata_adapter.SemanticChunk: {err}\nChunk: {chunk}")
        except Exception as e:
            raise ValueError(f"Chunk does not validate against chunk_metadata_adapter.SemanticChunk: {e}\nChunk: {chunk}")
        return chunk_full

    async def chunk_text(self, text: str, **params) -> List[ChunkFull]:
        url = f"{self.base_url}/cmd"
        payload = {
            "jsonrpc": "2.0",
            "method": "chunk",
            "params": {"text": text, **params},
            "id": 1
        }
        async with self.session.post(url, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            chunks = data.get("result", {}).get("chunks", [])
            return [self.parse_chunk(chunk) for chunk in chunks]

    async def get_help(self, cmdname: Optional[str] = None) -> Any:
        url = f"{self.base_url}/cmd"
        payload = {
            "jsonrpc": "2.0",
            "method": "help",
            "id": 1
        }
        if cmdname:
            payload["params"] = {"cmdname": cmdname}
        async with self.session.post(url, json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def health(self) -> Any:
        url = f"{self.base_url}/cmd"
        payload = {
            "jsonrpc": "2.0",
            "method": "health",
            "id": 1
        }
        async with self.session.post(url, json=payload) as resp:
            resp.raise_for_status()
            return await resp.json()

    def reconstruct_text(self, chunks: List[ChunkFull]) -> str:
        """
        Reconstruct the original text from a list of ChunkFull objects.
        Склеивает текст из чанков в исходном порядке.
        """
        sorted_chunks = sorted(
            chunks,
            key=lambda c: c.ordinal if c.ordinal is not None else chunks.index(c)
        )
        return ''.join(chunk.text for chunk in sorted_chunks if chunk.text) 