from typing import Optional, AsyncGenerator
from app.core.config import settings
import anthropic
import openai
import json


class LLMService:
    def __init__(self):
        self.claude_client: Optional[anthropic.AsyncAnthropic] = None
        self.openai_client: Optional[openai.AsyncOpenAI] = None

    def _get_claude(self) -> anthropic.AsyncAnthropic:
        if self.claude_client is None:
            self.claude_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self.claude_client

    def _get_openai(self) -> openai.AsyncOpenAI:
        if self.openai_client is None:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        return self.openai_client

    def _build_system_prompt(self, contexts: list[dict]) -> str:
        docs = "\n\n".join(
            f"[Source: Document {c['document_id'][:8]}, Page {c.get('page_number', 'N/A')}]\n{c['content']}"
            for c in contexts
        )
        return f"""You are an AI assistant that answers questions based on the provided documents.

Rules:
1. Answer ONLY using the provided context. If the context doesn't contain the answer, say: "I couldn't find relevant information in the uploaded documents."
2. Always cite sources using [Source: doc_id, Page X] notation.
3. Be precise and concise. Use bullet points for lists.
4. If the user asks in Indonesian, answer in Indonesian. Otherwise, answer in English.

Context:
{docs}"""

    def _build_messages(self, history: list[dict], query: str) -> list[dict]:
        messages = []
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})
        return messages

    async def stream_chat(
        self, query: str, contexts: list[dict], history: list[dict]
    ) -> AsyncGenerator[str, None]:
        system_prompt = self._build_system_prompt(contexts)
        messages = self._build_messages(history, query)

        if settings.llm_provider == "claude":
            client = self._get_claude()
            async with client.messages.stream(
                model=settings.llm_model,
                system=system_prompt,
                messages=messages,
                max_tokens=4096,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            client = self._get_openai()
            stream = await client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                stream=True,
                max_tokens=4096,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    async def chat(self, query: str, contexts: list[dict], history: list[dict]) -> str:
        system_prompt = self._build_system_prompt(contexts)
        messages = self._build_messages(history, query)

        if settings.llm_provider == "claude":
            client = self._get_claude()
            response = await client.messages.create(
                model=settings.llm_model,
                system=system_prompt,
                messages=messages,
                max_tokens=4096,
            )
            return response.content[0].text
        else:
            client = self._get_openai()
            response = await client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "system", "content": system_prompt}, *messages],
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""
