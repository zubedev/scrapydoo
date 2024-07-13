FROM python:3.12-slim as requirements

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=1.8.3

# set work directory as /scrapydoo
WORKDIR /requirements
# copy over the files needed for poetry
COPY poetry.lock* pyproject.toml ./

# install poetry, export requirements
RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry export -f requirements.txt --output requirements.txt

# create a virtual environment and install dependencies
RUN python -m venv /venv
# set python to use the virtual environment
ENV PATH="/venv/bin:$PATH"
# install dependencies to the virtual environment
RUN --mount=type=cache,target=/root/.cache \
    /venv/bin/python -m pip install -r requirements.txt

FROM python:3.12-slim

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    # gosu for easy step-down from root
    gosu \
    # wait script to check for scrapyd availability
    wait-for-it

RUN groupadd -g 999 scrapydoo  \
    && useradd -l -m -r -u 999 -g scrapydoo scrapydoo

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# copy over the virtual environment
COPY --from=requirements --chown=scrapydoo:scrapydoo /venv /venv
# set python to use the virtual environment
ENV PATH="/venv/bin:$PATH"

# set work directory as /scrapydoo
RUN mkdir -p /scrapydoo \
    && chown -R scrapydoo:scrapydoo /scrapydoo \
    && mkdir -p /var/lib/scrapyd \
    && chown -R scrapydoo:scrapydoo /var/lib/scrapyd
WORKDIR /scrapydoo

# install scrapy dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/root/.cache \
    playwright install --with-deps chromium \
    && mkdir -p /home/scrapydoo/.cache \
    && cp -R /root/.cache/ms-playwright /home/scrapydoo/.cache/ \
    && chown -R scrapydoo:scrapydoo /home/scrapydoo/.cache \
    # cleaning up unused files \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# copy the entrpoint and start script
COPY --chown=scrapydoo:scrapydoo docker/prod/entrypoint /entrypoint
COPY --chown=scrapydoo:scrapydoo docker/prod/start /start
RUN sed -i "s/\r$//g" /entrypoint \
    && chmod +x /entrypoint \
    && sed -i "s/\r$//g" /start \
    && chmod +x /start

# copy project and remove unnecessary files
COPY --chown=scrapydoo:scrapydoo . .
RUN rm -rf \
    .dockerignore \
    docker \
    poetry.lock \
    pyproject.toml

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
