# -*- coding: utf-8 -*-
"""
HW AI Search Lookup Tool (Internal Embedding – Manual Input v1 – patched 2)
==========================================================================
Performs keyword, semantic, vector or hybrid search over Azure AI Search.  
Embeds queries internally using Azure OpenAI or OpenAI.  
User must type index, field and semantic names exactly.  
"""

from __future__ import annotations

import contextvars
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import List, Dict, Any, Optional, Tuple, Union

from promptflow.core import tool
from promptflow.connections import (
    CustomConnection,
    AzureOpenAIConnection,
    OpenAIConnection,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError
from azure.search.documents import SearchClient

try:
    from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
except ImportError:
    raise ImportError(
        'Could not import langchain_openai.  Install "langchain-openai" in your PromptFlow environment.'
    )

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO))

VALID_QUERY_TYPES = {'keyword', 'semantic', 'vector', 'hybrid', 'hybrid_semantic'}
DEFAULT_EMBED_MODEL = 'text-embedding-3-large'


def _extract_search_credentials(conn: CustomConnection) -> Tuple[str, str]:
    if not isinstance(conn, CustomConnection):
        raise TypeError(f'Expected CustomConnection, got {type(conn).__name__}')
    c = dict(conn)
    endpoint = (
        c.get('endpoint')
        or c.get('api_base')
        or c.get('azure_endpoint')
        or c.get('value1')
        or c.get('key1')
    )
    api_key_from_conn = (
        c.get('api_key') or c.get('value2') or c.get('key2') or c.get('key')
    )
    if not endpoint:
        raise ValueError('Azure AI Search endpoint not found in connection.')
    if not api_key_from_conn:
        raise ValueError('Azure AI Search API key not found in connection.')

    if api_key_from_conn == '***':
        api_key_from_conn = os.getenv('AZURE_SEARCH_KEY')
        if not api_key_from_conn:
            raise ValueError('API key is "***" and AZURE_SEARCH_KEY env var is not set.')

    return endpoint, api_key_from_conn


def _client(conn: CustomConnection, index_name: str) -> SearchClient:
    endpoint, key = _extract_search_credentials(conn)
    try:
        return SearchClient(endpoint, index_name, AzureKeyCredential(key))
    except ClientAuthenticationError as e:
        raise RuntimeError(
            f'Authentication failed connecting to index "{index_name}".  {e}'
        ) from e
    except Exception as e:
        raise RuntimeError(
            f'Could not connect to index "{index_name}".  {e}'
        ) from e


def _embeddings(conn: Union[AzureOpenAIConnection, OpenAIConnection], model: str):
    if isinstance(conn, AzureOpenAIConnection):
        endpoint = getattr(conn, 'azure_endpoint', None) or getattr(conn, 'api_base', None)
        api_key = conn.api_key if conn.api_key != '***' else os.getenv('AZURE_OPENAI_API_KEY')
        if not endpoint or not api_key:
            raise ValueError('Azure OpenAI connection missing endpoint or key.')
        return AzureOpenAIEmbeddings(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=getattr(conn, 'api_version', None) or '2024-02-01',
            azure_deployment=model,
        )
    if isinstance(conn, OpenAIConnection):
        api_key = conn.api_key if conn.api_key != '***' else os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('OpenAI key missing.')
        return OpenAIEmbeddings(api_key=api_key, base_url=getattr(conn, 'base_url', None), model=model)
    raise TypeError('Unsupported embeddings connection type.')


def _text_from_doc(doc: Dict[str, Any], text_field: str) -> str:
    return str(
        doc.get(text_field) or doc.get('content') or doc.get('text') or ''
    )


