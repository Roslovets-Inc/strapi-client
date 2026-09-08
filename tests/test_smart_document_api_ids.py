import asyncio
from unittest.mock import AsyncMock

import pytest

from strapi_client import LocalizedSmartDocument, SmartDocument, StrapiClientAsync
from strapi_client.models.response import DocumentsResponse


@pytest.mark.parametrize("base", [SmartDocument, LocalizedSmartDocument])
@pytest.mark.parametrize("explicit", [False, True])
def test_api_ids_are_inherited_through_multiple_levels(base, explicit):
    class Repo(base):
        if explicit:
            __singular_api_id__ = "repository"
            __plural_api_id__ = "repositories"
            __content_type_id__ = "api::repository.repository"

    class RepoWithRealm(Repo):
        realm: str

    class ExtendedRepo(RepoWithRealm):
        pass

    singular = "repository" if explicit else "repo"
    for model in (Repo, RepoWithRealm, ExtendedRepo):
        assert model.__singular_api_id__ == singular
        assert model.__plural_api_id__ == ("repositories" if explicit else "repos")
        assert model.__content_type_id__ == f"api::{singular}.{singular}"
        assert "__singular_api_id__" in model.__dict__
        assert "__plural_api_id__" in model.__dict__
        assert "__content_type_id__" in model.__dict__


def test_abstract_smart_document_does_not_receive_api_ids():
    assert "__singular_api_id__" not in LocalizedSmartDocument.__dict__
    assert "__plural_api_id__" not in LocalizedSmartDocument.__dict__
    assert "__content_type_id__" not in LocalizedSmartDocument.__dict__


@pytest.mark.parametrize("field", ["__singular_api_id__", "__plural_api_id__", "__content_type_id__"])
def test_subclass_override_takes_priority_without_changing_other_ids(field):
    class Repo(SmartDocument):
        pass

    subclass = type("CustomRepo", (Repo,), {field: "custom"})
    for attribute, original in (
        ("__singular_api_id__", "repo"),
        ("__plural_api_id__", "repos"),
        ("__content_type_id__", "api::repo.repo"),
    ):
        assert getattr(subclass, attribute) == ("custom" if attribute == field else original)
        assert getattr(Repo, attribute) == original


def test_subclass_requests_inherited_endpoint():
    class Repo(SmartDocument):
        __plural_api_id__ = "repos"

    class RepoWithRealm(Repo):
        realm: str

    client = AsyncMock(spec=StrapiClientAsync)
    client.get_documents.return_value = DocumentsResponse(data=[], meta={"pagination": {"total": 0}})
    assert asyncio.run(RepoWithRealm.get_documents(client)) == []
    assert client.get_documents.await_args.kwargs["plural_api_id"] == "repos"
