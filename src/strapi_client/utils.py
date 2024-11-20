from typing import Any


def flatten_parameters(parameters: dict[str, Any]) -> tuple[str, Any]:
    """Flatten nested dict with parameters to flat structure for query."""
    for key, value in parameters.items():
        if isinstance(value, dict):
            for key1, value1 in flatten_parameters(value):
                yield f'[{key}]{key1}', value1
        else:
            yield f'[{key}]', value


def stringify_parameters(name: str, parameters: dict | list[str] | str | None) -> dict[str, Any]:
    """Stringify nested dict with parameters to strings for query."""
    if type(parameters) is dict:
        return {name + k: v for k, v in flatten_parameters(parameters)}
    elif type(parameters) is str:
        return {name: parameters}
    elif type(parameters) is list:
        return {f'{name}[{i}]': p for i, p in enumerate(parameters)}
    else:
        return {}


def compose_request_parameters(
        sort: list[str] | None = None,
        filters: dict[str, Any] | None = None,
        populate: list[str] | None = None,
        fields: list[str] | None = None,
        pagination: dict[str, Any] | None = None,
        publication_state: str | None = None,
) -> dict[str, Any]:
    return {
        **(stringify_parameters('sort', sort) if sort else {}),
        **(stringify_parameters('filters', filters) if filters else {}),
        **(stringify_parameters('populate', populate) if populate else {}),
        **(stringify_parameters('fields', fields) if fields else {}),
        **(stringify_parameters('pagination', pagination) if pagination else {}),
        **(stringify_parameters('publicationState', publication_state) if publication_state else {}),
    }
