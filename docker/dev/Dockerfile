FROM python:3.11-slim

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update -y  \
    && apt-get upgrade -y  \
    && apt-get install --no-install-recommends -y wait-for-it

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=1.8.2

# install poetry
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.create false

# set work directory as /scrapydoo
WORKDIR /scrapydoo

# install dependencies
COPY poetry.lock* pyproject.toml /scrapydoo/
RUN --mount=type=cache,target=/root/.cache \
    poetry install --with=dev --no-interaction

# install scrapy dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    playwright install --with-deps chromium \
    && cp -R /root/.cache /tmp/ \
    # cleaning up unused files \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# move back the playwright cache after unmount
RUN mv /tmp/.cache /root/

# copy project
COPY . .

# copy start script
COPY docker/dev/start /start
RUN sed -i "s/\r$//g" /start \
    && chmod +x /start

CMD ["/start"]
