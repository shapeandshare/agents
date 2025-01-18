# Git Agent

A reference implementation of the Agents framework that provides natural language interaction with Git repositories. The Git agent enables intelligent analysis of code repositories through an event-driven architecture, allowing users to query and understand codebases using natural language.

## Directory Structure

```
git/
├── api/                 # API service implementation
│   ├── middleware/      # Error handling and middleware
│   └── routers/         # FastAPI route definitions
├── charts/              # Helm deployment charts
│   └── git-agent/       # Git agent deployment configuration
├── sdk/                 # Public SDK
│   └── client/          # git client
│       ├── commands/    # internal git client commands
│   └── contracts/       # Data contracts and types
│       ├── dtos/        # Data transfer objects
│       └── types/       # Type definitions
├── services/            # Business services
│   ├── analysis/        # Content analysis 
│   ├── metadata/        # Metadata management
│   └── repository/      # Repository operations
└── workers/             # Background workers
    ├── analysis.py      # Content analysis worker
    └── repository.py    # Repository management worker
```

## Components

### API Layer

#### FastAPI Service
RESTful API handling client interactions:

- `POST /git/question`: Process chat queries
- `POST /git`: Initialize repository processing
- `DELETE /git`: Remove repository data
- `GET /metrics/health`: Health check endpoint

### Worker Layer

#### Repository Worker
Handles repository management operations:
- Repository cloning
- File system cleanup
- Event publishing
- Repository deletion

#### Analysis Worker
Processes repository content:
- Content extraction
- File filtering
- Chunk generation
- Vector embedding creation
- Status management

### Business Services

#### Repository Service
- Repository cloning operations
- File content extraction
- Repository cleanup
- File system operations

#### Analysis Service
- Content extraction
- File filtering
- Content processing
- Extension management

#### Chat History Service
- Conversation tracking
- Message storage
- History retrieval
- History cleanup

#### Metadata Service
- Status tracking
- Collection management
- Metadata operations
- State transitions

### Event System

#### Repository Events
- `REPOSITORY_PROCESS`: Initialize processing
- `REPOSITORY_CLONED`: Repository cloning completed
- `REPOSITORY_ANALYZED`: Analysis completed
- `REPOSITORY_DELETED`: Cleanup completed

#### Analysis Events
- `ANALYSIS_STARTED`: Begin content analysis
- `ANALYSIS_COMPLETED`: Analysis success
- `ANALYSIS_FAILED`: Analysis error

#### Vector Store Events
- `VECTORS_CREATED`: Embeddings created
- `VECTORS_DELETED`: Collection removed

### Setup

#### Prerequisites
- Kubernetes cluster
- Helm v3+
- Python 3.12+
- OpenAI API key

#### Environment Configuration
Configure `.env` file using the sample `.env.sample`:
```env
OPENAI_API_KEY=<key>
HASH_KEY=<key>
DATA_BASE_DIR=data

# Huggingface
HF_HOME=data/cache/hf
TOKENIZERS_PARALLELISM=false

# Infrastructure
CHROMADB_HOSTNAME=localhost
CHROMADB_PORT=8000
MONGODB_HOSTNAME=localhost
MONGODB_PORT=27017
RABBITMQ_HOSTNAME=localhost
RABBITMQ_PORT=5672
```

#### Installation

1. Setup development environment:
```bash
make setup
make prepare
```

2. Build components:
```bash
make build
```

3. Deploy infrastructure:
```bash
make install
```

4. Deploy Git agent:
```bash
make git-agent-install-dev
```

## Processing Pipeline

### Repository Processing Flow

1. **Initialization**
   - Receive repository URL
   - Generate identifiers
   - Create metadata
   - Queue processing task

2. **Repository Cloning**
   - Repository worker clones repository
   - Creates local storage
   - Publishes cloned event
   - Updates processing status

3. **Content Analysis**
   - Analysis worker extracts content
   - Filters relevant files
   - Generates content chunks
   - Creates vector embeddings
   - Updates completion status

### Query Processing Flow

1. **Request Processing**
   - Validate repository status
   - Load chat history
   - Transform query for context

2. **Context Loading**
   - Retrieve relevant vectors
   - Build context window
   - Generate LLM prompt

3. **Response Generation**
   - Query language model
   - Store chat history
   - Return formatted response

### Cleanup Flow

1. **Deletion Request**
   - Verify repository exists
   - Queue deletion tasks

2. **Resource Cleanup**
   - Remove vector collection
   - Delete metadata
   - Clear chat history
   - Clean file system
   - Update status
