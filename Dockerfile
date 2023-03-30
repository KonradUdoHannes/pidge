FROM python:3.11.1-slim

RUN mkdir /app
WORKDIR /app
RUN apt update && apt install make
RUN pip install -U pip
RUN pip install poetry
RUN poetry config installer.modern-installation false
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install

COPY pidge pidge
RUN poetry install
COPY Makefile .

CMD ["make","web-ui"]
