from typing import Any, Iterator


def flatten_parameters(parameters: dict[str, Any]) -> Iterator[tuple[str, Any]]:
    """Flatten nested dict with parameters to flat structure for query."""
    for key, value in parameters.items():
        if isinstance(value, dict):
            for key1, value1 in flatten_parameters(value):
                yield f'[{key}]{key1}', value1
        else:
            yield f'[{key}]', value


def stringify_parameters(
        name: str,
        parameters: dict[str, Any] | list[str] | str | None
) -> dict[str, Any]:
    """Stringify nested dict with parameters to strings for query."""
    if type(parameters) is dict:
        return {name + k: v for k, v in flatten_parameters(parameters)}
    elif type(parameters) is str:
        return {name: parameters}
    elif type(parameters) is list:
        return {f'{name}[{i}]': p for i, p in enumerate(parameters)}
    else:
        return {}
