```text
███████╗ ██████╗██████╗  █████╗ ██████╗ ██╗   ██╗██████╗  ██████╗  ██████╗
██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔═══██╗
███████╗██║     ██████╔╝███████║██████╔╝ ╚████╔╝ ██║  ██║██║   ██║██║   ██║
╚════██║██║     ██╔══██╗██╔══██║██╔═══╝   ╚██╔╝  ██║  ██║██║   ██║██║   ██║
███████║╚██████╗██║  ██║██║  ██║██║        ██║   ██████╔╝╚██████╔╝╚██████╔╝
╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚═════╝  ╚═════╝  ╚═════╝
>--------------------------------- Scrapy dappy doo crawler for proxy sites
```
[![scrapy](https://img.shields.io/badge/scrapy-2.11-%235fa839?style=flat-square)](https://scrapy.org)
[![python](https://img.shields.io/badge/python-3.11-%233776AB?style=flat-square&logo=python)](https://www.python.org)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org)
[![black](https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square&logo=stylelint)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit)](https://pre-commit.com)
[![license](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/zubedev/scrapydoo/actions/workflows/ci.yml/badge.svg)](https://github.com/zubedev/scrapydoo/actions/workflows/ci.yml)

## Features

- [x] Crawls proxy sites for working proxies
- [x] Scrapyd server to initiate crawl and get results
- [x] Retain jobs and logs for recent crawls

## Usage

```bash
# Copy the example environment file to .env
cp .env.example .env

# Build the docker image and run the container
docker-compose up --build --detach

# Run a scrapy crawl job via cli
# docker-compose exec -it scrapyd scrapy crawl <spider_name>
docker-compose exec -it scrapyd scrapy crawl freeproxylist

# Run a scrapy crawl job via scrapyd api
# Scrapyd documentation: https://scrapyd.readthedocs.io/en/latest/api.html#schedule-json
curl http://localhost:6800/schedule.json -d project=scrapydoo -d spider=freeproxylist
```
Scrapyd API is now available at http://localhost:6800.

## Pages

- [root](http://localhost:6800): `/` - Scrapyd server
- [jobs](http://localhost:6800/jobs): `/jobs` - crawl jobs
- [items](http://localhost:6800/items): `/items` - scraped items
- [logs](http://localhost:6800/logs): `/logs` - spider logs

## Endpoints
provided by [scrapyd](https://scrapyd.readthedocs.io/en/latest/api.html) server

- [daemonstatus](http://localhost:6800/daemonstatus.json): `/daemonstatus.json` - to check the load status of a service
- [addversion](http://localhost:6800/addversion.json): `/addversion.json` - to add a new version of a project
- [schedule](http://localhost:6800/schedule.json): `/schedule.json` - to schedule a spider run
- [cancel](http://localhost:6800/cancel.json): `/cancel.json` - to cancel a spider run
- [listprojects](http://localhost:6800/listprojects.json): `/listprojects.json` - to list all projects
- [listversions](http://localhost:6800/listversions.json): `/listversions.json` - to list all versions of a project
- [listspiders](http://localhost:6800/listspiders.json): `/listspiders.json` - to list all spiders of a project
- [listjobs](http://localhost:6800/listjobs.json): `/listjobs.json` - to list all pending, running and finished jobs
- [delversion](http://localhost:6800/delversion.json): `/delversion.json` - to delete a version of a project
- [delproject](http://localhost:6800/delproject.json): `/delproject.json` - to delete a project

## Development

```bash
# Poetry is required for installing and managing dependencies
# https://python-poetry.org/docs/#installation
poetry install

# Run the crawlers
#poetry run scrapy crawl <spider_name>
poetry run scrapy crawl freeproxylist

# Install pre-commit hooks
poetry run pre-commit install

# Formatting (inplace formats code)
poetry run black .

# Linting (and to fix automatically)
poetry run ruff .
poetry run ruff --fix .

# Type checking
poetry run mypy .
```

Configuration details can be found in [pyproject.toml](pyproject.toml).

## Support
[![Paypal](https://img.shields.io/badge/Paypal-@MdZubairBeg-253B80?&logo=paypal)](https://paypal.me/MdZubairBeg/10)
