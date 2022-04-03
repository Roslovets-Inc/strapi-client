<!-- markdownlint-disable -->

<a href="../strapi_client/strapi_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `strapi_client`





---

<a href="../strapi_client/strapi_client.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `process_response`

```python
process_response(response: dict) → (<class 'dict'>, <class 'dict'>)
```

Process response with entries. 


---

<a href="../strapi_client/strapi_client.py#L5"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `StrapiClient`
RESP API client for Strapi. 

<a href="../strapi_client/strapi_client.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(baseurl: str) → None
```

Initialize client. 




---

<a href="../strapi_client/strapi_client.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `authorize`

```python
authorize(identifier: str, password: str, token: str = None) → None
```

Set up or retrieve access token. 

---

<a href="../strapi_client/strapi_client.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_entries`

```python
get_entries(
    plural_api_id: str,
    sort: Optional[List[str]] = None,
    filters: Optional[dict] = None,
    populate: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
    pagination: Optional[dict] = None,
    publication_state: Optional[str] = None
) → dict
```

Get list of entries. 

---

<a href="../strapi_client/strapi_client.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_entry`

```python
update_entry(plural_api_id: str, document_id: int, data: dict) → None
```

Update entry fields. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
