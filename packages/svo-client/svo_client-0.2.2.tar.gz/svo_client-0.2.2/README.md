# svo-client

Асинхронный Python-клиент для SVO Semantic Chunker microservice.

## Установка

```bash
pip install svo-client
```

## Пример использования

```python
from svo_client.chunker_client import ChunkerClient
import asyncio

async def main():
    async with ChunkerClient() as client:
        chunks = await client.chunk_text("Your text here.")
        print(client.reconstruct_text(chunks))

asyncio.run(main())
```

## Документация
- [OpenAPI schema](docs/openapi.json)
- [Примеры и тесты](tests/test_chunker_client.py)
