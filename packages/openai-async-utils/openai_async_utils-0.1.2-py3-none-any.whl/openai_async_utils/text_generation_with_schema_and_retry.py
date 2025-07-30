import os
import json
import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Optional

import openai


# ─── Module-level Logger ────────────────────────────────────────────────────────
LOG = logging.getLogger(__name__)
if not LOG.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    LOG.addHandler(handler)
    LOG.setLevel(logging.INFO)


# ─── Helper: Initialize OpenAI client ────────────────────────────────────────────
def _get_openai_client(api_key: Optional[str] = None) -> openai.AsyncOpenAI:
    """
    Returns an AsyncOpenAI client. If `api_key` is None, it falls back to
    the OPENAI_API_KEY environment variable.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OpenAI API key must be provided or set in OPENAI_API_KEY.")
    return openai.AsyncOpenAI(api_key=key)


# ─── call_openai_api ─────────────────────────────────────────────────────────────
async def call_openai_api(
    system_prompt: str,
    previous_prompts: Optional[List[Dict[str, str]]] = None,
    *,
    api_key: Optional[str] = None,
    validation_schema=None,
    model: str = "gpt-4o-mini",
    max_attempts: int = 3,
) -> tuple[str, Dict[str, int]]:
    """
    Call OpenAI's chat completions endpoint with a retry mechanism and optional JSON validation.

    Args:
        system_prompt: The "system" message content.
        previous_prompts: A list of dicts, e.g. [{"role": "user", "content": "…"}].
        api_key: (optional) pass your OpenAI API key here; otherwise reads OPENAI_API_KEY.
        validation_schema: (optional) a pydantic/BaseModel class to validate response JSON.
        model: which chat model to use (default "gpt-3.5-turbo").
        max_attempts: how many retries before raising.

    Returns:
        Tuple of (response_content: str, usage: {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int}).

    Raises:
        Exception from OpenAI if all retries fail.
    """
    openai_client = _get_openai_client(api_key)
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            LOG.info(f"Calling OpenAI API (Attempt {attempt}/{max_attempts})")
            messages_payload = [{"role": "system", "content": system_prompt}]
            if previous_prompts:
                messages_payload.extend(previous_prompts)

            response = await openai_client.chat.completions.create(
                model=model,
                temperature=0.9,
                messages=messages_payload,
            )

            response_content = response.choices[0].message.content
            LOG.info(f"OpenAI Response: {response_content!r}")

            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            # Optional JSON validation
            if validation_schema:
                try:
                    parsed = json.loads(response_content)
                    validation_schema(**parsed)
                    LOG.info("Response structure validated successfully")
                except json.JSONDecodeError as ex_json:
                    LOG.warning(f"Failed to parse JSON (skipping validation): {ex_json}")
                except Exception as ex_schema:
                    LOG.warning(f"Schema validation failed: {ex_schema}")

            return response_content, usage

        except Exception as err:
            LOG.error(f"API call attempt {attempt} failed: {err}")
            if attempt < max_attempts:
                LOG.info(f"Retrying after 1s… (Attempt {attempt + 1}/{max_attempts})")
                await asyncio.sleep(1)
            else:
                LOG.error(f"All {max_attempts} attempts exhausted.")
                raise


# ─── stream_openai_api ──────────────────────────────────────────────────────────
async def stream_openai_api(
    system_prompt: str,
    previous_prompts: Optional[List[Dict[str, str]]] = None,
    *,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    max_attempts: int = 3,
) -> AsyncGenerator[str, None]:
    """
    Stream chat completions from OpenAI with a retry loop.
    Yields chunks of content as they arrive.

    Args:
        system_prompt: The "system" message content.
        previous_prompts: A list of dicts, e.g. [{"role": "user", "content": "…"}].
        api_key: (optional) pass your OpenAI API key here; otherwise reads OPENAI_API_KEY.
        model: which chat model to use (default "gpt-3.5-turbo").
        max_attempts: how many retries before raising.

    Yields:
        Each time a new piece of text arrives, that text is yielded.
    """
    openai_client = _get_openai_client(api_key)
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            LOG.info(f"Calling OpenAI streaming API (Attempt {attempt}/{max_attempts})")
            messages_payload = [{"role": "system", "content": system_prompt}]
            if previous_prompts:
                messages_payload.extend(previous_prompts)

            stream = await openai_client.chat.completions.create(
                model=model,
                temperature=0.9,
                messages=messages_payload,
                stream=True,
            )

            full_content = ""
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_content += delta
                    yield delta

            LOG.info(f"Finished streaming; total length: {len(full_content)}")
            return

        except Exception as err:
            LOG.error(f"Streaming attempt {attempt} failed: {err}")
            if attempt < max_attempts:
                LOG.info(f"Retrying stream after 1s… (Attempt {attempt + 1}/{max_attempts})")
                await asyncio.sleep(1)
            else:
                LOG.error(f"All {max_attempts} streaming attempts exhausted.")
                raise
