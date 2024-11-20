# Strapi Client

Work with Strapi from Python via REST API

## Install

```bash
pip install strapi-client
```

## Documentation

[Full API Reference](./docs)

## Examples

### Quick start (sync version):

```python
from src import StrapiClientSync

strapi = StrapiClientSync(YOUR_STRAPI_URL)
strapi.authorize(token=YOUR_STRAPI_TOKEN)
users = strapi.get_entries('users', filters={'username': {'$eq': 'Pavel'}})
user_id = users['data'][0]['id']
strapi.update_entry('users', user_id, data={'username': 'Mark'})
```

Quick start (async version):

```python
import asyncio
from src import StrapiClient


async def main():
    strapi = StrapiClient(YOUR_STRAPI_URL)
    await strapi.authorize(token=YOUR_STRAPI_TOKEN)
    users = await strapi.get_entries('users', filters={'username': {'$eq': 'Pavel'}})
    user_id = users['data'][0]['id']
    await strapi.update_entry('users', user_id, data={'username': 'Mark'})


asyncio.run(main())
```

## Development

### Create new release

Push changes to 'main' branch following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Update documentation

`docs` folder is being updated automatically by GitHub Actions when source files are changed.
