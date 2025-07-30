import abc
import base64
import io
import mimetypes
import os

# from tokencost import calculate_prompt_cost, calculate_completion_cost
from pathlib import Path
from typing import List

import anthropic
import requests
from dotenv import load_dotenv

# import google.generativeai as genai
from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai import types
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    OpenAI,
    RateLimitError,
)
from PIL import Image
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .messages import Message

load_dotenv(override=True)


class AIProvider(abc.ABC):
    @abc.abstractmethod
    def call_ai(self, messages, temperature, max_tokens, model, **kwargs):
        pass

    @abc.abstractmethod
    async def call_ai_async(self, messages, temperature, max_tokens, model, **kwargs):
        pass

    @abc.abstractmethod
    def generate(self, messages, temperature, max_tokens, model, **kwargs):
        pass

    @abc.abstractmethod
    async def generate_async(self, messages, temperature, max_tokens, model, **kwargs):
        pass


class LMStudioProvider(AIProvider):
    supported_models = ["lmstudio"]

    def __init__(self, ip_address="localhost", port=1234):
        self.base_url = f"http://{ip_address}:{port}/v1"

    def call_ai(self, messages, temperature, max_tokens, model=None, **kwargs):
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs,
            }
            if model:
                data["model"] = model

            response = requests.post(
                f"{self.base_url}/chat/completions", headers=headers, json=data
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise e

    async def call_ai_async(
        self, messages, temperature, max_tokens, model=None, **kwargs
    ):
        # For simplicity, we'll use the synchronous version in an async context
        # In a real-world scenario, you might want to use an async HTTP client
        return self.call_ai(messages, temperature, max_tokens, model, **kwargs)

    def generate(self, messages, temperature, max_tokens, model=None, **kwargs):
        raise NotImplementedError("This provider does not support image generation")

    async def generate_async(
        self, messages, temperature, max_tokens, model=None, **kwargs
    ):
        raise NotImplementedError("This provider does not support image generation")


class OpenAIProvider(AIProvider):
    supported_models = [
        "openai/o1-mini-2024-09-12",
        "openai/o1-mini",
        "openai/gpt-4",
        "openai/gpt-4o-mini-2024-07-18",
        "openai/gpt-4o-2024-11-20",
        "openai/gpt-4o-2024-05-13",
        "openai/o1-preview",
        "openai/o1-preview-2024-09-12",
        "openai/o3-mini",
        "openai/o3-mini-2025-01-31",
        "openai/gpt-4o-mini",
        "openai/gpt-3.5-turbo-instruct-0914",
        "openai/gpt-4o-mini-search-preview",
        "openai/gpt-3.5-turbo-1106",
        "openai/gpt-4o-search-preview",
        "openai/gpt-4-turbo",
        "openai/gpt-3.5-turbo-instruct",
        "openai/o1-2024-12-17",
        "openai/o1",
        "openai/gpt-3.5-turbo-0125",
        "openai/gpt-4o-2024-08-06",
        "openai/gpt-3.5-turbo",
        "openai/gpt-4-turbo-2024-04-09",
        "openai/gpt-4o-realtime-preview",
        "openai/gpt-3.5-turbo-16k",
        "openai/gpt-4o",
        "openai/text-embedding-3-small",
        "openai/chatgpt-4o-latest",
        "openai/gpt-4-1106-preview",
        "openai/text-embedding-ada-002",
        "openai/gpt-4-0613",
        "openai/gpt-4.5-preview",
        "openai/gpt-4.5-preview-2025-02-27",
        "openai/gpt-4o-search-preview-2025-03-11",
        "openai/gpt-4-0125-preview",
        "openai/gpt-4-turbo-preview",
        "openai/gpt-4.1-mini-2025-04-14",
        "openai/gpt-4.1",
        "openai/gpt-4.1-2025-04-14",
        "openai/o4-mini-2025-04-16",
    ]

    def __init__(self, api_key=None):
        self.sync_client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.async_client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def call_ai(
        self, messages, temperature, max_tokens, model="openai/gpt-4o", **kwargs
    ):
        try:
            prepared_messages = self._prepare_messages(messages)  # Add this line
            response = self.sync_client.chat.completions.create(
                model=model.split("/")[-1],
                messages=prepared_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e

    async def call_ai_async(
        self, messages, temperature, max_tokens, model="openai/gpt-4o", **kwargs
    ):
        try:
            prepared_messages = self._prepare_messages(messages)
            response = await self.async_client.chat.completions.create(
                model=model.split("/")[-1],
                messages=prepared_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e

    def generate(self, messages, temperature, max_tokens, model=None, **kwargs):
        raise NotImplementedError("This provider does not support image generation")

    async def generate_async(
        self, messages, temperature, max_tokens, model=None, **kwargs
    ):
        raise NotImplementedError("This provider does not support image generation")

    def _process_media(self, media_path):
        if isinstance(media_path, (str, Path)):
            path = Path(media_path)
            if path.is_file():
                with open(path, "rb") as media_file:
                    return base64.b64encode(media_file.read()).decode("utf-8")
            else:
                raise ValueError(f"File not found: {media_path}")
        elif isinstance(media_path, bytes):
            return base64.b64encode(media_path).decode("utf-8")
        else:
            raise ValueError(f"Unsupported media format: {type(media_path)}")

    def _process_image(self, image_path):
        if isinstance(image_path, (str, Path)):
            # Handle both string paths and Path objects
            path = Path(image_path)
            if path.is_file():
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            else:
                raise ValueError(f"File not found: {image_path}")
        elif isinstance(image_path, bytes):
            # Assume it's image data
            return base64.b64encode(image_path).decode("utf-8")
        elif isinstance(image_path, Image.Image):
            # It's a PIL Image
            buffered = io.BytesIO()
            image_path.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        else:
            raise ValueError(f"Unsupported image format: {type(image_path)}")

    def _prepare_messages(self, messages):
        prepared_messages = []
        for message in messages:
            content = message["content"]
            if isinstance(content, str):
                prepared_messages.append({"role": message["role"], "content": content})
            elif isinstance(content, list):
                prepared_content = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "image_url":
                        image_data = self._process_media(item["image_url"]["url"])
                        mime_type, _ = mimetypes.guess_type(item["image_url"]["url"])
                        # Default to jpeg if we can't determine the type
                        mime_type = mime_type or "image/jpeg"
                        prepared_content.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                },
                            }
                        )
                    elif isinstance(item, dict) and item.get("type") in [
                        "video_url",
                        "audio_url",
                    ]:
                        # Handle other media types if needed, not supported yet
                        # prepared_content.append(item)
                        pass
                    else:
                        prepared_content.append(item)
                prepared_messages.append(
                    {"role": message["role"], "content": prepared_content}
                )
        return prepared_messages


