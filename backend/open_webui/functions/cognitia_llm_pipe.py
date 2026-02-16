"""
title: Cognitia LLM (ZeroGPU)
description: Connect to Cognitia LLM Space on HuggingFace with ZeroGPU (H200)
author: Cognitia
version: 1.0.0
requirements: aiohttp
"""

import json
import aiohttp
from typing import Optional, List, AsyncGenerator
from pydantic import BaseModel, Field


class Pipe:
    """
    Pipe for connecting to Cognitia LLM HuggingFace Space.
    Uses Gradio API with ZeroGPU (NVIDIA H200) acceleration.
    """

    class Valves(BaseModel):
        """Admin configuration for the pipe"""
        SPACE_URL: str = Field(
            default="https://Juansquiroga-cognitia-llm.hf.space",
            description="HuggingFace Space URL"
        )
        HF_TOKEN: str = Field(
            default="",
            description="HuggingFace API token for authenticated ZeroGPU access (higher quota)"
        )
        DEFAULT_MODEL: str = Field(
            default="qwen2.5-7b",
            description="Default model to use"
        )
        MAX_TOKENS: int = Field(
            default=512,
            description="Maximum tokens to generate"
        )
        TEMPERATURE: float = Field(
            default=0.7,
            description="Generation temperature"
        )
        TIMEOUT: int = Field(
            default=120,
            description="Request timeout in seconds"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.models = [
            {"id": "phi3", "name": "Phi-3 (3.8B) - Rapido"},
            {"id": "qwen2.5-7b", "name": "Qwen 2.5 (7B) - Alta calidad"},
            {"id": "smollm2-1.7b", "name": "SmolLM2 (1.7B) - Ultra rapido"},
            {"id": "mistral-7b", "name": "Mistral (7B) - Razonamiento"},
        ]

    def pipes(self) -> List[dict]:
        """Return list of available models as pipes"""
        return [
            {
                "id": model["id"],
                "name": f"cognitia/{model['name']}",
            }
            for model in self.models
        ]

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Optional[callable] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Main pipe function to process chat requests.

        Args:
            body: Request body containing messages and model
            __user__: User information
            __event_emitter__: Event emitter for streaming

        Yields:
            Response content chunks
        """
        try:
            # Extract model from the request
            model_id = body.get("model", self.valves.DEFAULT_MODEL)
            # Handle model names like "cognitia/phi3" -> "phi3"
            if "/" in model_id:
                model_id = model_id.split("/")[-1]

            # Validate model
            valid_models = [m["id"] for m in self.models]
            if model_id not in valid_models:
                model_id = self.valves.DEFAULT_MODEL

            # Extract messages
            messages = body.get("messages", [])
            if not messages:
                yield "Error: No messages provided"
                return

            # Convert messages to JSON string for Gradio
            messages_json = json.dumps([
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                for msg in messages
            ])

            # Get generation parameters
            max_tokens = body.get("max_tokens", self.valves.MAX_TOKENS)
            temperature = body.get("temperature", self.valves.TEMPERATURE)

            # Call Gradio API
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.valves.TIMEOUT)
            ) as session:
                # Step 1: Initiate the call
                call_url = f"{self.valves.SPACE_URL}/call/chat_completions"
                call_data = {
                    "data": [messages_json, model_id, max_tokens, temperature]
                }

                # Build headers with optional HF token for authenticated ZeroGPU access
                headers = {"Content-Type": "application/json"}
                if self.valves.HF_TOKEN:
                    headers["Authorization"] = f"Bearer {self.valves.HF_TOKEN}"

                async with session.post(
                    call_url,
                    json=call_data,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield f"Error: API returned {response.status}: {error_text}"
                        return

                    result = await response.json()
                    event_id = result.get("event_id")

                    if not event_id:
                        yield f"Error: No event_id in response: {result}"
                        return

                # Step 2: Fetch the result
                result_url = f"{self.valves.SPACE_URL}/call/chat_completions/{event_id}"

                async with session.get(result_url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield f"Error: Failed to get result: {error_text}"
                        return

                    # Parse SSE response
                    event_type = None
                    async for line in response.content:
                        line = line.decode("utf-8").strip()

                        # Track event type
                        if line.startswith("event: "):
                            event_type = line[7:]
                            continue

                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix

                            # Handle error events from ZeroGPU
                            if event_type == "error":
                                if data == "null" or data == "":
                                    yield "Error: ZeroGPU no disponible. El Space puede estar en cold start o con cuota agotada. Intenta de nuevo en unos segundos."
                                else:
                                    yield f"Error: {data}"
                                return

                            try:
                                # Parse the data array
                                parsed = json.loads(data)
                                if parsed is None:
                                    yield "Error: Respuesta vacia del servidor. ZeroGPU puede no estar disponible."
                                    return
                                if isinstance(parsed, list) and len(parsed) > 0:
                                    # Parse the OpenAI-format response
                                    openai_response = json.loads(parsed[0])
                                    if "choices" in openai_response:
                                        content = openai_response["choices"][0]["message"]["content"]
                                        yield content
                                    elif "error" in openai_response:
                                        yield f"Error: {openai_response['error']['message']}"
                            except json.JSONDecodeError:
                                continue

        except aiohttp.ClientError as e:
            yield f"Connection error: {str(e)}"
        except Exception as e:
            yield f"Error: {type(e).__name__}: {str(e)}"
