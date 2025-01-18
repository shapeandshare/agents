# Agents

A Kubernetes-based framework for building AI-powered agents with a reference implementation for Git repository analysis. The framework provides core components and abstractions for developing specialized agents that can leverage language models, vector storage, and persistent data management. The included Git analysis service demonstrates these capabilities by enabling natural language interactions with code repositories.
## Overview

The Agents framework consists of:

### Core Framework
- Base agent interfaces and implementations
- Event-driven messaging infrastructure
- Common persistence interfaces
- Standardized service patterns
- Environment configuration utilities

### Infrastructure Components
- MongoDB for persistent storage and metadata
- ChromaDB for vector embeddings and search
- RabbitMQ for event messaging and task queues

### Services Layer
- Vector processing service
- Chat history management
- Repository analysis service
- Metadata management service

### Reference Implementation
The Git Agent serves as a complete reference implementation demonstrating the framework's capabilities.

The Agents system is designed to:
- Clone and analyze Git repositories
- Generate vector embeddings of repository content
- Store repository metadata and chat history
- Enable natural language interactions with codebases
- Scale horizontally in Kubernetes environments

Key Features:
- RESTful API interface
- Persistent vector storage using ChromaDB
- Metadata and chat history storage using MongoDB
- Kubernetes-native deployment
- Horizontal pod autoscaling
- Configurable resource management
- Support for multiple concurrent repository analyses

## System Architecture

### Core Components
1. **Base Framework (`/core`)**
   - Framework contracts (DTOs, interfaces, errors)
   - Infrastructure layer (MongoDB, ChromaDB, RabbitMQ)
   - Common services (vector operations, chat history)
   - Configuration management
   - Error handling middleware

2. **Git Agent (`/git`)**
   - API layer (FastAPI endpoints)
   - Background workers
   - Business services
   - Domain models
   - Event handlers

3. **Infrastructure Services**
   - ChromaDB (vector storage)
   - MongoDB (metadata and chat history)
   - RabbitMQ (message queue)
   - Kubernetes deployment

The system consists of several key components deployed in a Kubernetes cluster:

```mermaid
flowchart TB
    %% Main Applications
    subgraph GitAgentAPI["Git Agent API Service"]
        direction TB
        FastAPI["FastAPI Router"]
        GitRouter["Git Router"]
        MetricsRouter["Metrics Router"]
        
        FastAPI --> GitRouter
        FastAPI --> MetricsRouter
        
        subgraph GitEndpoints["Git Endpoints"]
            PostQuestion["POST /git/question"]
            PostRepository["POST /git"]
            DeleteRepository["DELETE /git"]
        end
        
        GitRouter --> PostQuestion
        GitRouter --> PostRepository
        GitRouter --> DeleteRepository
    end

    subgraph ChatHistoryService["Chat History Service"]
        direction TB
        ChatAPI["FastAPI Router"]
        
        subgraph ChatEndpoints["Chat Endpoints"]
            ListConvos["GET /conversations"]
            CreateConvo["POST /conversations"]
            AddMessage["POST /messages"]
            GetConvo["GET /conversation"]
            DeleteConvo["DELETE /conversation"]
        end
        
        ChatAPI --> ListConvos
        ChatAPI --> CreateConvo
        ChatAPI --> AddMessage
        ChatAPI --> GetConvo
        ChatAPI --> DeleteConvo
    end

    subgraph GitWorkers["Git Workers"]
        direction TB
        RepoWorker["Repository Worker"]
        AnalysisWorker["Analysis Worker"]
          
        subgraph WorkerServices["Worker Services"]
            MetadataService["Metadata Service"]
            RepoService["Repository Service"]
            AnalysisService["Analysis Service"]
            VectorService["Vector Service"]
        end
        
        RepoWorker --> RepoService
        AnalysisWorker --> AnalysisService
        AnalysisWorker --> VectorService
        
        %% Metadata Service Connections
        GitAgentAPI --> MetadataService
        AnalysisWorker --> GitClient
    end

    %% Infrastructure Services
    subgraph Infrastructure["Infrastructure Services"]
        direction TB
        MongoDB[(MongoDB)]
        ChromaDB[(ChromaDB)]
        RabbitMQ[("RabbitMQ\nEvent Bus")]
        FileSystem[("FileSystem")]
    end

    %% External Services
    subgraph External["External Services"]
        direction TB
        OpenAI["OpenAI GPT-4"]
        HuggingFace["HuggingFace Models"]
        GitRepos["Git Repositories"]
    end

    %% Application Connections
    Client([Client Applications]) --> GitClient
    GitClient["Git Agent Client"] --> GitAgentAPI
    
    %% Git Agent API Connections
    GitAgentAPI --> |"Chat History\nOperations"| ChatHistoryService
    GitAgentAPI --> |"Vector\nOperations"| ChromaDB
    GitAgentAPI --> |"Queue\nEvents"| RabbitMQ
    GitAgentAPI --> |"LLM\nQueries"| OpenAI
    
    %% Git Workers Connections
    RabbitMQ --> |"Repository\nEvents"| RepoWorker
    RabbitMQ --> |"Analysis\nEvents"| AnalysisWorker
    RepoService --> |"Clone"| GitRepos
    AnalysisService --> |"Process"| VectorService
    VectorService --> |"Store"| ChromaDB
    VectorService --> |"Generate\nEmbeddings"| HuggingFace
    RepoService --> FileSystem
    AnalysisService --> FileSystem
    
    %% Storage Connections
    ChatHistoryService --> MongoDB
    MetadataService --> |"Store/Retrieve\nMetadata"| MongoDB

    %% Styling
    classDef primary fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    classDef secondary fill:#E1F5FE,stroke:#0288D1,stroke-width:2px
    classDef worker fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px
    classDef infra fill:#EFEBE9,stroke:#5D4037,stroke-width:2px
    classDef external fill:#E8EAF6,stroke:#3F51B5,stroke-width:2px
    classDef metadata fill:#FFE0B2,stroke:#FF9800,stroke-width:2px

    class GitAgentAPI,FastAPI,GitRouter,MetricsRouter,GitEndpoints primary
    class ChatHistoryService,ChatAPI,ChatEndpoints,ChatStorage secondary
    class GitWorkers,RepoWorker,AnalysisWorker,WorkerServices worker
    class MongoDB,ChromaDB,RabbitMQ infra
    class External,OpenAI,HuggingFace,GitRepos external
    class MetadataService metadata
```

