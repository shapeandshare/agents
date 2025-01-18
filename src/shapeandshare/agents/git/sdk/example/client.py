import asyncio
import logging

import click
from dotenv import load_dotenv
from pydantic import BaseModel

from ..client.git import GitAgentClient
from ..contracts.dtos.git_metadata import GitMetadata

load_dotenv(dotenv_path=".env", verbose=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class GitAgentConsumer(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    user_id: str
    client: GitAgentClient

    async def setup_context(self, repository_url: str) -> None:
        try:
            metadata: GitMetadata = await self.client.repository_ingest(
                user_id=self.user_id, repository_url=repository_url
            )
            print(metadata)
        except Exception as error:
            logger.warning(str(error))

    async def converse(self, repository_url: str, prompt: str) -> str:
        response: str = (await self.client.chat(user_id=self.user_id, repository_url=repository_url, prompt=prompt))[
            "answer"
        ]
        return response


@click.command()
@click.option("--user-id", type=click.STRING, help="user")
@click.option("--repository-url", type=click.STRING, help="report url")
@click.option("--prompt", type=click.STRING, default="", help="prompt")
def handler(user_id: str, repository_url: str, prompt: str):
    agent = GitAgentConsumer(client=GitAgentClient(), user_id=user_id)
    if len(prompt) < 1:
        asyncio.run(agent.setup_context(repository_url=repository_url))
    else:
        response: str = asyncio.run(agent.converse(repository_url=repository_url, prompt=prompt))
        print(response)


if __name__ == "__main__":
    handler()
