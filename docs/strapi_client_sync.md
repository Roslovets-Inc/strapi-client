<!-- markdownlint-disable -->

<a href="../strapi_client/strapi_client_sync.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `strapi_client_sync`






---

<a href="../strapi_client/strapi_client_sync.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `StrapiClientSync`
RESP API client for Strapi. 

<a href="../strapi_client/strapi_client_sync.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(baseurl: str) → None
```

Initialize client. 




---

<a href="../strapi_client/strapi_client_sync.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `authorize`

```python
authorize(identifier: str, password: str, token: str = None) → None
```

Set up or retrieve access token. 

---

<a href="../strapi_client/strapi_client_sync.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_entry`

```python
create_entry(plural_api_id: str, data: dict) → dict
```

Create entry. 

---

<a href="../strapi_client/strapi_client_sync.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_entry`

```python
delete_entry(plural_api_id: str, document_id: int) → dict
```

Delete entry by id. 

---

<a href="../strapi_client/strapi_client_sync.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_entries`

```python
get_entries(
    plural_api_id: str,
    sort: Optional[List[str]] = None,
    filters: Optional[dict] = None,
    populate: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
    pagination: Optional[dict] = None,
    publication_state: Optional[str] = None,
    get_all: bool = False,
    batch_size: int = 100
) → dict
```

Get list of entries. Optionally can operate in batch mode to get all entities automatically. 

---

<a href="../strapi_client/strapi_client_sync.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_entry`

```python
get_entry(
    plural_api_id: str,
    document_id: int,
    populate: Optional[List[str]] = None,
    fields: Optional[List[str]] = None
) → dict
```

Get entry by id. 

---

<a href="../strapi_client/strapi_client_sync.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_entry`

```python
update_entry(plural_api_id: str, document_id: int, data: dict) → dict
```

Update entry fields. 

---

<a href="../strapi_client/strapi_client_sync.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upsert_entry`

```python
upsert_entry(plural_api_id: str, data: dict, keys: List[str]) → dict
```

Create entry or update fields. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
