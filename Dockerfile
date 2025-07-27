FROM python:3.10-slim

ENV POETRY_VERSION=2.1.3
ENV PATH="/root/.local/bin:$PATH"

# System deps
RUN apt-get update && apt-get install -y \
    curl build-essential git \
    && apt-get clean

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set workdir
WORKDIR /src

# Copy files
COPY ./app ./app
COPY ./tools ./tools
COPY pyproject.toml poetry.lock ./
COPY README.md .

# Install dependencies
RUN poetry install

RUN poetry run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Run
CMD ["poetry", "run", "python", "app/main.py"]
