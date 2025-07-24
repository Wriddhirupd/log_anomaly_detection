#FROM python:3.13-slim
#FROM alpine:3.20
FROM python:3.13-alpine
RUN echo $(ls -al)

WORKDIR /src

COPY ./app ./app
COPY ./pyproject.toml ./poetry.lock ./
COPY ./README.md ./README.md

RUN echo $(ls -al)

RUN pip install poetry==2.1.3

RUN poetry install

RUN cd app/

RUN echo $(ls -al)

#CMD ["poetry", "run", "python", "main.py"]