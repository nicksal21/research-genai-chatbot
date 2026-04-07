"""
Business logic for AI agent with knowledge base integration.
"""
from dotenv import load_dotenv
load_dotenv()
import os
from llama_index.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.llms import ChatMessage, MessageRole

retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=os.getenv("BEDROCK_KNOWLEDGE_BASE_ID"),
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 8}},
    )
llm = OpenAI(model=os.getenv("OPENAI_MODEL"))

_knowledge_base_tool = QueryEngineTool.from_defaults(
    query_engine=RetrieverQueryEngine(retriever=retriever),
    name="amazon_knowledge_base",
    description=(
        "A vector database of knowledge about 2023 Florida Building Codes."
    ),
)

agent = ReActAgent(
    tools=[_knowledge_base_tool],
    llm=llm,
    system_prompt = """
    You are a helpful AI assistant with access to a vector database about the 2023 Florida Building Codes.

    When a user asks a building-code question, use the available retrieval tool to find the answer.

    Requirements for every building-code answer:
    1. Answer in English.
    2. Always cite the exact section and subsection used.  For example: "In section 302.2..." or "According to section 115.1...".
    3. Be concise.
    4. Answer only from retrieved building-code content.
    5. Do not use outside knowledge.
    6. When listing examples, use only examples explicitly present in the retrieved source.
    7. Cite figures only when a figure is actually referenced by the retrieved material.
    8. If the retrieved material is insufficient, say so instead of guessing.
    """,
)

import re

CITATION_PATTERNS = [
    r"Section\s+\d+(\.\d+)*",
    r"Sections?\s+\d+(\.\d+)*",
    r"\b\d+(\.\d+)+\b",   # catches things like 303.2
]

def has_required_citation(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in CITATION_PATTERNS)


async def get_agent_response(message, chat_history):
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(ChatMessage(role=MessageRole.USER, content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=msg["content"]))

    user_message = ChatMessage(role=MessageRole.USER, content=message)

    response = await agent.run(user_message, chat_history=messages)
    answer = str(response)

    if has_required_citation(answer):
        return answer

    retry_message = ChatMessage(
        role=MessageRole.USER,
        content=(
            f"{message}\n\n"
            "You must answer only from retrieved code content and include the exact section/subsection citation. "
            "If you cannot cite the retrieved source, say you cannot verify it."
        ),
    )

    retry_response = await agent.run(retry_message, chat_history=messages)
    retry_answer = str(retry_response)

    if has_required_citation(retry_answer):
        return retry_answer

    return (
        "I could not verify this answer from the retrieved building-code text with an exact citation."
    )