import json
import logging
from typing import Optional, Generator

from r2r.core import (RAGPipeline, GenerationConfig, LLMProvider, LoggingDatabaseConnection,
                      RAGPipelineOutput, VectorDBProvider, VectorSearchResult,
                      log_execution_to_db)
from r2r.embeddings import OpenAIEmbeddingProvider
from r2r.pipelines import BasicRAGPipeline, BasicPromptProvider

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_TASK_PROMPT = """
## Task:
Answer the query given immediately below given the context which follows later. Use line item references to like [1], [2], ... refer to specifically numbered items in the provided context. Pay close attention to the title of each given source to ensure it is consistent with the query.

### Query:
{query}

### Context:
{context}

### Query:
{query}

REMINDER - Use line item references to like [1], [2], ... refer to specifically numbered items in the provided context.
## Response:
"""


class AutoContextRAGPipelineOutput(RAGPipelineOutput):
    def __init__(self, search_results, context, completion):
        
        self.search_results = self.filter_search_results(search_results)
        self.context = context
        self.completion = completion
        
    def filter_search_results(self, search_results):
        # add url, visit date, title, snippet
        filtered_results = []
        for result in search_results:
            print(result)
            metadata = result.metadata
            url = metadata['url']
            title = metadata['title']
            text = metadata['text']
            formatted_result = f"URL: {url}\nnTitle: {title}\Context: {text}"
            print(formatted_result)
            filtered_results.append(formatted_result)
        return "\n\n".join(filtered_results)


class AutoContextRAGPipeline(BasicRAGPipeline):
    def __init__(
        self,
        llm: LLMProvider,
        db: VectorDBProvider,
        embedding_model: str,
        embeddings_provider: OpenAIEmbeddingProvider,
        logging_connection: Optional[LoggingDatabaseConnection] = None,
        system_prompt: Optional[str] = DEFAULT_SYSTEM_PROMPT,
        task_prompt: Optional[str] = DEFAULT_TASK_PROMPT,
    ) -> None:
        logger.debug(f"Initalizing `AutoContextRAGPipeline`")

        super().__init__(
            llm,
            db,
            embedding_model,
            embeddings_provider,
            logging_connection=logging_connection,
            prompt_provider=BasicPromptProvider(system_prompt, task_prompt)
        )

    @log_execution_to_db
    def search(
        self,
        query: str,
        filters: dict,
        limit: int,
    ) -> list[VectorSearchResult]:
        logger.debug(f"Retrieving results for query: {query}")

        results = self.db.search(
            query_vector=self.embeddings_provider.get_embedding(
                query,
                self.embedding_model,
            ),
            filters=filters,
            limit=limit,
        )
        logger.debug(f"Retrieved the raw results shown:\n{results}\n")
        return results

    @log_execution_to_db
    def construct_context(
        self,
        results: list,
    ) -> str:
        # url, visit time, title, snippet
        context = ""
        for result in results:
            context += f"## URL:\n{result.metadata['url']}\n\n## Visit Time:\n{result.metadata['visit_time']}\n\n## Title:\n{result.metadata['title']}\n\n## Snippet:\n{result.metadata['snippet']}\n\n"
        return context

    # Modifies `SyntheticRAGPipeline` run to return search_results and completion
    def run(
        self,
        query,
        filters={},
        limit=5,
        search_only=True,
        generation_config: Optional[GenerationConfig] = None,
        *args,
        **kwargs,
    ):
        """
        Runs the completion pipeline.
        """
        if not generation_config:
            generation_config = GenerationConfig(model="gpt-3.5-turbo")

        self.initialize_pipeline(query, search_only)
        search_results = self.search(query, filters, limit)
            
        return AutoContextRAGPipelineOutput(search_results, None, None)


