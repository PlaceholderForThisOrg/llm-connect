# My Companion Backend Service

This is the backend service for **My Companion**.

## 🚀 Getting Started

Follow these steps to run the service locally:

### 1. Create environment file

Create a `.env.development` file in the root directory.

### 2. Configure environment variables

Copy the required variables from `.env.example` and provide the appropriate values in `.env.development`.

### 3. Run the service

Start the backend using the following command:

```bash
uv run python -m llm_connect.main



docker compose up postgres mongodb -d
docker compose run --rm flyway
uv run python -m llm_connect.main