Core Components:
- FastAPI Service: Handles HTTP requests and manages background tasks
- Git Agent: Processes repositories and manages interactions with AI models
- ChromaDB: Vector store for semantic search capabilities
- MongoDB: Persistent storage for metadata and chat history
- OpenAI GPT-4: Large language model for natural language understanding

## Component Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Service
    participant Agent as Git Agent
    participant MetaService as Metadata Service
    participant ChatService as Chat History Service
    participant Queue as RabbitMQ
    participant RepWorker as Repository Worker
    participant AnaWorker as Analysis Worker
    participant GitClient as Git Agent Client
    participant RepoService as Repository Service
    participant AnaService as Analysis Service
    participant VecService as Vector Service
    participant Git as Git Repository
    participant DB as MongoDB
    participant Chroma as ChromaDB
    participant LLM as OpenAI GPT-4
    participant HF as HuggingFace

    %% Chat request flow
    Client->>API: POST /git/question (url, prompt, id)
    API->>Agent: generate_chat_response(request)
    Agent->>MetaService: Check repository status
    MetaService->>DB: Get metadata by hash(id+url)
    
    alt Repository Not Processed
        Note over Agent,Queue: Start Repository Processing Flow
        Agent->>ChatService: conversation_create(user_id)
        ChatService->>DB: Save conversation
        Note over Agent: Generate storage_id hash(id+url)
        Agent->>MetaService: Create metadata (SUBMITTED)
        MetaService->>DB: Store metadata with col_id
        Agent->>MetaService: Update status (PROCESSING)
        MetaService->>DB: Update metadata
        Agent->>Queue: Publish repository.process event
        
        %% Repository Worker Flow
        Queue->>RepWorker: Consume repository.process event
        RepWorker->>RepoService: clone(url, repository_id)
        RepoService->>Git: Clone repository
        RepWorker->>Queue: Publish repository.cloned event

        %% Analysis Worker Flow
        Queue->>AnaWorker: Consume repository.cloned event
        AnaWorker->>AnaService: extract_repository_content
        AnaService->>RepoService: files_list(repository_id)
        AnaService->>RepoService: file_content_read(repository_id, file)
        Note over AnaService: Filter by extensions/rules
        AnaWorker->>VecService: Create collection
        loop For each file
            AnaWorker->>AnaWorker: Split content into chunks
            AnaWorker->>HF: Generate embeddings
            AnaWorker->>Chroma: Store document chunks & embeddings
        end
        AnaWorker->>GitClient: status_update(COMPLETED)
        GitClient->>API: PUT /git (status update)
        API->>MetaService: Update metadata status
        MetaService->>DB: Update metadata
        AnaWorker->>Queue: Publish repository.analyzed event
        API-->>Client: Return 202 Accepted

    else Repository Ready
        Agent->>ChatService: conversation_get(conversation_id)
        ChatService->>DB: Load conversation history
        Agent->>VecService: get_vectorstore(col_id)
        Agent->>LLM: Transform search query
        Agent->>VecService: Search related content
        VecService->>Chroma: similarity_search
        Agent->>LLM: Generate response with context
        Agent->>ChatService: message_add(conversation_id, response)
        ChatService->>DB: Store message
        Agent-->>Client: Return 200 with response
    end

    %% Repository deletion flow
    rect rgb(240, 240, 240)
        Note right of Client: Repository Deletion Flow
        Client->>API: DELETE /git (url, id)
        API->>Agent: delete_context(request)
        Note over Agent: Start background task
        Agent->>VecService: Delete collection(col_id)
        Agent->>MetaService: Delete metadata
        MetaService->>DB: Remove metadata
        Agent->>ChatService: Delete conversation
        ChatService->>DB: Remove conversation
        API-->>Client: Return 202 Accepted
    end
