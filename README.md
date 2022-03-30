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
from strapi_client import StrapiClient

strapi = StrapiClient(strapi_url)
strapi.authorize(your_identifier, your_password) # optional
users = strapi.get_entries('users', filters={'username': {'$eq': 'Pavel'}})
user_id = users['data'][0]['id']
strapi.update_entry('users', user_id, data={'username': 'Mark'})
```

## Development

### Create new release

Push changes to 'main' branch following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Update documentation

`docs` folder is being updated automatically by GitHub Actions when source files are changed.
