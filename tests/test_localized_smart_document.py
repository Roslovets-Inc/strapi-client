import asyncio
import datetime
from unittest.mock import AsyncMock

import pytest

from strapi_client import LocalizedSmartDocument, SmartDocument, StrapiClientAsync
from strapi_client.models.response import DocumentResponse, DocumentsResponse
from strapi_client.utils import serialize_document_data

NOW = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)


class Article(LocalizedSmartDocument):
    title: str


class Category(SmartDocument):
    title: str


def article_data(title: str = "Bonjour", locale: str = "fr") -> dict:
    return {
        "id": 1,
        "documentId": "article-1",
        "createdAt": NOW,
        "updatedAt": NOW,
        "publishedAt": NOW,
        "locale": locale,
        "title": title,
    }


def article() -> Article:
    return Article.model_validate(article_data())


def test_locale_field_is_the_localization_marker_and_is_managed():
    document = article()

    assert "locale" in Article.model_fields
    assert "locale" not in Category.model_fields
    assert Article.__plural_api_id__ == "articles"
    assert document.locale == "fr"
    assert "locale" not in document.model_dump_data(exclude_managed_fields=True)


def test_reserved_locale_is_not_serialized_into_request_data():
    with pytest.warns(UserWarning, match="Field 'locale' is reserved"):
        data = serialize_document_data({"title": "Bonjour", "locale": "fr"})

    assert data == {"title": "Bonjour"}


def test_non_localized_smart_document_can_forward_locale_without_storing_it():
    async def main():
        client = AsyncMock(spec=StrapiClientAsync)
        client.get_document.return_value = DocumentResponse(
            data={
                "id": 1,
                "documentId": "category-1",
                "createdAt": NOW,
                "updatedAt": NOW,
                "publishedAt": NOW,
                "locale": "fr",
                "title": "Category",
            }
        )

        document = await Category.get_document(client, "category-1", locale="fr")

        assert not hasattr(document, "locale")
        assert client.get_document.call_args.kwargs["locale"] == "fr"

    asyncio.run(main())


def test_localized_reads_forward_locale_and_parse_it():
    async def main():
        client = AsyncMock(spec=StrapiClientAsync)
        client.get_document.return_value = DocumentResponse(data=article_data())
        client.get_documents.return_value = DocumentsResponse(
            data=[article_data()],
            meta={"pagination": {"total": 1}},
        )

        document = await Article.get_document(client, "article-1", locale="fr")
        documents = await Article.get_documents(client, locale="fr")

        assert document.locale == "fr"
        assert documents[0].locale == "fr"
        get_document_call = client.get_document.call_args.kwargs
        assert get_document_call["locale"] == "fr"
        assert "locale" in get_document_call["fields"]
        assert client.get_documents.call_args.kwargs["locale"] == "fr"

    asyncio.run(main())


def test_localized_create_forwards_requested_locale():
    async def main():
        client = AsyncMock(spec=StrapiClientAsync)
        client.create_document.return_value = DocumentResponse(data=article_data())

        document = await Article.create_document(client, {"title": "Bonjour"}, locale="fr")

        assert document.locale == "fr"
        client.create_document.assert_awaited_once_with(
            plural_api_id="articles",
            data={"title": "Bonjour"},
            locale="fr",
        )

    asyncio.run(main())


def test_localized_instance_crud_keeps_document_locale():
    async def main():
        client = AsyncMock(spec=StrapiClientAsync)
        client.update_document.return_value = DocumentResponse(data=article_data(title="Salut"))
        client.get_document.return_value = DocumentResponse(data=article_data(title="Actualisé"))
        document = article()

        await document.update_document(client, {"title": "Salut"})
        client.update_document.assert_awaited_once_with(
            plural_api_id="articles",
            document_id="article-1",
            data={"title": "Salut"},
            locale="fr",
        )

        await document.refresh_document(client)
        assert document.title == "Actualisé"
        assert client.get_document.call_args.kwargs["locale"] == "fr"

        await document.delete_document(client)
        client.delete_document.assert_awaited_once_with(
            plural_api_id="articles",
            document_id="article-1",
            locale="fr",
        )

    asyncio.run(main())
