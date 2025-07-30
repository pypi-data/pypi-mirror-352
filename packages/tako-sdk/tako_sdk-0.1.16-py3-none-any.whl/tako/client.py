import os
from typing import List, Optional
import requests
import httpx

from tako.types.common.exceptions import (
    RelevantResultsNotFoundException,
    raise_exception_from_response,
)
from tako.types.knowledge_search.types import (
    KnowledgeSearchOutputs,
    KnowledgeSearchResults,
    KnowledgeSearchSourceIndex,
)
from tako.types.visualize.types import TakoDataFormatDataset, VisualizeRequest

TAKO_API_KEY = os.getenv("TAKO_API_KEY", None)
TAKO_SERVER_URL = os.getenv("TAKO_SERVER_URL", "https://trytako.com/")
TAKO_API_VERSION = os.getenv("TAKO_API_VERSION", "v1")


class TakoClient:
    def __init__(
        self,
        api_key: Optional[str] = TAKO_API_KEY,
        server_url: Optional[str] = TAKO_SERVER_URL,
        api_version: Optional[str] = TAKO_API_VERSION,
    ):
        assert api_key is not None, "API key is required"
        self.api_key = api_key
        self.server_url = server_url
        self.api_version = api_version

    def knowledge_search(
        self,
        text: str,
        source_indexes: Optional[List[KnowledgeSearchSourceIndex]] = [
            KnowledgeSearchSourceIndex.TAKO,
        ],
    ) -> KnowledgeSearchResults:
        """
        Search for knowledge cards based on a text query.

        Args:
            text: The text to search for.
            source_indexes: The source indexes to search for.

        Returns:
            A list of knowledge search results.

        Raises:
            APIException: If the API returns an error.
        """
        url = f"{self.server_url}/api/{self.api_version}/knowledge_search"
        payload = {
            "inputs": {
                "text": text,
            },
        }
        if source_indexes:
            payload["source_indexes"] = source_indexes

        response = requests.post(url, json=payload, headers={"X-API-Key": self.api_key})
        try:
            # Based on the response, raise an exception if the response is an error
            raise_exception_from_response(response)
        except RelevantResultsNotFoundException:
            # For cases where no relevant results are found, return an empty list
            # instead of raising an exception
            return KnowledgeSearchResults(
                outputs=KnowledgeSearchOutputs(knowledge_cards=[])
            )

        return KnowledgeSearchResults.model_validate(response.json())

    def get_image(self, card_id: str) -> bytes:
        """
        Get an image for a knowledge card.

        Args:
            card_id: The ID of the knowledge card.

        Returns:
            The image as bytes.
        """
        url = f"{self.server_url}/api/{self.api_version}/image/{card_id}/"
        response = requests.get(
            url,
            headers={
                "Accept": "image/*",
            },
        )
        return response.content

    def beta_visualize(
        self, tako_formatted_dataset: TakoDataFormatDataset
    ) -> KnowledgeSearchResults:
        url = f"{self.server_url}/api/{self.api_version}/beta/visualize"
        visualize_request = VisualizeRequest(
            tako_formatted_dataset=tako_formatted_dataset,
        )
        payload = visualize_request.model_dump()
        response = requests.post(url, json=payload, headers={"X-API-Key": self.api_key})
        raise_exception_from_response(response)
        return KnowledgeSearchResults.model_validate(response.json())


class AsyncTakoClient:
    def __init__(
        self,
        api_key: Optional[str] = TAKO_API_KEY,
        server_url: Optional[str] = TAKO_SERVER_URL,
        api_version: Optional[str] = TAKO_API_VERSION,
        default_timeout_seconds: Optional[float] = 30.0,
    ):
        assert api_key is not None, "API key is required"
        self.api_key = api_key
        self.server_url = server_url.strip("/")
        self.api_version = api_version
        self.default_timeout_seconds = default_timeout_seconds

    async def knowledge_search(
        self,
        text: str,
        source_indexes: Optional[List[KnowledgeSearchSourceIndex]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> KnowledgeSearchResults:
        """
        Async search for knowledge cards based on a text query.

        Args:
            text: The text to search for.
            source_indexes: The source indexes to search for.

        Returns:
            A list of knowledge search results.

        Raises:
            APIException: If the API returns an error.
        """
        # Trailing slash is required for httpx
        url = f"{self.server_url}/api/{self.api_version}/knowledge_search/"
        payload = {
            "inputs": {
                "text": text,
            },
        }
        if source_indexes:
            payload["source_indexes"] = source_indexes

        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.post(
                url, json=payload, headers={"X-API-Key": self.api_key}
            )
            return KnowledgeSearchResults.model_validate(response.json())

    async def get_image(
        self, card_id: str, timeout_seconds: Optional[float] = None
    ) -> bytes:
        """
        Async get an image for a knowledge card.

        Args:
            card_id: The ID of the knowledge card.

        Returns:
            The image as bytes.
        """
        # Trailing slash is required for httpx
        url = f"{self.server_url}/api/{self.api_version}/image/{card_id}/"
        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.get(
                url,
                headers={
                    "Accept": "image/*",
                },
            )
            return response.content

    async def beta_visualize(
        self,
        tako_formatted_dataset: TakoDataFormatDataset,
        timeout_seconds: Optional[float] = None,
    ) -> KnowledgeSearchResults:
        url = f"{self.server_url}/api/{self.api_version}/beta/visualize"
        visualize_request = VisualizeRequest(
            tako_formatted_dataset=tako_formatted_dataset,
        )
        payload = visualize_request.model_dump()
        async with httpx.AsyncClient(
            timeout=timeout_seconds or self.default_timeout_seconds
        ) as client:
            response = await client.post(
                url, json=payload, headers={"X-API-Key": self.api_key}
            )
            raise_exception_from_response(response)
            return KnowledgeSearchResults.model_validate(response.json())
