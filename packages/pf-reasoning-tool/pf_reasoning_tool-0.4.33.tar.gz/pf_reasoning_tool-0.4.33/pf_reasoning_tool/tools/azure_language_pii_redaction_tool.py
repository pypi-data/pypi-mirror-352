# -*- coding: utf-8 -*-
"""
Azure AI Language Service PII Detection and Redaction Tool
=========================================================
Takes a string input and returns a string with PII redacted,
using the Azure AI Language Service.
"""

from __future__ import annotations

import logging
import os
import requests # Required for REST API calls
from typing import List, Dict, Any, Optional, Tuple

# Core PromptFlow imports
from promptflow.core import tool
from promptflow.connections import CustomConnection

# Setup logger for the tool
logger = logging.getLogger(__name__)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))

# API Version for Language Service
# Refer to: https://learn.microsoft.com/en-us/azure/ai-services/language-service/concepts/model-lifecycle
# Using a GA version is generally recommended. The quickstart uses 2023-04-01.
LANGUAGE_API_VERSION = "2023-04-01"

# ------------------------------------------------------------------ #
# 1.  Credential Extraction Helper                                   #
# ------------------------------------------------------------------ #
def _extract_language_service_credentials(conn: CustomConnection) -> Tuple[str, str]:
    """
    Extracts endpoint and API key for Azure AI Language Service from a CustomConnection.
    Assumes endpoint might be in 'endpoint', 'api_base', 'key1', or 'value1'.
    Assumes API key might be in 'api_key', 'key', 'key2', or 'value2'.
    """
    if not isinstance(conn, CustomConnection):
        raise TypeError(f"Expected CustomConnection, got {type(conn).__name__}")

    c = dict(conn)
    endpoint = (
        c.get("endpoint")
        or c.get("api_base") # Common for Azure services
        or c.get("key1")     # User specified structure
        or c.get("value1")
    )
    api_key_from_conn = (
        c.get("api_key")
        or c.get("key")      # Common for API keys
        or c.get("key2")     # User specified structure
        or c.get("value2")
    )

    if not endpoint:
        raise ValueError(
            "CustomConnection for Language Service must include the endpoint "
            "(e.g., 'endpoint', 'api_base', 'key1', 'value1')."
        )
    if not api_key_from_conn:
        raise ValueError(
            "CustomConnection for Language Service must include the API key "
            "(e.g., 'api_key', 'key', 'key2', 'value2')."
        )

    # Resolve "***" placeholder for API key using environment variable
    resolved_api_key = api_key_from_conn
    if api_key_from_conn == "***":
        logger.info("Language Service API key is '***', resolving from AZURE_LANGUAGE_KEY environment variable.")
        resolved_api_key = os.getenv("AZURE_LANGUAGE_KEY") # Use a distinct env var name
        if not resolved_api_key:
            raise ValueError(
                "Language Service API key is '***' in connection, but the "
                "'AZURE_LANGUAGE_KEY' environment variable is not set or is empty."
            )
    
    if not resolved_api_key:
        raise ValueError("Failed to determine a valid Language Service API key.")

    # Ensure endpoint is a base URL (e.g., https://<your-resource>.cognitiveservices.azure.com)
    if "/language/:analyze-text" in endpoint:
        # Strip the specific path if user included it
        endpoint = endpoint.split("/language/:analyze-text")[0]
    
    logger.debug(f"Using Language Service Endpoint: {endpoint}")
    return endpoint, resolved_api_key


# ------------------------------------------------------------------ #
# 2.  Main PromptFlow Tool Function                                  #
# ------------------------------------------------------------------ #
@tool
def redact_pii_text(
    connection: CustomConnection,
    text_input: str,
    language: str = "en",
    pii_categories: Optional[List[str]] = None,
    # redact_character: str = "*" # The API controls this, so this param isn't directly useful
                                  # unless we manually redact based on offsets.
                                  # For now, relying on service's 'redactedText'.
) -> str:
    """
    Detects and redacts Personally Identifiable Information (PII) from input text
    using the Azure AI Language Service.
    """
    if not text_input or not text_input.strip():
        logger.warning("Input text is empty or whitespace only. Returning as is.")
        return text_input

    try:
        endpoint, api_key = _extract_language_service_credentials(connection)
    except Exception as e:
        logger.error(f"Failed to extract Language Service credentials: {e}")
        raise ValueError(f"Invalid Language Service connection: {e}") from e

    # Construct the API endpoint for PII detection
    # URL: https://<your-resource-name>.cognitiveservices.azure.com/language/:analyze-text?api-version=<API-VERSION>
    api_url = f"{endpoint.rstrip('/')}/language/:analyze-text?api-version={LANGUAGE_API_VERSION}"

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/json",
    }

    # Build the payload
    payload_parameters = {
        "modelVersion": "latest", # Use the latest available model
        # "loggingOptOut": False, # Default is False
    }
    if pii_categories and isinstance(pii_categories, list) and len(pii_categories) > 0:
        payload_parameters["piiCategories"] = pii_categories
        logger.info(f"Using custom PII categories for redaction: {pii_categories}")
    # For general PII, do not specify domain="phi".
    # If you wanted to target only phi, you would add: "domain": "phi"
    # payload_parameters["domain"] = "phi" # Uncomment and adjust if specific domain is needed

    payload = {
        "kind": "PiiEntityRecognition",
        "parameters": payload_parameters,
        "analysisInput": {
            "documents": [
                {
                    "id": "1", # Document ID can be arbitrary for a single document
                    "language": language,
                    "text": text_input,
                }
            ]
        },
    }

    logger.debug(f"Sending PII redaction request to: {api_url}")
    # logger.debug(f"Payload (text omitted for brevity): { {k:v for k,v in payload.items() if k != 'analysisInput'} }")


    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        
        response_json = response.json()
        logger.debug(f"Received API response: {response_json}")

        # Process the response
        # Example response structure:
        # {
        #     "kind": "PiiEntityRecognitionResults",
        #     "results": {
        #         "documents": [
        #             {
        #                 "id": "1",
        #                 "redactedText": "My name is **** and I live in *****.",
        #                 "entities": [ ... ],
        #                 "warnings": []
        #             }
        #         ],
        #         "errors": [],
        #         "modelVersion": "2023-04-01"
        #     }
        # }

        if response_json.get("results") and response_json["results"].get("documents"):
            doc_result = response_json["results"]["documents"][0] # Assuming one document was sent
            if "redactedText" in doc_result:
                logger.info("PII redaction successful.")
                return doc_result["redactedText"]
            else:
                # This case should ideally not happen if the API call is successful.
                # If no PII is found, redactedText should be the original text.
                logger.warning("API response did not contain 'redactedText'. Returning original text.")
                return text_input
        elif response_json.get("results") and response_json["results"].get("errors"):
            errors = response_json["results"]["errors"]
            logger.error(f"API returned errors: {errors}")
            # Concatenate error messages if multiple, or just take the first
            error_message = "; ".join([e.get("error", {}).get("message", "Unknown error") for e in errors])
            raise RuntimeError(f"Language Service API returned errors: {error_message}")
        else:
            logger.error(f"Unexpected API response format: {response_json}")
            raise RuntimeError("Unexpected response format from Language Service API.")

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - Response: {http_err.response.text}", exc_info=True)
        raise RuntimeError(f"Language Service API request failed with HTTP error: {http_err}") from http_err
    except Exception as e:
        logger.error(f"An unexpected error occurred during PII redaction: {e}", exc_info=True)
        raise RuntimeError(f"An unexpected error occurred: {e}") from e