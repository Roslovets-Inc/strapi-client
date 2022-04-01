# Strapi Client

Work with Strapi from Python via REST API

## Install

```bash
pip install strapi-client
```

## Documentation

[Full API Reference](./docs)

## Examples

Quick start:

```python
import asyncio
from strapi_client import StrapiClient

async def main():
    strapi = StrapiClient(strapi_url)
    await strapi.authorize(your_identifier, your_password) # optional
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
