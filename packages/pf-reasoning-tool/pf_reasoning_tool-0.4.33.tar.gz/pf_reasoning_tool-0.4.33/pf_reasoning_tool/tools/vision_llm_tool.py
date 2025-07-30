# -*- coding: utf-8 -*-
# pf-reasoning-tool-proj/pf_reasoning_tool/tools/vision_llm_tool.py
'''
Vision-only Promptflow tool (GPT-4V / GPT-4o).  Single quotes.  Two spaces after full stop.
'''

from typing import Union, List, Optional

from promptflow.contracts.types import PromptTemplate
from promptflow.connections import AzureOpenAIConnection, OpenAIConnection
from promptflow.tools.exception import InvalidConnectionType
from promptflow.tools.common import handle_openai_error
from promptflow._internal import tool

# Vision wrappers shipped with Promptflow
from promptflow.tools.aoai_gpt4v import AzureOpenAI as AoaiVisionWrapper
from promptflow.tools.openai_gpt4v import OpenAI as OpenAIVisionWrapper


@handle_openai_error()
@tool(streaming_option_parameter='stream', return_names=['output'])
def vision_llm(
    connection: Union[AzureOpenAIConnection, OpenAIConnection],
    prompt: PromptTemplate,
    deployment_name: str = '',
    model: str = '',
    temperature: float = 0.7,
    top_p: float = 1.0,
    stream: bool = False,
    stop: Optional[List[str]] = None,
    max_tokens: Optional[int] = None,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    seed: Optional[int] = None,
    detail: str = 'auto',
    **kwargs,
) -> str:
    '''
    Call a vision-capable chat completion model and return the assistant message text.
    '''

    if isinstance(connection, AzureOpenAIConnection):
        client = AoaiVisionWrapper(connection)
        return client.chat(
            prompt=prompt,
            deployment_name=deployment_name,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            stop=stop,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            seed=seed,
            detail=detail,
            **kwargs,
        )

    if isinstance(connection, OpenAIConnection):
        client = OpenAIVisionWrapper(connection)
        return client.chat(
            prompt=prompt,
            model=model,
            temperature=temperature,
            top_p=top_p,
            stream=stream,
            stop=stop,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            seed=seed,
            detail=detail,
            **kwargs,
        )

    raise InvalidConnectionType(
        message=f'Unsupported connection type {type(connection).__name__}.  '
                f'Use AzureOpenAIConnection or OpenAIConnection.'
    )
