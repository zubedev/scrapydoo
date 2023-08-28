FROM python:3.11-slim

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update -y  \
    && apt-get upgrade -y  \
    && apt-get install --no-install-recommends -y wait-for-it

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=1.5.1

# install poetry
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.create false

# set work directory as /scrapydoo
WORKDIR /scrapydoo

# install dependencies
COPY poetry.lock* pyproject.toml /scrapydoo/
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --with=dev --no-interaction

# install scrapy dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    playwright install --with-deps chromium \
    # cleaning up unused files \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# copy project
COPY . .

# copy start script
COPY docker/dev/start /start
RUN sed -i "s/\r$//g" /start \
    && chmod +x /start

CMD ["/start"]
