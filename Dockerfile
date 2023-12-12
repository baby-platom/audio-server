FROM python:3.8 as requirements-stage

WORKDIR /tmp

ENV \
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python

ENV PATH="/root/.local/bin:$PATH"

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.8

WORKDIR /app

ENV \
    APP_PATH=/app \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

RUN apt-get update && apt-get install ffmpeg libavcodec-extra -y

COPY --from=requirements-stage /tmp/requirements.txt $APP_PATH/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app/ .

CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload
