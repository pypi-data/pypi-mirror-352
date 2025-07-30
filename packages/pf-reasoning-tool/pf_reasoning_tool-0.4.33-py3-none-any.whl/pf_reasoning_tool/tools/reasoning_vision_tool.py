# -*- coding: utf-8 -*-
# pf_reasoning_tool/tools/reasoning_vision_tool.py
'''
Reasoning + Vision Promptflow tool.  Works with GPT-4o-vision (Azure or OpenAI).
Single quotes and two spaces after full stop, as requested.
'''

from typing import Union, List, Dict, Optional
import re
from jinja2 import Template
from openai import AzureOpenAI, OpenAI
from promptflow.core import tool
from promptflow.connections import CustomConnection, AzureOpenAIConnection, OpenAIConnection
from promptflow.contracts.types import PromptTemplate


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def get_client(connection: Union[CustomConnection, AzureOpenAIConnection, OpenAIConnection]):
    '''Return an OpenAI or AzureOpenAI client.  Forces 2025-01-01-preview for AOAI.'''
    if not connection:
        raise ValueError('Connection object is required.')

    # Support both dict-like and attribute-style connections
    try:
        connection_dict = dict(connection)
    except (TypeError, ValueError):
        connection_dict = {
            'api_key': getattr(connection, 'api_key', None),
            'api_base': getattr(connection, 'api_base', None),
            'azure_endpoint': getattr(connection, 'azure_endpoint', None),
            'api_version': getattr(connection, 'api_version', None),
        }

    api_key = connection_dict.get('api_key')
    if not api_key:
        raise ValueError('API key is missing from the connection.')

    # Public OpenAI
    if api_key.startswith('sk-'):
        client_args = {'api_key': api_key, 'base_url': connection_dict.get('api_base')}
        return OpenAI(**{k: v for k, v in client_args.items() if v})

    # Azure OpenAI
    azure_endpoint = connection_dict.get('azure_endpoint') or connection_dict.get('api_base')
    if not azure_endpoint:
        raise ValueError('Azure endpoint is missing in the connection.')

    forced_api_version = '2025-01-01-preview'
    print(f'INFO: Forcing Azure OpenAI API version: {forced_api_version}')
    client_args = {
        'api_key': api_key,
        'azure_endpoint': azure_endpoint,
        'api_version': forced_api_version,
    }
    return AzureOpenAI(**{k: v for k, v in client_args.items() if v})


def get_reasoning_effort_options(**kwargs) -> List[Dict[str, str]]:
    '''Return the dropdown values for reasoning_effort.'''
    return [{'value': x, 'display_value': x} for x in ('low', 'medium', 'high')]


def _parse_roles(rendered_prompt: str) -> Dict[str, str]:
    '''Extract developer/system and user content from the rendered prompt.'''
    dev_pattern = r'#\s*(?:system|developer):\s*(.*?)(?=\s*#\s*user:|$)'
    usr_pattern = r'#\s*user:\s*(.*)'

    dev_match = re.search(dev_pattern, rendered_prompt, re.IGNORECASE | re.DOTALL)
    usr_match = re.search(usr_pattern, rendered_prompt, re.IGNORECASE | re.DOTALL)

    developer_content = dev_match.group(1).strip() if dev_match else ''
    if not usr_match:
        raise ValueError(
            'Required "# user:" marker not found in rendered prompt.\n'
            f'Rendered prompt:\n>>>\n{rendered_prompt}\n<<<'
        )
    user_content = usr_match.group(1).strip()
    return {'developer': developer_content, 'user': user_content}


def _build_user_message(user_text: str, image_url: Optional[str], detail: str) -> Dict:
    '''Return the user message payload, with image block if provided.'''
    if image_url:
        return {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': user_text},
                {'type': 'image_url', 'image_url': {'url': image_url, 'detail': detail}},
            ],
        }
    return {'role': 'user', 'content': user_text}


# --------------------------------------------------------------------------- #
# Main tool                                                                    #
# --------------------------------------------------------------------------- #

@tool
def reasoning_vision_llm(  # Function name used in YAML
    connection: Union[CustomConnection, AzureOpenAIConnection, OpenAIConnection],
    deployment_name: str,
    prompt: PromptTemplate,
    image_url: Optional[str] = None,
    max_completion_tokens: Optional[int] = None,
    reasoning_effort: str = 'low',
    detail: str = 'auto',
    **kwargs,
) -> str:
    '''
    Calls a reasoning-capable, vision-enabled LLM (e.g. GPT-4o-vision).  
    The prompt must contain "# developer:" or "# system:" and "# user:" markers.
    `image_url` may be left blank for text-only operation.
    '''

    client = get_client(connection)

    # Render template
    try:
        rendered_prompt = Template(prompt, trim_blocks=True, keep_trailing_newline=True).render(**kwargs)
        print('--- DEBUG: Rendered Prompt START ---')
        print(rendered_prompt)
        print('--- DEBUG: Rendered Prompt END ---')
    except Exception as e:
        raise ValueError(f'Failed to render prompt template: {e}') from e

    # Parse roles
    try:
        roles = _parse_roles(rendered_prompt)
    except Exception as e:
        raise ValueError(f'Role parsing failed: {e}') from e

    # Build messages
    messages = [
        {'role': 'developer', 'content': roles['developer']},
        _build_user_message(roles['user'], image_url, detail),
    ]
    print(f'--- DEBUG: Messages for API call: {messages}')

    # Chat completion
    api_params = {
        'messages': messages,
        'model': deployment_name,               # AOAI: deployment name; OpenAI: model name
        'reasoning_effort': reasoning_effort,
    }
    if max_completion_tokens is not None:
        api_params['max_completion_tokens'] = max_completion_tokens

    print('API call parameters (sans key):', api_params)
    try:
        response = client.chat.completions.create(**api_params)
        return response.choices[0].message.content
    except Exception as e:
        print('Error calling LLM:', e)
        raise