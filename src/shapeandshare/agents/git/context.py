from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.framework.common.config.environment import demand_env_var, demand_env_var_as_float, demand_env_var_as_int
from ..core.framework.contracts.dtos.llm_hyperparameters import LLMHyperParameters
from ..core.framework.contracts.dtos.rabbitmq_config import RabbitMQConfig
from ..core.infrastructure.messaging.rabbitmq.publisher import MessagePublisher
from ..core.infrastructure.persistence.chromadb.utils import get_chroma_client
from ..core.infrastructure.persistence.git.dao import GitDao
from ..core.infrastructure.persistence.mongodb.dao_legacy import MongoDaoLegacy, get_mongodb
from ..core.services.chathistory.sdk.client.chathistory import ChatHistoryClient
from ..core.services.vector.service import VectorService
from .agent import GitAgent
from .prompts import question_answering_prompt
from .sdk.client.git import GitAgentClient
from .services.analysis.service import AnalysisService
from .services.metadata.service import MetadataService
from .services.repository.service import RepositoryService

context = {}


def build_runtime_context() -> None:
    # RabbitMQ Configuration
    context["rabbitmq_config"] = RabbitMQConfig(
        hostname=demand_env_var(name="RABBITMQ_HOSTNAME"),
        port=demand_env_var_as_int(name="RABBITMQ_PORT"),
        username=demand_env_var(name="RABBITMQ_USERNAME"),
        password=demand_env_var(name="RABBITMQ_PASSWORD"),
    )

    context["publisher"] = MessagePublisher(config=context["rabbitmq_config"], exchange_name="git_agent")

    params: LLMHyperParameters = LLMHyperParameters(
        model=demand_env_var(name="LLM_HYPERPARAMETER_MODEL"),
        temperature=demand_env_var_as_float(name="LLM_HYPERPARAMETER_TEMPERATURE"),
        max_tokens=demand_env_var_as_int(name="LLM_HYPERPARAMETER_MAX_TOKENS"),
        timeout=demand_env_var_as_int(name="LLM_HYPERPARAMETER_TIMEOUT"),
        max_retries=demand_env_var_as_int(name="LLM_HYPERPARAMETER_RETRIES"),
    )
    context["llm"] = ChatOpenAI(**params.model_dump())
    context["vector_service"] = VectorService(
        client=get_chroma_client(),
        embedder=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    )
    context["repository_service"] = RepositoryService(git=GitDao())
    context["chathistory_client"] = ChatHistoryClient()
    context["metadata_service"] = MetadataService(dao=MongoDaoLegacy(database=get_mongodb()))
    context["analysis_service"] = AnalysisService(
        repository_service=context["repository_service"],
        default_extensions={".py", ".md", ".txt", ".yaml", ".yml", ".sh", ".toml", ".env"},
        default_included_files={"Makefile"},
        default_excluded_dirs={".git", "__pycache__", "node_modules", "venv", ".env", ".idea"},
    )
    context["text_splitter"] = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    context["agent"] = GitAgent(
        repository_service=context["repository_service"],
        analysis_service=context["analysis_service"],
        metadata_service=context["metadata_service"],
        chathistory_client=context["chathistory_client"],
        vector_service=context["vector_service"],
        publisher=context["publisher"],
        llm=context["llm"],
        document_chain=create_stuff_documents_chain(context["llm"], question_answering_prompt),
        text_splitter=context["text_splitter"],
    )
    context["git_agent_client"] = GitAgentClient()
