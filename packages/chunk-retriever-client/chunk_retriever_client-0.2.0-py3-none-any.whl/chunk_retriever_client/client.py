"""
Chunk Retriever asynchronous client implementation.
"""
from typing import Optional, Tuple, Any, Union
import aiohttp
import asyncio
import uuid
import re
from chunk_metadata_adapter import FlatSemanticChunk

class ChunkRetrieverClient:
    """
    Asynchronous client for Chunk Retriever microservice.
    """
    @classmethod
    async def find_chunks_by_source_id(
        cls,
        url: str,
        port: int,
        source_id: Union[str, uuid.UUID]
    ) -> Tuple[Optional[Any], str]:
        """
        Query the Chunk Retriever by source_id.
        Returns (response, errstr): response is the parsed JSON or None, errstr is error description or empty string.
        source_id can be a UUID4 string or uuid.UUID object.
        """
        # Validate URL
        if not isinstance(url, str) or not re.match(r"^https?://[\w\.-]+", url):
            return None, "Invalid URL: must start with http:// or https:// and be a valid hostname"
        # Validate port
        if not isinstance(port, int) or not (1 <= port <= 65535):
            return None, "Invalid port: must be integer in range 1-65535"
        # Accept source_id as str or uuid.UUID
        if isinstance(source_id, uuid.UUID):
            source_id_str = str(source_id)
        elif isinstance(source_id, str):
            source_id_str = source_id
        else:
            return None, "source_id must be a string or uuid.UUID object"
        # Validate source_id as UUID4
        try:
            val = uuid.UUID(source_id_str, version=4)
            if str(val) != source_id_str:
                return None, "source_id must be a valid UUID4 string or uuid.UUID object"
        except Exception:
            return None, "source_id must be a valid UUID4 string or uuid.UUID object"
        # Prepare request
        endpoint = f"{url}:{port}/cmd"
        payload = {
            "jsonrpc": "2.0",
            "method": "find_chunks_by_source_id",
            "params": {"source_id": source_id_str},
            "id": 1
        }
        headers = {"Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload, headers=headers, timeout=10) as resp:
                    if resp.status != 200:
                        return None, f"Server returned status {resp.status}"
                    try:
                        data = await resp.json()
                    except Exception as e:
                        return None, f"Invalid JSON response: {e}"
                    if "error" in data:
                        return None, data["error"].get("message", str(data["error"]))
                    # Validate metadata in response (if present)
                    result = data.get("result")
                    if result and "chunks" in result:
                        try:
                            for chunk in result["chunks"]:
                                FlatSemanticChunk(**chunk)
                        except Exception as e:
                            return None, f"Invalid chunk metadata in response: {e}"
                    return result, ""
        except asyncio.TimeoutError:
            return None, "Request timed out"
        except aiohttp.ClientError as e:
            return None, f"Network error: {e}"
        except Exception as e:
            return None, f"Unexpected error: {e}" 