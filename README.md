# Research Agent

This project is a multi-agent research assistant built with Chainlit, Firecrawl, and OpenAI models. It automates the process of researching a topic by breaking it down into a series of steps, each handled by a specialized agent.

## Features

- **Multi-Agent System:** The research process is divided into four distinct steps, each performed by a specialized agent:
    1.  **Initial Research Agent:** Conducts an initial search for relevant sources.
    2.  **Deep Research Agent:** Scrapes and analyzes the most important sources.
    3.  **Enhancer Agent:** Simplifies complex concepts and adds examples to the content.
    4.  **Reporter Agent:** Generates a comprehensive and well-structured final report.
- **Interactive UI:** The application uses Chainlit to provide a user-friendly chat interface for interacting with the research agent.
- **Real-time Updates:** The UI provides real-time updates on the progress of the research, showing the current step and status.
- **Powered by OpenAI and Firecrawl:** The agents use OpenAI's powerful language models (via OpenRouter) for their reasoning and content generation capabilities, and Firecrawl for web scraping and searching.

## Technologies Used

- **Chainlit:** A Python framework for building conversational AI applications.
- **Firecrawl:** A tool for scraping and searching web pages.
- **OpenAI:** The language models used by the agents.
- **OpenRouter:** A service that provides access to various language models.
- **Python:** The programming language used for the project.

## How to Run the Project

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Mrkhan9914626/Research_agent.git
    cd Research_agent
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up the environment variables:**
    Create a `.env` file in the root of the project and add the following environment variables:
    ```
    OPENROUTER_API_KEY="your_openrouter_api_key"
    FIRECRAWL_API_KEY="your_firecrawl_api_key"
    ```

4.  **Run the MCP server:**
    The application requires an MCP server to be running. You can find more information about the MCP server in its documentation.

5.  **Run the Chainlit application:**
    ```bash
    chainlit run main.py -w
    ```
