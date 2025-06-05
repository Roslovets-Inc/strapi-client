# Strapi Client

[![PyPI - Version](https://img.shields.io/pypi/v/strapi-client)](https://pypi.org/project/strapi-client/)

Interact with Strapi from Python using the REST API

## Install

```bash
pip install strapi-client
```

## Documentation

[Full API Reference](https://roslovets-inc.github.io/strapi-client/reference/)

## Examples

### Quick start (sync version):

```python
from strapi_client import StrapiClient

with StrapiClient(base_url='YOUR_STRAPI_URL', token='YOUR_STRAPI_TOKEN') as client:
    # await strapi.authorize(identifier='user_identifier', password='user_password')  # Optional
    users = client.get_documents('users', filters={'username': {'$eq': 'Pavel'}})
    user_id = users.data[0]['documentId']
    client.update_document('users', user_id, data={'username': 'Mark'})
```

### Quick start (async version):

```python
import asyncio
from strapi_client import StrapiClientAsync


async def main():
    async with StrapiClientAsync(base_url='YOUR_STRAPI_URL', token='YOUR_STRAPI_TOKEN') as client:
        # await strapi.authorize(identifier='user_identifier', password='user_password')  # Optional
        users = await client.get_documents('users', filters={'username': {'$eq': 'Pavel'}})
        user_id = users.data[0]['documentId']
        await client.update_document('users', user_id, data={'username': 'Mark'})


asyncio.run(main())
```

### Quick start with SmartDocument ORM

```python
import asyncio
from strapi_client import StrapiClientAsync, SmartDocument, MediaImageDocument


class User(SmartDocument):
    username: str
    first_name: str
    photo: MediaImageDocument


class Session(SmartDocument):
    uid: str
    user: User | None


async def main():
    async with StrapiClientAsync(base_url='YOUR_STRAPI_URL', token='YOUR_STRAPI_TOKEN') as client:
        # Get with relations and media by ID
        user1 = await User.get_document(client, document_id='YOUR_DOCUMENT_ID')
        print(user1.photo)

        # List documents with automatic population
        sessions = await Session.get_documents(client, sort=['created_at'])
        for session in sessions:
            print(session.user.photo if session.user else 'No user')

        # Find one document
        user1 = await User.get_first_document(client, filters={'username': 'Mark'})
        if user1:
            print(user1)


asyncio.run(main())
```

### Quick start with ActiveDocument ORM (experimental)

Relations and upserts are supported in experimental mode.

```python
import asyncio
from strapi_client import StrapiClientAsync, ActiveDocument, DocumentField


class User(ActiveDocument):
    username: str = DocumentField(unique=True)
    first_name: str


class Session(ActiveDocument):
    uid: str = DocumentField(unique=True)
    user: User | None = DocumentField(default=None, relation=True)


async def main():
    async with StrapiClientAsync(base_url='YOUR_STRAPI_URL', token='YOUR_STRAPI_TOKEN') as client:
        # Update existing document
        user1 = await User.get_document(client, document_id='YOUR_DOCUMENT_ID')
        user1.first_name = 'Mark'
        await user1.update_document(client)

        # Create or update document with relation
        session1 = await Session(uid='123', user=user1).upsert_document(client)
        await session1.refresh(client)  # populate fields from Strapi

        # Create and delete document
        user2 = await User(username='pavel', first_name='Pavel').create_document(client)
        await user2.delete_document(client)


asyncio.run(main())
```

## Development

### Create new release

Push changes to 'main' branch following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Update documentation

`docs` folder is being updated automatically by GitHub Actions when source files are changed.
