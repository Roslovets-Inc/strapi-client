<!-- markdownlint-disable -->

<a href="../strapi_client/strapi_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `strapi_client`





---

<a href="../strapi_client/strapi_client.py#L290"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `process_data`

```python
process_data(entry: dict) → Union[dict, List[dict]]
```

Process response with entries. 


---

<a href="../strapi_client/strapi_client.py#L301"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `process_response`

```python
process_response(response: dict) → Tuple[List[dict], dict]
```

Process response with entries. 


---

<a href="../strapi_client/strapi_client.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `StrapiClient`
REST API client for Strapi. 

<a href="../strapi_client/strapi_client.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(baseurl: str) → None
```

Initialize client. 




---

<a href="../strapi_client/strapi_client.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `authorize`

```python
authorize(
    identifier: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None
) → None
```

Set up or retrieve access token. 

---

<a href="../strapi_client/strapi_client.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_entry`

```python
create_entry(plural_api_id: str, data: dict) → dict
```

Create entry. 

---

<a href="../strapi_client/strapi_client.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_entry`

```python
delete_entry(plural_api_id: str, document_id: int) → dict
```

Delete entry by id. 

---

<a href="../strapi_client/strapi_client.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

Get list of entries. Optionally can operate in batch mode to get all entries automatically. 

---

<a href="../strapi_client/strapi_client.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="../strapi_client/strapi_client.py#L253"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_uploaded_files`

```python
get_uploaded_files(filters: Optional[dict] = None) → list[dict]
```

Get uploaded files. 

---

<a href="../strapi_client/strapi_client.py#L216"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_get_request`

```python
send_get_request(route: str) → dict
```

Send GET request to custom endpoint. 

---

<a href="../strapi_client/strapi_client.py#L202"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_post_request`

```python
send_post_request(route: str, body: Optional[dict] = None) → dict
```

Send POST request to custom endpoint. 

---

<a href="../strapi_client/strapi_client.py#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_entry`

```python
update_entry(plural_api_id: str, document_id: int, data: dict) → dict
```

Update entry fields. 

---

<a href="../strapi_client/strapi_client.py#L229"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upload_files`

```python
upload_files(
    files: list,
    ref: Optional[str] = None,
    ref_id: Optional[int] = None,
    field: Optional[str] = None
) → dict
```

Upload files. 

---

<a href="../strapi_client/strapi_client.py#L165"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upsert_entry`

```python
upsert_entry(
    plural_api_id: str,
    data: dict,
    keys: List[str],
    unique: bool = True
) → dict
```

Create entry or update fields. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
