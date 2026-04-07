# Florida Building Code RAG Chatbot

This project is a simple retrieval-augmented generation (RAG) chatbot built to demonstrate practical familiarity with AWS-based GenAI architecture. It allows a user to ask questions about the **2023 Florida Building Code** and receive concise answers grounded in retrieved source material, with section-level citations included in the response.

## Purpose

The main goal of this project is to show competency with:

- Building a basic RAG pipeline
- Using AWS storage and knowledge-base infrastructure
- Connecting an LLM application to retrieved reference documents
- Enforcing grounded, citation-based answers
- Deploying a lightweight chat application in AWS

This is not meant to be a production-grade legal or code-compliance system. It is a portfolio/demo project intended to show hands-on understanding of how retrieval, orchestration, and frontend interaction work together in an AI application.

## What the App Does

The chatbot answers user questions about the **2023 Florida Building Codes** by retrieving relevant content from an AWS Bedrock Knowledge Base and passing that context into an LLM workflow. The agent is instructed to answer only from retrieved building-code content, cite exact sections or subsections, stay concise, and avoid using outside knowledge. If it cannot verify an answer from retrieval, it says so rather than guessing.

The current implementation includes a retry mechanism: if the first model response does not contain a section-style citation, the app asks the agent to try again under stricter instructions. If a valid citation still is not produced, the app returns a fallback message indicating that it could not verify the answer from retrieved text.

## High-Level Architecture

1. **Source documents**  
   Free versions of the Florida code documents were converted into Markdown and JSON metadata files and uploaded to an S3 bucket.

2. **Knowledge base layer**  
   An **AWS Bedrock Knowledge Base** was configured to index and retrieve from that document set. The retriever in `agent.py` uses `AmazonKnowledgeBasesRetriever` and requests up to 8 results from the vector search configuration.

3. **LLM orchestration**  
   The application uses an OpenAI model via LlamaIndex. Retrieved context is exposed to the agent as a query tool named `amazon_knowledge_base`. The agent itself is a `ReActAgent`, which can decide when to use the retrieval tool before producing an answer.

4. **Frontend / chat interface**  
   The user interacts through a Gradio web app with a chat window, message box, send button, and clear button. The interface maintains message history and asynchronously calls the agent for each user prompt.

5. **Deployment target**  
   According to the existing README, the app was hosted on **AWS ECS**.

## Repository Files

### `agent.py`

This file contains the application’s core AI logic. It:

- Loads environment variables with `dotenv`
- Creates the Bedrock Knowledge Base retriever
- Instantiates the OpenAI LLM
- Wraps the retriever in a `QueryEngineTool`
- Defines the ReAct agent and its system prompt
- Checks whether answers include required citations
- Retries once if the first answer does not meet citation requirements
- Returns a fallback verification message if retrieval-grounded citation still fails

This file is what enforces the “retrieval first, cite exactly, do not guess” behavior.

### `app.py`

This file defines the Gradio application. It:

- Creates the chat UI
- Stores chat history in message format
- Accepts user input from a textbox
- Sends the latest user message plus prior context to `get_agent_response`
- Appends the assistant reply back into the chat history
- Launches the app on `0.0.0.0:8080`

This is the user-facing application layer.

## Answering Behavior

The chatbot is explicitly instructed to do the following for building-code questions:

- answer in English
- use the retrieval tool
- cite the exact section or subsection used
- remain concise
- answer only from retrieved code content
- avoid outside knowledge
- use only explicitly retrieved examples
- cite figures only if the retrieved material actually references them
- say the material is insufficient instead of guessing

This makes the app a good demonstration of grounded-answer design and basic output guardrails.

## Requirements

To run this project, you need:

- Python environment with the packages used in the codebase
- An OpenAI API key
- An AWS account with access to:
  - S3
  - Amazon Bedrock Knowledge Bases
  - whatever IAM permissions are needed for retrieval access
- A populated Bedrock Knowledge Base containing your processed Florida code documents

The code expects environment variables for:

- `BEDROCK_KNOWLEDGE_BASE_ID`
- `OPENAI_MODEL`

Because the app loads environment variables using `load_dotenv()`, you will typically place these in a `.env` file.

## Example `.env`

```env
BEDROCK_KNOWLEDGE_BASE_ID=your_bedrock_kb_id
OPENAI_MODEL=gpt-4.1-mini
OPENAI_API_KEY=your_openai_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=your_aws_region
```

Depending on how your AWS credentials are configured, you may use IAM roles instead of long-term access keys. For deployment, IAM roles are generally preferable.

## How to Run Locally

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install the required dependencies.
4. Create a `.env` file with the required values.
5. Make sure your Bedrock Knowledge Base is already set up and accessible.
6. Start the app:

```bash
python app.py
```

The application launches a Gradio server on port `8080`, bound to `0.0.0.0`.

## Example Workflow

1. User opens the chatbot UI.
2. User asks a building-code question.
3. The message is passed to the agent along with prior chat history.
4. The agent retrieves relevant building-code chunks from the Bedrock Knowledge Base.
5. The LLM generates a response using only the retrieved material.
6. The app checks whether the response contains a valid citation pattern such as `Section 303.2`.
7. If no citation is detected, the app retries with stricter instructions.
8. If citation still fails, the app returns a verification failure message.

## Why This Project Is Useful as a Demo

This project demonstrates several practical GenAI engineering concepts in one small application:

- document ingestion and knowledge-base preparation
- retrieval over domain-specific documents
- tool-based agent orchestration
- frontend chat integration
- output constraints and citation enforcement
- cloud-hosted AI application structure

It is especially useful as a portfolio project because it is narrow, concrete, and grounded in real reference material rather than being a generic chatbot. The use of building-code documents also gives it a clear domain and a clear reason for using RAG instead of pure model memory.

## Limitations

This project has a few intentional simplifications:

- It is limited to the code documents that were indexed.
- It depends on retrieval quality from the Bedrock Knowledge Base.
- Citation detection is pattern-based, not semantic validation.
- It is designed for concise answers, not deep legal/code interpretation.
- It is a demo app and should not be relied on as an authoritative compliance tool.

The fallback behavior helps prevent unsupported answers, but it does not replace expert review.

## Possible Future Improvements

Some good next steps for extending the project would be:

- display retrieved source chunks directly in the UI
- show document title/chapter metadata alongside answers
- support multiple code books with user-selectable scope
- add conversation memory controls or citation highlighting
- improve document preprocessing and chunking strategy
- add authentication and usage logging
- deploy with production-ready containerization and secrets handling
- add evaluation tests for retrieval quality and citation accuracy

## Acknowledgment

The existing README notes that this project was based on the structure of an external chatbot example repository and then adapted to this Florida building-code use case.