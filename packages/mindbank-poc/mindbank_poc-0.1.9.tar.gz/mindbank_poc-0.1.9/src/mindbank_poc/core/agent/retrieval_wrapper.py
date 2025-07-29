from typing import Optional, List, Dict, Any, Tuple
from mindbank_poc.core.retrieval.service import SearchResultItemInternal
import logging
from mindbank_poc.core.agent.summarizer import map_reduce_summarize

logger = logging.getLogger(__name__)

class RetrievalWrapper:
    """
    Wrapper for integrating agent logic with the RetrievalService.
    Provides methods for context search with advanced filters (archetype, source, author, metadata, etc).
    """

    def __init__(self, retrieval_service: Any):
        self.retrieval_service = retrieval_service

    async def search_context(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        sort_by: Optional[str] = "score",
        sort_order: Optional[str] = "desc",
        max_total_chars: int = 4000,
        use_summarizer: bool = True
    ) -> Tuple[List[str], Optional[str]]:
        """
        Search for relevant context using the retrieval service.
        Supports query + advanced filters.
        
        Args:
            query: The search query text
            filters: Dictionary of filters to apply
            limit: Maximum number of results to return
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            max_total_chars: Maximum characters in summarized context
            use_summarizer: Whether to use LLM summarization (vs truncation)
            
        Returns:
            A tuple of (raw_results_list, summarized_context)
            where summarized_context is the map-reduced summary of all results
        """
        results_text: List[str] = []
        internal_results: List[SearchResultItemInternal] = []

        if query:
            # If query is present, use retrieval_service.search
            # Extract archetype and search_mode from filters if they exist
            _filters = filters.copy() if filters else {}
            # Support list of connector/source IDs via 'source_ids'
            source_ids: Optional[List[str]] = _filters.pop("source_ids", None)

            archetype = _filters.pop("archetype", None) if _filters else None
            search_mode = _filters.pop("search_mode", "hybrid") if _filters else "hybrid"
            
            # Remaining _filters are considered metadata_filters
            metadata_filters = _filters if _filters else None

            # If explicit source_ids provided, encode into metadata_filters (connector_id)
            if source_ids:
                # If only one id, simple string; else join with | for now (future: list support)
                # RetrievalService._search converts values to str, no list support yet.
                # We'll pass first ID to narrow search; TODO: enhance RetrievalService for list filters.
                metadata_filters = metadata_filters or {}
                metadata_filters["connector_id"] = source_ids[0]

            internal_results = await self.retrieval_service.search(
                query_text=query,
                metadata_filters=metadata_filters,
                archetype=archetype,
                search_mode=search_mode,
                limit=limit
            )
        elif filters:
            print(f"RetrievalWrapper: Filters: {filters}")
            # If query is None but filters are present, use retrieval_service.filter_search
            # Unpack filters dict for filter_search arguments
            archetype = filters.get("archetype")
            source = filters.get("source")
            source_name = filters.get("source_name")
            author = filters.get("author")
            date_from = filters.get("date_from")
            date_to = filters.get("date_to")
            classification_types = filters.get("classification_types")
            custom_metadata = filters.get("custom_metadata")
            tags = filters.get("tags")
            
            internal_results = await self.retrieval_service.filter_search(
                archetype=archetype,
                source=source,
                source_name=source_name,
                author=author,
                date_from=date_from,
                date_to=date_to,
                classification_types=classification_types,
                custom_metadata=custom_metadata,
                tags=tags,
                limit=limit,
                sort_by=sort_by,
                sort_order=sort_order
            )
        else:
            # No query and no filters, return empty list or handle as an error/default search?
            # For now, return empty list.
            return [], None

        for item in internal_results:
            if item.unit:
                content = item.unit.text_repr
                results_text.append(content)
        
        # Generate summarized context if documents were found
        summarized_context = None
        if results_text:
            try:
                if use_summarizer:
                    # Use map-reduce summarization
                    logger.info(f"Summarizing {len(results_text)} documents using map-reduce")
                    summarized_context = await map_reduce_summarize(
                        documents=results_text, 
                        max_total_chars=max_total_chars
                    )
                    logger.info(f"Generated summary of {len(summarized_context)} chars")
                else:
                    # Simple truncation approach (previous method)
                    logger.info(f"Using simple truncation for {len(results_text)} documents")
                    trimmed_docs = [doc[:300] for doc in results_text]
                    combined = []
                    current_len = 0
                    for d in trimmed_docs:
                        if current_len + len(d) + 10 > max_total_chars:
                            break
                        combined.append(d)
                        current_len += len(d) + 10
                    summarized_context = "\n\n---\n\n".join(combined)
            except Exception as e:
                logger.error(f"Error summarizing context: {e}", exc_info=True)
                # Fallback to simple truncation on error
                first_few_docs = results_text[:min(5, len(results_text))]
                summarized_context = "\n\n---\n\n".join([d[:300] for d in first_few_docs])
                if len(summarized_context) > max_total_chars:
                    summarized_context = summarized_context[:max_total_chars] + "..."
        
        return results_text, summarized_context