class AnthropicProvider(AIProvider):
    supported_models = [
        "anthropic/claude-3-7-sonnet-20250219",
        "anthropic/claude-3-5-sonnet-20241022",
        "anthropic/claude-3-5-haiku-20241022",
        "anthropic/claude-3-5-sonnet-20240620",
        "anthropic/claude-3-haiku-20240307",
        "anthropic/claude-3-opus-20240229",
        "anthropic/claude-3-sonnet-20240229",
        "anthropic/claude-2.1",
        "anthropic/claude-2.0",
        "anthropic/claude-opus-4-20250514",
        "anthropic/claude-sonnet-4-20250514",
    ]

    def __init__(self, api_key=None):
        self.sync_client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.async_client = anthropic.AsyncAnthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )

        self.supported_models = [
            f"anthropic/{model.id}" for model in self.sync_client.models.list(limit=30)
        ]

    def _prepare_messages(self, messages):
        """Prepare messages for Claude API, handling both text, images, and caching."""
        system_content = []
        user_messages = []

        for message in messages:
            if message["role"] == "system":
                system_msg = {"type": "text", "text": message["content"]}
                # Add cache_control if present
                if "cache_control" in message:
                    system_msg["cache_control"] = message["cache_control"]
                system_content.append(system_msg)
            else:
                if isinstance(message["content"], str):
                    user_messages.append(
                        {"role": message["role"], "content": message["content"]}
                    )
                elif isinstance(message["content"], list):
                    prepared_content = []
                    for item in message["content"]:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                prepared_content.append(
                                    {"type": "text", "text": item["text"]}
                                )
                            elif item.get("type") == "image_url":
                                # Handle both local files and URLs
                                image_url = item["image_url"]["url"]
                                if image_url.startswith(("http://", "https://")):
                                    prepared_content.append(
                                        {
                                            "type": "image",
                                            "source": {"type": "url", "url": image_url},
                                        }
                                    )
                                else:
                                    # For local files, use base64
                                    image_data = self._process_image(image_url)
                                    prepared_content.append(
                                        {
                                            "type": "image",
                                            "source": {
                                                "type": "base64",
                                                "media_type": self._get_media_type(
                                                    image_url
                                                ),
                                                "data": image_data,
                                            },
                                        }
                                    )
                    user_messages.append(
                        {"role": message["role"], "content": prepared_content}
                    )

        return system_content, user_messages

    def _process_image(self, image_path):
        MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

        if isinstance(image_path, (str, Path)):
            path = Path(image_path)
            if path.is_file():
                # Read the image file
                with open(path, "rb") as image_file:
                    image_data = image_file.read()

                # Check if image needs resizing
                if len(image_data) > MAX_IMAGE_SIZE:
                    # Open with PIL and resize
                    img = Image.open(io.BytesIO(image_data))

                    # Calculate scaling factor to get under the limit
                    # Start with 0.5 scaling as suggested
                    scale = 0.5
                    img_resized = img.resize(
                        (int(img.width * scale), int(img.height * scale))
                    )

                    # Keep resizing if still too large
                    buffer = io.BytesIO()
                    img_format = img.format or "JPEG"
                    img_resized.save(buffer, format=img_format)
                    resized_data = buffer.getvalue()

                    while len(resized_data) > MAX_IMAGE_SIZE and scale > 0.1:
                        # Reduce scale further if still too large
                        scale *= 0.8
                        img_resized = img.resize(
                            (int(img.width * scale), int(img.height * scale))
                        )
                        buffer = io.BytesIO()
                        img_resized.save(buffer, format=img_format)
                        resized_data = buffer.getvalue()

                    return base64.b64encode(resized_data).decode("utf-8")

                # If image is already small enough, just return the encoded data
                return base64.b64encode(image_data).decode("utf-8")
            # Add URL handling
            elif str(image_path).startswith(("http://", "https://")):
                response = requests.get(str(image_path))
                response.raise_for_status()
                image_data = response.content

                # Check if image needs resizing
                if len(image_data) > MAX_IMAGE_SIZE:
                    # Open with PIL and resize
                    img = Image.open(io.BytesIO(image_data))

                    # Start with 0.5 scaling
                    scale = 0.5
                    img_resized = img.resize(
                        (int(img.width * scale), int(img.height * scale))
                    )

                    # Keep resizing if still too large
                    buffer = io.BytesIO()
                    img_format = img.format or "JPEG"
                    img_resized.save(buffer, format=img_format)
                    resized_data = buffer.getvalue()

                    while len(resized_data) > MAX_IMAGE_SIZE and scale > 0.1:
                        # Reduce scale further if still too large
                        scale *= 0.8
                        img_resized = img.resize(
                            (int(img.width * scale), int(img.height * scale))
                        )
                        buffer = io.BytesIO()
                        img_resized.save(buffer, format=img_format)
                        resized_data = buffer.getvalue()

                    return base64.b64encode(resized_data).decode("utf-8")

                return base64.b64encode(image_data).decode("utf-8")
            else:
                raise ValueError(f"File not found: {image_path}")
        elif isinstance(image_path, bytes):
            image_data = image_path

            # Check if image needs resizing
            if len(image_data) > MAX_IMAGE_SIZE:
                # Open with PIL and resize
                img = Image.open(io.BytesIO(image_data))

                # Start with 0.5 scaling
                scale = 0.5
                img_resized = img.resize(
                    (int(img.width * scale), int(img.height * scale))
                )

                # Keep resizing if still too large
                buffer = io.BytesIO()
                img_format = img.format or "JPEG"
                img_resized.save(buffer, format=img_format)
                resized_data = buffer.getvalue()

                while len(resized_data) > MAX_IMAGE_SIZE and scale > 0.1:
                    # Reduce scale further if still too large
                    scale *= 0.8
                    img_resized = img.resize(
                        (int(img.width * scale), int(img.height * scale))
                    )
                    buffer = io.BytesIO()
                    img_resized.save(buffer, format=img_format)
                    resized_data = buffer.getvalue()

                return base64.b64encode(resized_data).decode("utf-8")

            return base64.b64encode(image_data).decode("utf-8")
        elif isinstance(image_path, Image.Image):
            img = image_path
            # Preserve original format if possible, fallback to PNG
            img_format = getattr(img, "format", "PNG") or "PNG"

            # First try with original size
            buffer = io.BytesIO()
            img.save(buffer, format=img_format)
            image_data = buffer.getvalue()

            # Check if image needs resizing
            if len(image_data) > MAX_IMAGE_SIZE:
                # Start with 0.5 scaling
                scale = 0.5
                img_resized = img.resize(
                    (int(img.width * scale), int(img.height * scale))
                )

                # Keep resizing if still too large
                buffer = io.BytesIO()
                img_resized.save(buffer, format=img_format)
                resized_data = buffer.getvalue()

                while len(resized_data) > MAX_IMAGE_SIZE and scale > 0.1:
                    # Reduce scale further if still too large
                    scale *= 0.8
                    img_resized = img.resize(
                        (int(img.width * scale), int(img.height * scale))
                    )
                    buffer = io.BytesIO()
                    img_resized.save(buffer, format=img_format)
                    resized_data = buffer.getvalue()

                return base64.b64encode(resized_data).decode("utf-8")

            return base64.b64encode(image_data).decode("utf-8")
        else:
            raise ValueError(f"Unsupported image format: {type(image_path)}")

    def _get_media_type(self, file_path):
        if isinstance(file_path, str) and file_path.startswith(("http://", "https://")):
            response = requests.head(file_path)
            return response.headers.get("content-type", "image/jpeg")
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "image/jpeg"

    def generate(self, messages, temperature, max_tokens, model=None, **kwargs):
        raise NotImplementedError("This provider does not support image generation")

    async def generate_async(
        self, messages, temperature, max_tokens, model=None, **kwargs
    ):
        raise NotImplementedError("This provider does not support image generation")

    def call_ai(
        self,
        messages,
        temperature,
        max_tokens,
        model="anthropic/claude-3-5-sonnet-20240620",
        **kwargs,
    ):
        try:
            system_content, user_messages = self._prepare_messages(messages)

            # Extract thinking parameter if provided in kwargs
            thinking = kwargs.pop("thinking", None)

            # If thinking is True (boolean), convert to proper format
            if thinking is True:
                thinking = {
                    "type": "enabled",
                    "budget_tokens": min(
                        max_tokens // 2, 1024
                    ),  # Use half of max_tokens or 1024, whichever is smaller
                }

            # Create API call parameters
            api_params = {
                "model": model.split("/")[-1],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_content,
                "messages": user_messages
                if user_messages
                else [{"role": "user", "content": "Follow the system prompt."}],
                **kwargs,
            }

            # Add thinking parameter only if it's provided
            if thinking:
                api_params["thinking"] = thinking

            response = self.sync_client.messages.create(**api_params)

            # Handle thinking content if present
            if hasattr(response, "content") and len(response.content) > 1:
                # Check if any content block is of type "thinking"
                thinking_blocks = [
                    block
                    for block in response.content
                    if getattr(block, "type", None) == "thinking"
                ]
                if thinking_blocks:
                    # You can log or process thinking blocks separately if needed
                    # For now, we'll just return the final text response
                    text_blocks = [
                        block
                        for block in response.content
                        if getattr(block, "type", None) == "text"
                    ]
                    if text_blocks:
                        return text_blocks[0].text

            # Default return for normal responses
            return response.content[0].text
        except Exception as e:
            raise e

    async def call_ai_async(
        self,
        messages,
        temperature,
        max_tokens,
        model="anthropic/claude-3-5-sonnet-20240620",
        **kwargs,
    ):
        try:
            system_content, user_messages = self._prepare_messages(messages)

            # Extract thinking parameter if provided in kwargs
            thinking = kwargs.pop("thinking", None)

            # If thinking is True (boolean), convert to proper format
            if thinking is True:
                thinking = {
                    "type": "enabled",
                    "budget_tokens": min(
                        max_tokens // 2, 1024
                    ),  # Use half of max_tokens or 1024, whichever is smaller
                }

            # Create API call parameters
            api_params = {
                "model": model.split("/")[-1],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_content,
                "messages": user_messages
                if user_messages
                else [{"role": "user", "content": "Follow the system prompt."}],
                **kwargs,
            }

            # Add thinking parameter only if it's provided
            if thinking:
                api_params["thinking"] = thinking

            response = await self.async_client.messages.create(**api_params)

            # Handle thinking content if present
            if hasattr(response, "content") and len(response.content) > 1:
                # Check if any content block is of type "thinking"
                thinking_blocks = [
                    block
                    for block in response.content
                    if getattr(block, "type", None) == "thinking"
                ]
                if thinking_blocks:
                    # You can log or process thinking blocks separately if needed
                    # For now, we'll just return the final text response
                    text_blocks = [
                        block
                        for block in response.content
                        if getattr(block, "type", None) == "text"
                    ]
                    if text_blocks:
                        return text_blocks[0].text

            # Default return for normal responses
            return response.content[0].text
        except Exception as e:
            raise e


