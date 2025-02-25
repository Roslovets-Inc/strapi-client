<!-- markdownlint-disable -->

<a href="../src/strapi_client/strapi_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `strapi_client.strapi_client`






---

<a href="../src/strapi_client/strapi_client.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `StrapiClient`
REST API client for Strapi. 


---

#### <kbd>property</kbd> api_url





---

#### <kbd>property</kbd> client







---

<a href="../src/strapi_client/strapi_client.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `authorize`

```python
authorize(identifier: str, password: str) → None
```

Get auth token using identifier and password. 

---

<a href="../src/strapi_client/strapi_client.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_document`

```python
create_document(plural_api_id: str, data: dict[str, Any]) → DocumentResponse
```

Create new document. 

---

<a href="../src/strapi_client/strapi_client.py#L125"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_document`

```python
delete_document(plural_api_id: str, document_id: str) → None
```

Delete document by document id. 

---

<a href="../src/strapi_client/strapi_client.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_document`

```python
get_document(
    plural_api_id: str,
    document_id: str,
    populate: list[str] | str | None = None,
    fields: list[str] | None = None
) → DocumentResponse
```

Get document by document id. 

---

<a href="../src/strapi_client/strapi_client.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_documents`

```python
get_documents(
    plural_api_id: str,
    sort: list[str] | None = None,
    filters: dict[str, Any] | None = None,
    populate: list[str] | str | None = None,
    fields: list[str] | None = None,
    publication_state: str | None = None,
    locale: str | None = None,
    start: int | None = 0,
    page: int | None = None,
    batch_size: int = 25,
    with_count: bool = True
) → DocumentsResponse
```

Get list of documents. By default, operates in batch mode to get all documents automatically. 

---

<a href="../src/strapi_client/strapi_client.py#L216"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_uploaded_files`

```python
get_uploaded_files(filters: dict | None = None) → list[dict[str, Any]]
```

Get uploaded files. 

---

<a href="../src/strapi_client/strapi_client.py#L184"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_delete_request`

```python
send_delete_request(route: str, use_auth: bool = True) → Response
```

Send DELETE request to custom endpoint. 

---

<a href="../src/strapi_client/strapi_client.py#L131"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_get_request`

```python
send_get_request(
    route: str,
    params: dict[str, Any] | None = None,
    use_auth: bool = True
) → Response
```

Send GET request to custom endpoint. 

---

<a href="../src/strapi_client/strapi_client.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_post_request`

```python
send_post_request(
    route: str,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    files: list | None = None,
    use_auth: bool = True
) → Response
```

Send POST request to custom endpoint. 

---

<a href="../src/strapi_client/strapi_client.py#L146"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send_put_request`

```python
send_put_request(
    route: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    use_auth: bool = True
) → Response
```

Send PUT request to custom endpoint. 

---

<a href="../src/strapi_client/strapi_client.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_document`

```python
update_document(
    plural_api_id: str,
    document_id: str,
    data: dict[str, Any]
) → DocumentResponse
```

Update document fields. 

---

<a href="../src/strapi_client/strapi_client.py#L193"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upload_files`

```python
upload_files(
    files: list[Path | str],
    ref: str | None = None,
    ref_id: int | None = None,
    field: str | None = None
) → dict[str, Any]
```

Upload list of files. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
