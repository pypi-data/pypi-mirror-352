"""Index service for managing code indexes.

This module provides the IndexService class which handles the business logic for
creating, listing, and running code indexes. It orchestrates the interaction between the
file system, database operations (via IndexRepository), and provides a clean API for
index management.
"""

from datetime import datetime
from pathlib import Path

import pydantic
import structlog
from tqdm.asyncio import tqdm

from kodit.bm25.keyword_search_service import BM25Document, KeywordSearchProvider
from kodit.embedding.vector_search_service import (
    VectorSearchRequest,
    VectorSearchService,
)
from kodit.indexing.indexing_models import Snippet
from kodit.indexing.indexing_repository import IndexRepository
from kodit.snippets.snippets import SnippetService
from kodit.source.source_service import SourceService
from kodit.util.spinner import Spinner

# List of MIME types that are blacklisted from being indexed
MIME_BLACKLIST = ["unknown/unknown"]


class IndexView(pydantic.BaseModel):
    """Data transfer object for index information.

    This model represents the public interface for index data, providing a clean
    view of index information without exposing internal implementation details.
    """

    id: int
    created_at: datetime
    updated_at: datetime | None = None
    source: str | None = None
    num_snippets: int | None = None


class IndexService:
    """Service for managing code indexes.

    This service handles the business logic for creating, listing, and running code
    indexes. It coordinates between file system operations, database operations (via
    IndexRepository), and provides a clean API for index management.
    """

    def __init__(
        self,
        repository: IndexRepository,
        source_service: SourceService,
        keyword_search_provider: KeywordSearchProvider,
        vector_search_service: VectorSearchService,
    ) -> None:
        """Initialize the index service.

        Args:
            repository: The repository instance to use for database operations.
            source_service: The source service instance to use for source validation.

        """
        self.repository = repository
        self.source_service = source_service
        self.snippet_service = SnippetService()
        self.log = structlog.get_logger(__name__)
        self.keyword_search_provider = keyword_search_provider
        self.code_search_service = vector_search_service

    async def create(self, source_id: int) -> IndexView:
        """Create a new index for a source.

        This method creates a new index for the specified source, after validating
        that the source exists and doesn't already have an index.

        Args:
            source_id: The ID of the source to create an index for.

        Returns:
            An Index object representing the newly created index.

        Raises:
            ValueError: If the source doesn't exist or already has an index.

        """
        # Check if the source exists
        source = await self.source_service.get(source_id)

        # Check if the index already exists
        index = await self.repository.get_by_source_id(source.id)
        if not index:
            index = await self.repository.create(source.id)
        return IndexView(
            id=index.id,
            created_at=index.created_at,
        )

    async def list_indexes(self) -> list[IndexView]:
        """List all available indexes with their details.

        Returns:
            A list of Index objects containing information about each index,
            including file and snippet counts.

        """
        indexes = await self.repository.list_indexes()

        # Transform database results into DTOs
        return [
            IndexView(
                id=index.id,
                created_at=index.created_at,
                updated_at=index.updated_at,
                num_snippets=await self.repository.num_snippets_for_index(index.id),
                source=source.uri,
            )
            for index, source in indexes
        ]

    async def run(self, index_id: int) -> None:
        """Run the indexing process for a specific index."""
        # Get and validate index
        index = await self.repository.get_by_id(index_id)
        if not index:
            msg = f"Index not found: {index_id}"
            raise ValueError(msg)

        # Create snippets for supported file types
        await self._create_snippets(index_id)

        snippets = await self.repository.get_all_snippets(index_id)

        self.log.info("Creating keyword index")
        with Spinner():
            await self.keyword_search_provider.index(
                [
                    BM25Document(snippet_id=snippet.id, text=snippet.content)
                    for snippet in snippets
                ]
            )

        self.log.info("Creating semantic code index")
        with Spinner():
            await self.code_search_service.index(
                [
                    VectorSearchRequest(snippet.id, snippet.content)
                    for snippet in snippets
                ]
            )

        # Update index timestamp
        await self.repository.update_index_timestamp(index)

    async def _create_snippets(
        self,
        index_id: int,
    ) -> None:
        """Create snippets for supported files.

        Args:
            index: The index to create snippets for.
            file_list: List of files to create snippets from.
            existing_snippets_set: Set of file IDs that already have snippets.

        """
        files = await self.repository.files_for_index(index_id)
        self.log.info("Creating snippets for files", index_id=index_id)
        for file in tqdm(files, total=len(files), leave=False):
            # Skip unsupported file types
            if file.mime_type in MIME_BLACKLIST:
                self.log.debug("Skipping mime type", mime_type=file.mime_type)
                continue

            # Create snippet from file content
            try:
                snippets = self.snippet_service.snippets_for_file(
                    Path(file.cloned_path)
                )
            except ValueError as e:
                self.log.debug("Skipping file", file=file.cloned_path, error=e)
                continue

            for snippet in snippets:
                s = Snippet(
                    index_id=index_id,
                    file_id=file.id,
                    content=snippet.text,
                )
                await self.repository.add_snippet_or_update_content(s)
