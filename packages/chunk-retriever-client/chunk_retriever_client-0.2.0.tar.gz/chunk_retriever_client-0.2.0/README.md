# chunk_retriever_client

Asynchronous Python client for the Chunk Retriever microservice.

## Installation
```bash
pip install chunk_retriever_client
```

## Usage Example
```python
import asyncio
from chunk_retriever_client.client import ChunkRetrieverClient

async def main():
    response, errstr = await ChunkRetrieverClient.find_chunks_by_source_id(
        url="http://localhost", port=8010, source_id="b7e2c4a0-1234-4f56-8abc-1234567890ab"
    )
    print("Response:", response)
    print("Error:", errstr)

asyncio.run(main())
```

## License
MIT