class GeminiProvider(AIProvider):
    supported_models = [
        "gemini/gemini-1.0-pro-vision-latest",
        "gemini/gemini-1.5-flash",
        "gemini/gemini-1.5-flash-001",
        "gemini/gemini-1.5-flash-001-tuning",
        "gemini/gemini-1.5-flash-002",
        "gemini/gemini-1.5-flash-8b",
        "gemini/gemini-1.5-flash-8b-001",
        "gemini/gemini-1.5-flash-8b-exp-0827",
        "gemini/gemini-1.5-flash-8b-exp-0924",
        "gemini/gemini-1.5-flash-8b-latest",
        "gemini/gemini-1.5-flash-latest",
        "gemini/gemini-1.5-pro",
        "gemini/gemini-1.5-pro-001",
        "gemini/gemini-1.5-pro-002",
        "gemini/gemini-1.5-pro-latest",
        "gemini/gemini-2.0-flash",
        "gemini/gemini-2.0-flash-001",
        "gemini/gemini-2.0-flash-exp",
        "gemini/gemini-2.0-flash-exp-image-generation",
        "gemini/gemini-2.0-flash-lite",
        "gemini/gemini-2.0-flash-lite-001",
        "gemini/gemini-2.0-flash-lite-preview",
        "gemini/gemini-2.0-flash-lite-preview-02-05",
        "gemini/gemini-2.0-flash-thinking-exp",
        "gemini/gemini-2.0-flash-thinking-exp-01-21",
        "gemini/gemini-2.0-flash-thinking-exp-1219",
        "gemini/gemini-2.0-pro-exp",
        "gemini/gemini-2.0-pro-exp-02-05",
        "gemini/gemini-exp-1206",
        "gemini/gemini-pro-vision",
        "gemini/gemma-3-27b-it",
        "gemini/learnlm-1.5-pro-experimental",
        "gemini/models/gemini-1.0-pro-vision-latest",
        "gemini/models/gemini-1.5-flash",
        "gemini/models/gemini-1.5-flash-001",
        "gemini/models/gemini-1.5-flash-001-tuning",
        "gemini/models/gemini-1.5-flash-002",
        "gemini/models/gemini-1.5-flash-8b",
        "gemini/models/gemini-1.5-flash-8b-001",
        "gemini/models/gemini-1.5-flash-8b-exp-0827",
        "gemini/models/gemini-1.5-flash-8b-exp-0924",
        "gemini/models/gemini-1.5-flash-8b-latest",
        "gemini/models/gemini-1.5-flash-latest",
        "gemini/models/gemini-1.5-pro",
        "gemini/models/gemini-1.5-pro-001",
        "gemini/models/gemini-1.5-pro-002",
        "gemini/models/gemini-1.5-pro-latest",
        "gemini/models/gemini-2.0-flash",
        "gemini/models/gemini-2.0-flash-001",
        "gemini/models/gemini-2.0-flash-exp",
        "gemini/models/gemini-2.0-flash-exp-image-generation",
        "gemini/models/gemini-2.0-flash-lite",
        "gemini/models/gemini-2.0-flash-lite-001",
        "gemini/models/gemini-2.0-flash-lite-preview",
        "gemini/models/gemini-2.0-flash-lite-preview-02-05",
        "gemini/models/gemini-2.0-flash-preview-image-generation",
        "gemini/models/gemini-2.0-flash-thinking-exp",
        "gemini/models/gemini-2.0-flash-thinking-exp-01-21",
        "gemini/models/gemini-2.0-flash-thinking-exp-1219",
        "gemini/models/gemini-2.0-pro-exp",
        "gemini/models/gemini-2.0-pro-exp-02-05",
        "gemini/models/gemini-2.5-flash-preview-04-17",
        "gemini/models/gemini-2.5-flash-preview-04-17-thinking",
        "gemini/models/gemini-2.5-flash-preview-05-20",
        "gemini/models/gemini-2.5-flash-preview-tts",
        "gemini/models/gemini-2.5-pro-exp-03-25",
        "gemini/models/gemini-2.5-pro-preview-03-25",
        "gemini/models/gemini-2.5-pro-preview-05-06",
        "gemini/models/gemini-2.5-pro-preview-tts",
        "gemini/models/gemini-exp-1206",
        "gemini/models/gemini-pro-vision",
        "gemini/models/gemma-3-12b-it",
        "gemini/models/gemma-3-1b-it",
        "gemini/models/gemma-3-27b-it",
        "gemini/models/gemma-3-4b-it",
        "gemini/models/gemma-3n-e4b-it",
        "gemini/models/learnlm-2.0-flash-experimental",
        "genai/models/gemini-1.0-pro-vision-latest",
        "genai/models/gemini-1.5-flash",
        "genai/models/gemini-1.5-flash-001",
        "genai/models/gemini-1.5-flash-001-tuning",
        "genai/models/gemini-1.5-flash-002",
        "genai/models/gemini-1.5-flash-8b",
        "genai/models/gemini-1.5-flash-8b-001",
        "genai/models/gemini-1.5-flash-8b-exp-0827",
        "genai/models/gemini-1.5-flash-8b-exp-0924",
        "genai/models/gemini-1.5-flash-8b-latest",
        "genai/models/gemini-1.5-flash-latest",
        "genai/models/gemini-1.5-pro",
        "genai/models/gemini-1.5-pro-001",
        "genai/models/gemini-1.5-pro-002",
        "genai/models/gemini-1.5-pro-latest",
        "genai/models/gemini-2.0-flash",
        "genai/models/gemini-2.0-flash-001",
        "genai/models/gemini-2.0-flash-exp",
        "genai/models/gemini-2.0-flash-exp-image-generation",
        "genai/models/gemini-2.0-flash-lite",
        "genai/models/gemini-2.0-flash-lite-001",
        "genai/models/gemini-2.0-flash-lite-preview",
        "genai/models/gemini-2.0-flash-lite-preview-02-05",
        "genai/models/gemini-2.0-flash-preview-image-generation",
        "genai/models/gemini-2.0-flash-thinking-exp",
        "genai/models/gemini-2.0-flash-thinking-exp-01-21",
        "genai/models/gemini-2.0-flash-thinking-exp-1219",
        "genai/models/gemini-2.0-pro-exp",
        "genai/models/gemini-2.0-pro-exp-02-05",
        "genai/models/gemini-2.5-flash-preview-04-17",
        "genai/models/gemini-2.5-flash-preview-04-17-thinking",
        "genai/models/gemini-2.5-flash-preview-05-20",
        "genai/models/gemini-2.5-flash-preview-tts",
        "genai/models/gemini-2.5-pro-exp-03-25",
        "genai/models/gemini-2.5-pro-preview-03-25",
        "genai/models/gemini-2.5-pro-preview-05-06",
        "genai/models/gemini-2.5-pro-preview-tts",
        "genai/models/gemini-exp-1206",
        "genai/models/gemini-pro-vision",
        "genai/models/gemma-3-12b-it",
        "genai/models/gemma-3-1b-it",
        "genai/models/gemma-3-27b-it",
        "genai/models/gemma-3-4b-it",
        "genai/models/gemma-3n-e4b-it",
        "genai/models/learnlm-2.0-flash-experimental",
    ]

    def __init__(self, api_key=None):
        # genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.client = genai.Client(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        try:
            # Get models from API
            api_models = []
            for m in self.client.models.list():
                if (
                    hasattr(m, "supported_actions")
                    and "generateContent" in m.supported_actions
                ):
                    # Create both gemini/ and genai/ prefixed versions
                    genai_name = f"genai/{m.name}"
                    gemini_name = f"gemini/{m.name}"
                    api_models.append(genai_name)
                    api_models.append(gemini_name)

            # Add the API models to our supported models
            if api_models:
                self.supported_models.extend(api_models)
        except Exception as e:
            print(e, f"Error initializing GeminiProvider: {e}")

    def call_ai(
        self,
        messages,
        temperature,
        max_tokens,
        model="gemini/gemini-2.0-flash-exp",
        **kwargs,
    ):
        try:
            # Extract system message if present
            system_instruction = next(
                (msg["content"] for msg in messages if msg["role"] == "system"), None
            )

            # Get the user messages
            user_messages = [msg for msg in messages if msg["role"] != "system"]

            # Convert messages to content
            if not user_messages:
                contents = "Follow the system instructions."
            elif len(user_messages) == 1 and isinstance(
                user_messages[0]["content"], str
            ):
                contents = user_messages[0]["content"]
            else:
                # Handle multiple messages or messages with images
                contents = []
                for message in user_messages:
                    if isinstance(message["content"], str):
                        contents.append(message["content"])
                    elif isinstance(message["content"], list):
                        text_parts = []
                        image_parts = []
                        for item in message["content"]:
                            if item.get("type") == "text":
                                text_parts.append(item["text"])
                            elif item.get("type") == "image_url":
                                image_path = item["image_url"]["url"]
                                with open(image_path, "rb") as f:
                                    image_data = f.read()
                                image_parts.append(
                                    types.Part.from_bytes(
                                        data=image_data, mime_type="image/jpeg"
                                    )
                                )

                        # Always ensure there's text content
                        if not text_parts:
                            text_parts.append("Consider this image in your response.")

                        # Combine text parts into a single string
                        contents.append(" ".join(text_parts))
                        # Add image parts after text
                        contents.extend(image_parts)

            response = self.client.models.generate_content(
                model=model.split("/")[-1],
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    system_instruction=system_instruction,  # Pass system instruction directly in config
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_NONE",
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_NONE",
                        ),
                    ],
                ),
            )
            return response.text
        except Exception as e:
            raise e

    async def call_ai_async(
        self,
        messages,
        temperature,
        max_tokens,
        model="gemini/gemini-2.0-flash-exp",
        **kwargs,
    ):
        try:
            # Extract system message if present
            system_instruction = next(
                (msg["content"] for msg in messages if msg["role"] == "system"), None
            )

            # Get the user messages
            user_messages = [msg for msg in messages if msg["role"] != "system"]

            if not user_messages:
                contents = "Follow the system instructions."
            elif len(user_messages) == 1 and isinstance(
                user_messages[0]["content"], str
            ):
                contents = user_messages[0]["content"]
            else:
                # Handle multiple messages or messages with images
                contents = []
                for message in user_messages:
                    if isinstance(message["content"], str):
                        contents.append(message["content"])
                    elif isinstance(message["content"], list):
                        text_parts = []
                        image_parts = []
                        for item in message["content"]:
                            if item.get("type") == "text":
                                text_parts.append(item["text"])
                            elif item.get("type") == "image_url":
                                image_path = item["image_url"]["url"]
                                with open(image_path, "rb") as f:
                                    image_data = f.read()
                                image_parts.append(
                                    types.Part.from_bytes(
                                        data=image_data, mime_type="image/jpeg"
                                    )
                                )

                        # Always ensure there's text content
                        if not text_parts:
                            text_parts.append("Consider this image in your response.")

                        # Combine text parts into a single string
                        contents.append(" ".join(text_parts))
                        # Add image parts after text
                        contents.extend(image_parts)

            response = self.client.models.generate_content(
                model=model.split("/")[-1],
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    system_instruction=system_instruction,  # Pass system instruction directly in config
                    safety_settings=[
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_NONE",
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold="BLOCK_NONE",
                        ),
                    ],
                ),
            )
            return response.text
        except Exception as e:
            raise e

    def _process_video(self, video_path):
        video_file = genai.upload_file(path=video_path)

        # Wait until the uploaded video is available
        while video_file.state.name == "PROCESSING":
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(video_file.state.name)

        return video_file

    def generate(
        self,
        messages,
        temperature,
        max_tokens,
        model="gemini/gemini-2.0-flash-exp-image-generation",
        **kwargs,
    ):
        try:
            # Extract system message if present
            system_instruction = next(
                (msg["content"] for msg in messages if msg["role"] == "system"), None
            )

            # Get the user messages
            user_messages = [msg for msg in messages if msg["role"] != "system"]

            # Convert messages to content
            if not user_messages:
                contents = "Follow the system instructions."
            elif len(user_messages) == 1 and isinstance(
                user_messages[0]["content"], str
            ):
                contents = [user_messages[0]["content"]]
            else:
                # Handle multiple messages or messages with images
                contents = []
                for message in user_messages:
                    if isinstance(message["content"], str):
                        contents.append(message["content"])
                    elif isinstance(message["content"], list):
                        text_parts = []
                        image_parts = []
                        for item in message["content"]:
                            if item.get("type") == "text":
                                text_parts.append(item["text"])
                            elif item.get("type") == "image_url":
                                image_path = item["image_url"]["url"]
                                # Handle PIL Image
                                if isinstance(image_path, Image.Image):
                                    image_parts.append(image_path)
                                # Handle file path
                                else:
                                    with open(image_path, "rb") as f:
                                        image_data = f.read()
                                    image_parts.append(
                                        Image.open(io.BytesIO(image_data))
                                    )

                        # Always ensure there's text content
                        if not text_parts:
                            text_parts.append("Consider this image in your response.")

                        # Add text as one part
                        contents.append(" ".join(text_parts))
                        # Add image parts
                        contents.extend(image_parts)

            # Configure response modalities to include both text and image
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_instruction,
                response_modalities=["Text", "Image"],
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE",
                    ),
                ],
            )

            response = self.client.models.generate_content(
                model=model.split("/")[-1],
                contents=contents,
                config=config,
            )

            # Process response to extract both text and images
            result = {"text": "", "images": []}

            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.text is not None:
                        result["text"] += part.text
                    elif part.inline_data is not None:
                        # Convert byte data to PIL Image
                        image = Image.open(io.BytesIO(part.inline_data.data))
                        result["images"].append(image)

            return result
        except Exception as e:
            raise e

    async def generate_async(
        self,
        messages,
        temperature,
        max_tokens,
        model="gemini/gemini-2.0-flash-exp-image-generation",
        **kwargs,
    ):
        # For simplicity, we'll use the synchronous version for now
        # In a real-world scenario, you might want to use an async implementation
        return self.generate(messages, temperature, max_tokens, model, **kwargs)