```


### Data Flow

```mermaid
flowchart LR
    %% Repository Processing Flow
    subgraph Input[Repository Ingestion]
        RepoURL[Git Repository URL] --> Validate[Validate URL]
        Validate --> ProcessEvent[Repository Process Event]
        ProcessEvent --> Clone[Clone Repository]
        Clone --> CloneEvent[Repository Cloned Event]
        CloneEvent --> Extract[Extract Content]
        Extract --> FilterContent[Filter Content]
        FilterContent --> Chunks[Generate Chunks]
        Chunks --> SaveMetadata[Store Initial Metadata]
    end

    subgraph Analysis[Content Processing]
        Chunks --> GenEmbeddings[Generate Embeddings]
        GenEmbeddings --> StoreVectors[Store Vector Data]
        StoreVectors --> IndexVectors[Index Vectors]
        IndexVectors --> AnalyzedEvent[Repository Analyzed Event]
        AnalyzedEvent --> StatusUpdate[Git Agent Client Status Update]
        StatusUpdate --> APIUpdate[API Status Update]
        APIUpdate --> UpdateStatus[Update Processing Status]
        UpdateStatus --> Notify[Notify Completion]
    end
    
    subgraph Query[Chat Processing]
        Question[User Question] --> ValidateQuery[Validate Query]
        ValidateQuery --> CheckStatus[Check Repository Status]
        CheckStatus --> |If Ready| LoadHistory[Load Chat History]
        CheckStatus --> |Not Ready| ReturnStatus[Return Processing Status]
        LoadHistory --> LoadContext[Load Relevant Context]
        LoadContext --> TransformQuery[Transform Query]
        TransformQuery --> SearchVectors[Search Vector Store]
        SearchVectors --> RankResults[Rank Results]
        RankResults --> BuildPrompt[Build LLM Prompt]
        BuildPrompt --> GenerateResponse[Generate Response]
        GenerateResponse --> ValidateResponse[Validate Response]
        ValidateResponse --> SaveHistory[Store Chat History]
    end

    subgraph Storage[Persistent Storage]
        GitStorage[(Local Git Storage)]
        ChromaDB[(ChromaDB Vector Store)]
        MongoDB[(MongoDB Document Store)]
    end

    subgraph Events[Event Processing]
        EventBus{RabbitMQ Event Bus}
        ProcessEvent --> EventBus
        CloneEvent --> EventBus
        AnalyzedEvent --> EventBus
        Notify --> EventBus
    end

    %% Connect flows to storage
    Clone --> GitStorage
    StoreVectors --> ChromaDB
    IndexVectors --> ChromaDB
    SaveMetadata --> MongoDB
    UpdateStatus --> MongoDB
    SearchVectors --> ChromaDB
    SaveHistory --> MongoDB
    LoadHistory --> MongoDB
    LoadContext --> ChromaDB

    %% Error flows
    Validate --> |Invalid| ErrorHandler[Error Handler]
    Clone --> |Failed| ErrorHandler
    Extract --> |Failed| ErrorHandler
    GenEmbeddings --> |Failed| ErrorHandler
    ValidateQuery --> |Invalid| ErrorHandler
    ValidateResponse --> |Invalid| ErrorHandler
    StatusUpdate --> |Failed| ErrorHandler

    %% Style Definitions
    classDef process fill:#f9f,stroke:#333,stroke-width:2px
    classDef storage fill:#bbf,stroke:#333,stroke-width:2px
    classDef event fill:#bfb,stroke:#333,stroke-width:2px
    classDef error fill:#fbb,stroke:#333,stroke-width:2px
    classDef validate fill:#ffb,stroke:#333,stroke-width:2px
    classDef update fill:#dfd,stroke:#333,stroke-width:2px

    class Clone,Extract,GenEmbeddings,BuildPrompt,GenerateResponse process
    class GitStorage,MongoDB,ChromaDB storage
    class ProcessEvent,CloneEvent,AnalyzedEvent,EventBus event
    class ErrorHandler error
    class Validate,ValidateQuery,ValidateResponse validate
    class StatusUpdate,APIUpdate update
```

## Setup and Installation

### Prerequisites
- Kubernetes cluster
- Helm v3+
- Python 3.12+
- OpenAI API key


### Environment Configuration
Copy `.env.example` to `.env` and configure:
```
OPENAI_API_KEY=<<OPENAI API KEY>>
HASH_KEY=<<PRESHARED HASHING KEY>>
```
 