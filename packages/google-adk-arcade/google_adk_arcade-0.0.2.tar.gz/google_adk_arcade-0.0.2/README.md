<h3 align="center">
  <a name="readme-top"></a>
  <img
    src="https://docs.arcade.dev/images/logo/arcade-logo.png"
  >
</h3>
<div align="center">
  <h3>Arcade Integration for OpenAI Agents</h3>
    <a href="https://github.com/ArcadeAI/agents-arcade/blob/main/LICENSE">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</a>
  <a href="https://pypi.org/project/google-adk-arcade/">
    <img src="https://img.shields.io/pypi/v/google-adk-arcade.svg" alt="PyPI">
  </a>
</div>

<p align="center">
    <a href="https://docs.arcade.dev" target="_blank">Arcade Documentation</a> •
    <a href="https://docs.arcade.dev/toolkits" target="_blank">Toolkits</a> •
    <a href="https://github.com/ArcadeAI/arcade-py" target="_blank">Arcade Python Client</a> •
    <a href="https://platform.openai.com/docs/guides/agents" target="_blank">https://google.github.io/adk-docs/</a>
</p>

# agents-arcade

`agents-arcade` provides an integration between [Arcade](https://docs.arcade.dev) and the [Google ADK Python](https://github.com/google/adk-python). This allows you to enhance your AI agents with Arcade's extensive toolkit ecosystem, including tools that reqwuire authorization like Google Mail, Linkedin, X, and more.

## Installation

```bash
pip install google-adk-arcade
```

## Basic Usage

```python
import asyncio

from arcadepy import AsyncArcade
from dotenv import load_dotenv
from google.adk import Agent, Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.genai import types

from google_adk_arcade.tools import get_arcade_tools

load_dotenv(override=True)


async def main():
    app_name = 'my_app'
    user_id = 'mateo@arcade.dev'
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    client = AsyncArcade()

    google_tools = await get_arcade_tools(client, tools=["Google.ListEmails"])

    # authorize the tools
    for tool in google_tools:
        result = await client.tools.authorize(
            tool_name=tool.name,
            user_id=user_id
        )
        if result.status != "completed":
            print(f"Click this link to authorize {tool.name}:\n{result.url}")
        await client.auth.wait_for_completion(result)

    google_agent = Agent(
        model="gemini-2.0-flash",
        name="google_tool_agent",
        instruction="I can use Google tools to manage an inbox!",
        description="An agent equipped with tools to read Gmail emails. "
                    "Make sure to call google_listemails to read and summarize"
                    " emails",
        tools=google_tools,
    )
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, state={
            "user_id": user_id,
        }
    )
    runner = Runner(
        app_name=app_name,
        agent=google_agent,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    user_input = "summarize my latest 3 emails"
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=user_input)]
    )
    for event in runner.run(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content.parts and event.content.parts[0].text:
            print(f'** {event.author}: {event.content.parts[0].text}')

if __name__ == '__main__':
    asyncio.run(main())

```

## Key Features

-   **Easy Integration**: Simple API (one function) to connect Arcade tools with Google ADK
-   **Extensive Toolkit Support**: Access to all Arcade toolkits including Gmail, Google Drive, Search, and more
-   **Asynchronous Support**: Built with async/await for compatibility with Google ADK
-   **Authentication Handling**: Manages authorization for tools requiring user permissions like Google, LinkedIn, etc

## Available Toolkits

Arcade provides many toolkits including:

-   **Google**: Gmail, Google Drive, Google Calendar
-   **Search**: Google search, Bing search
-   **Web**: Crawling, scraping, etc
-   **Github**: Repository operations
-   **Slack**: Sending messages to Slack
-   **LinkedIn**: Posting to LinkedIn
-   **X**: Posting and reading tweets on X
-   And many more

For a complete list, see the [Arcade Toolkits documentation](https://docs.arcade.dev/toolkits).

## Authentication

Many Arcade tools require user authentication. The authentication flow is managed by Arcade and can be triggered by providing a `user_id` in the context when running your agent. Refer to the Arcade documentation for more details on managing tool authentication.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
