FROM python:3.11-slim

RUN apt-get update  \
    && apt-get upgrade -y  \
    && apt-get install --no-install-recommends -y wait-for-it

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=1.5.1

# install poetry
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false

# set work directory as /scrapydoo
WORKDIR /scrapydoo

# install dependencies
COPY poetry.lock* pyproject.toml /scrapydoo/
RUN poetry install --with=dev --no-interaction

# install scrapy dependencies
RUN playwright install --with-deps chromium \
    # cleaning up unused files \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# copy project
COPY . .

# copy start script
COPY docker/start /start
RUN chmod +x /start

CMD ["/start"]
