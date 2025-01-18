from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_TEMPLATE = """
You are a knowledgeable assistant analyzing a codebase. Answer questions based on the provided context below.

Guidelines:
- Focus on information explicitly present in the context
- If the context doesn't contain relevant information, respond with "I don't know"
- When discussing code, reference specific files and line numbers when possible
- Consider the broader architectural context when explaining components
- For technical questions, include relevant code snippets in your explanation
- Use markdown formatting for code and technical terms

<context>
{context}
</context>
"""

question_answering_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_TEMPLATE,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


QUERY_TRANSFORM_TEMPLATE = """
Given the conversation history, generate a precise search query to find relevant information in the codebase.

Guidelines:
- Focus on technical terms, file names, and code concepts
- Include relevant file extensions if mentioned
- Prioritize architectural terms when discussing system design
- Consider related components that might be relevant
- Keep the query concise but specific

Only return the search query, no additional text.
"""

query_transform_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        ("user", QUERY_TRANSFORM_TEMPLATE),
    ]
)
