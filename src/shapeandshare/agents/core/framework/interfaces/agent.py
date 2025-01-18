import logging
from abc import abstractmethod
from typing import Any

from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from ....git.prompts import query_transform_prompt
from ....git.sdk.contracts.dtos.chat import BaseChatRequest, ChatRequest
from ...services.chathistory.sdk.client.chathistory import ChatHistoryClient
from ...services.chathistory.sdk.contacts.models.conversation import Conversation
from ...services.vector.service import VectorService
from ..contracts.dtos.chat_history import ChatHistory

logger = logging.getLogger()


class BaseAgent(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    llm: ChatOpenAI
    document_chain: Any
    vector_service: VectorService
    chathistory_client: ChatHistoryClient

    """ """

    @abstractmethod
    def _load_context(self, request: BaseChatRequest) -> Chroma:
        """ """

    async def generate_response(self, vectorstore: Chroma, request: ChatRequest) -> dict:
        retriever: VectorStoreRetriever = vectorstore.as_retriever(k=request.k)  # k -- the number of docs to return

        query_transforming_retriever_chain = RunnableBranch(
            (
                lambda x: len(x.get("messages", [])) == 1,
                # If only one message, then we just pass that message's content to retriever
                (lambda x: x["messages"][-1].content) | retriever,
            ),
            # If messages, then we pass inputs to LLM chain to transform the query, then pass to retriever
            query_transform_prompt | self.llm | StrOutputParser() | retriever,
        ).with_config(run_name="chat_retriever_chain")

        conversational_retrieval_chain = RunnablePassthrough.assign(
            context=query_transforming_retriever_chain,
        ).assign(
            answer=self.document_chain,
        )

        conversation: Conversation = await self.chathistory_client.message_add(
            conversation_id=request.conversation_id, user_id=request.id, role="user", content=request.prompt
        )
        history: ChatHistory = ChatHistory(conversation_id=request.conversation_id, history=[])
        for message in conversation.messages:
            if message.role == "user":
                history.history.append(HumanMessage(content=message.content))
            else:
                history.history.append(AIMessage(content=message.content))

        response = conversational_retrieval_chain.invoke(
            {
                "messages": history.history,
            }
        )
        await self.chathistory_client.message_add(
            conversation_id=request.conversation_id,
            user_id=request.id,
            role="assistant",
            content=response["answer"],
        )
        return {"answer": response["answer"]}