def _execute_search(
    query_text: str,
    search_client: SearchClient,
    index_name: str,
    query_type: str,
    top_k: int,
    text_field: str,
    vector_field: str,
    search_filters: Optional[str],
    select_fields: Optional[List[str]],
    semantic_config: Optional[str],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]],
    embedding_model_name: str,
) -> List[Dict[str, Any]]:
    needs_vec = query_type in {'vector', 'hybrid', 'hybrid_semantic'}
    needs_sem = query_type in {'semantic', 'hybrid_semantic'}

    vector: Optional[List[float]] = None
    if needs_vec:
        if not embeddings_connection:
            raise ValueError('Embeddings connection required for vector searches.')
        vector = _embeddings(embeddings_connection, embedding_model_name).embed_query(
            query_text
        )

    if needs_sem and not semantic_config:
        raise ValueError('Semantic configuration name required for semantic modes.')

    params: Dict[str, Any] = {
        'top': top_k,
        'filter': search_filters,
        'select': ','.join(select_fields) if select_fields else None,
        'include_total_count': False,
    }

    if query_type in {'keyword', 'semantic', 'hybrid', 'hybrid_semantic'}:
        params['search_text'] = query_text

    if needs_vec:
        if vector is None:
            raise RuntimeError('Vector was required but is None.')
        params['vector_queries'] = [
            {
                'kind': 'vector',      # ← mandatory for REST v2023-10-01-Preview and later
                'vector': vector,
                'k': top_k,
                'fields': vector_field,
            }
        ]
        if query_type == 'vector':
            params.pop('top', None)
            params.pop('search_text', None)

    if needs_sem:
        params['query_type'] = 'semantic'
        params['semantic_configuration_name'] = semantic_config

    params = {k: v for k, v in params.items() if v is not None}

    docs = list(search_client.search(**params))

    output: List[Dict[str, Any]] = []
    for d in docs:
        output.append(
            {
                'text': _text_from_doc(d, text_field),
                'vector': d.get(vector_field),
                'score': d.get('@search.score'),
                'metadata': {
                    k: v
                    for k, v in d.items()
                    if k not in {text_field, vector_field} and not k.startswith('@search.')
                },
                'original_entity': d,
            }
        )
    return output


@tool
def hw_ai_search_lookup_with_embed(
    connection: CustomConnection,
    index_name: str,
    queries: Union[str, List[str]],
    embeddings_connection: Optional[Union[AzureOpenAIConnection, OpenAIConnection]] = None,
    embedding_model_name: str = DEFAULT_EMBED_MODEL,
    query_type: str = 'hybrid',
    top_k: int = 3,
    text_field: str = 'content',
    vector_field: str = 'vector',
    search_filters: Optional[str] = None,
    select_fields: Optional[List[str]] = None,
    semantic_config: Optional[str] = None,
) -> List[List[Dict[str, Any]]]:
    if query_type not in VALID_QUERY_TYPES:
        raise ValueError(f'Invalid query_type "{query_type}".')
    if isinstance(queries, str):
        query_list = [queries]
    elif isinstance(queries, list) and all(isinstance(q, str) for q in queries):
        query_list = queries
    else:
        raise TypeError('queries must be a string or list of strings.')

    search_client = _client(connection, index_name)

    search_partial = partial(
        _execute_search,
        search_client=search_client,
        index_name=index_name,
        query_type=query_type,
        top_k=top_k,
        text_field=text_field,
        vector_field=vector_field,
        search_filters=search_filters,
        select_fields=select_fields,
        semantic_config=semantic_config,
        embeddings_connection=embeddings_connection,
        embedding_model_name=embedding_model_name,
    )

    parent_ctx = contextvars.copy_context()
    def _run(func, *a):
        return parent_ctx.run(func, *a)

    results_map = {}
    with ThreadPoolExecutor() as exe:
        fut_to_q = {exe.submit(_run, search_partial, q): q for q in query_list}
        for fut in fut_to_q:
            q = fut_to_q[fut]
            try:
                results_map[q] = fut.result()
            except Exception:
                results_map[q] = []

    return [results_map[q] for q in query_list]