class DeepSeekProvider(AIProvider):
    supported_models = ["deepseek-chat", "deepseek-reasoner"]

    def __init__(self, api_key=None):
        self.sync_client = OpenAI(
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self.async_client = AsyncOpenAI(
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

    def generate(self, messages, temperature, max_tokens, model=None, **kwargs):
        raise NotImplementedError("This provider does not support image generation")

    async def generate_async(
        self, messages, temperature, max_tokens, model=None, **kwargs
    ):
        raise NotImplementedError("This provider does not support image generation")

    def call_ai(
        self, messages, temperature, max_tokens, model="deepseek-chat", **kwargs
    ):
        try:
            response = self.sync_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e

    async def call_ai_async(
        self, messages, temperature, max_tokens, model="deepseek-chat", **kwargs
    ):
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e


class AIManager:
    def __init__(self):
        self.providers = {}

    def add_provider(self, provider):
        self.providers[provider.__class__.__name__] = provider

    def get_provider(self, model):
        for provider in self.providers.values():
            if model in provider.supported_models:
                return provider
        raise ValueError(f"No provider found for model: {model}")

    def call_ai(self, messages, temperature, max_tokens, model, **kwargs):
        provider = self.get_provider(model)
        if provider:
            """
            text_messages = [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                    if isinstance(msg["content"], str)
                    else "",
                }
                for msg in messages
            ]
            """
            # Calculate prompt cost estimate
            try:
                # prompt_cost = float(calculate_prompt_cost(text_messages, model))
                prompt_cost = 0.0
            except Exception:
                prompt_cost = 0.0

            response = provider.call_ai(
                messages, temperature, max_tokens, model, **kwargs
            )

            # Calculate completion cost estimate
            try:
                # completion_cost = float(calculate_completion_cost(response, model))
                completion_cost = 0.0
            except Exception:
                completion_cost = 0.0

            total_cost = prompt_cost + completion_cost

            return response, total_cost
        else:
            raise ValueError(f"No provider found for model: {model}")

    # TODO shouldn't be 0 when no model...
    async def call_ai_async(self, messages, temperature, max_tokens, model, **kwargs):
        provider = self.get_provider(model)
        if provider:
            """
            text_messages = [
                {
                    "role": msg["role"],
                    "content": msg["content"]
                    if isinstance(msg["content"], str)
                    else "",
                }
                for msg in messages
            ]
            """
            # Calculate cost estimate
            try:
                # prompt_cost = float(calculate_prompt_cost(text_messages, model))
                prompt_cost = 0.0
            except Exception:
                prompt_cost = 0.0

            response = await provider.call_ai_async(
                messages, temperature, max_tokens, model, **kwargs
            )

            try:
                # completion_cost = float(calculate_completion_cost(response, model))
                completion_cost = 0.0
            except Exception:
                completion_cost = 0.0

            total_cost = prompt_cost + completion_cost

            return response, total_cost
        else:
            raise ValueError(f"No provider found for model: {model}")

    def generate(self, messages, temperature, max_tokens, model, **kwargs):
        provider = self.get_provider(model)
        if provider:
            try:
                prompt_cost = 0.0  # Cost calculation could be implemented later

                response = provider.generate(
                    messages, temperature, max_tokens, model, **kwargs
                )

                completion_cost = 0.0  # Cost calculation could be implemented later
                total_cost = prompt_cost + completion_cost

                return response, total_cost
            except NotImplementedError:
                raise ValueError(f"Model {model} does not support image generation")
        else:
            raise ValueError(f"No provider found for model: {model}")

    async def generate_async(self, messages, temperature, max_tokens, model, **kwargs):
        provider = self.get_provider(model)
        if provider:
            try:
                prompt_cost = 0.0  # Cost calculation could be implemented later

                response = await provider.generate_async(
                    messages, temperature, max_tokens, model, **kwargs
                )

                completion_cost = 0.0  # Cost calculation could be implemented later
                total_cost = prompt_cost + completion_cost

                return response, total_cost
            except NotImplementedError:
                raise ValueError(f"Model {model} does not support image generation")
        else:
            raise ValueError(f"No provider found for model: {model}")


@retry(
    retry=(
        retry_if_exception_type(APITimeoutError)
        | retry_if_exception_type(APIConnectionError)
        | retry_if_exception_type(RateLimitError)
        | retry_if_exception_type(APIStatusError)
        | retry_if_exception_type(google_exceptions.DeadlineExceeded)
        | retry_if_exception_type(google_exceptions.ServiceUnavailable)
        | retry_if_exception_type(google_exceptions.ResourceExhausted)
        | retry_if_exception_type(anthropic.InternalServerError)
    ),
    wait=wait_exponential(multiplier=2, min=2, max=120),
    stop=stop_after_attempt(3),
    reraise=True,
)
def call_ai_with_retry(ai_manager, messages, temperature, max_tokens, model, **kwargs):
    response, cost = ai_manager.call_ai(
        messages, temperature, max_tokens, model=model, **kwargs
    )
    return response, cost


@retry(
    retry=(
        retry_if_exception_type(APITimeoutError)
        | retry_if_exception_type(APIConnectionError)
        | retry_if_exception_type(RateLimitError)
        | retry_if_exception_type(APIStatusError)
        | retry_if_exception_type(google_exceptions.DeadlineExceeded)
        | retry_if_exception_type(google_exceptions.ServiceUnavailable)
        | retry_if_exception_type(google_exceptions.ResourceExhausted)
        | retry_if_exception_type(anthropic.InternalServerError)
    ),
    wait=wait_exponential(multiplier=2, min=2, max=120),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def call_ai_async_with_retry(
    ai_manager, messages, temperature, max_tokens, model, **kwargs
):
    response, cost = await ai_manager.call_ai_async(
        messages, temperature, max_tokens, model=model, **kwargs
    )
    return response, cost


# Add retry wrapper functions
@retry(
    retry=(
        retry_if_exception_type(APITimeoutError)
        | retry_if_exception_type(APIConnectionError)
        | retry_if_exception_type(RateLimitError)
        | retry_if_exception_type(APIStatusError)
        | retry_if_exception_type(google_exceptions.DeadlineExceeded)
        | retry_if_exception_type(google_exceptions.ServiceUnavailable)
        | retry_if_exception_type(google_exceptions.ResourceExhausted)
        | retry_if_exception_type(anthropic.InternalServerError)
    ),
    wait=wait_exponential(multiplier=2, min=2, max=120),
    stop=stop_after_attempt(3),
    reraise=True,
)
def generate_with_retry(ai_manager, messages, temperature, max_tokens, model, **kwargs):
    response, cost = ai_manager.generate(
        messages, temperature, max_tokens, model=model, **kwargs
    )
    return response, cost


@retry(
    retry=(
        retry_if_exception_type(APITimeoutError)
        | retry_if_exception_type(APIConnectionError)
        | retry_if_exception_type(RateLimitError)
        | retry_if_exception_type(APIStatusError)
        | retry_if_exception_type(google_exceptions.DeadlineExceeded)
        | retry_if_exception_type(google_exceptions.ServiceUnavailable)
        | retry_if_exception_type(google_exceptions.ResourceExhausted)
        | retry_if_exception_type(anthropic.InternalServerError)
    ),
    wait=wait_exponential(multiplier=2, min=2, max=120),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def generate_async_with_retry(
    ai_manager, messages, temperature, max_tokens, model, **kwargs
):
    response, cost = await ai_manager.generate_async(
        messages, temperature, max_tokens, model=model, **kwargs
    )
    return response, cost


class AIManagerSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AIManager()
            # Initialize providers only when needed
            if os.getenv("OPENAI_API_KEY"):
                try:
                    cls._instance.add_provider(OpenAIProvider())
                except Exception as e:
                    print(f"Error adding OpenAI provider: {e}")
            if os.getenv("ANTHROPIC_API_KEY"):
                try:
                    cls._instance.add_provider(AnthropicProvider())
                except Exception as e:
                    print(f"Error adding Anthropic provider: {e}")
            if os.getenv("GOOGLE_API_KEY"):
                try:
                    cls._instance.add_provider(GeminiProvider())
                except Exception as e:
                    print(f"Error adding Gemini provider: {e}")
            if os.getenv("DEEPSEEK_API_KEY"):
                try:
                    cls._instance.add_provider(DeepSeekProvider())
                except Exception as e:
                    print(f"Error adding DeepSeek provider: {e}")

            if os.getenv("LMSTUDIO_IP") and os.getenv("LMSTUDIO_PORT"):
                try:
                    cls._instance.add_provider(
                        LMStudioProvider(
                            ip_address=os.getenv("LMSTUDIO_IP", "192.168.11.34"),
                            port=int(os.getenv("LMSTUDIO_PORT", "1234")),
                        )
                    )
                except Exception as e:
                    print(f"Error adding LMStudio provider: {e}")

        return cls._instance


def call_ai(
    model: str, messages: List[Message], temperature=0.1, max_tokens=4096, **kwargs
):
    ai_manager = AIManagerSingleton.get_instance()
    return call_ai_with_retry(
        ai_manager, messages, temperature, max_tokens, model, **kwargs
    )


def call_ai_async(
    model: str, messages: List[Message], temperature=0.1, max_tokens=4096, **kwargs
):
    ai_manager = AIManagerSingleton.get_instance()
    return call_ai_async_with_retry(
        ai_manager, messages, temperature, max_tokens, model, **kwargs
    )


def generate(
    model: str, messages: List[Message], temperature=0.1, max_tokens=4096, **kwargs
):
    ai_manager = AIManagerSingleton.get_instance()
    return generate_with_retry(
        ai_manager, messages, temperature, max_tokens, model, **kwargs
    )


async def generate_async(
    model: str, messages: List[Message], temperature=0.1, max_tokens=4096, **kwargs
):
    ai_manager = AIManagerSingleton.get_instance()
    return generate_async_with_retry(
        ai_manager, messages, temperature, max_tokens, model, **kwargs
    )
