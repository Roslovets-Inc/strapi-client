<!-- markdownlint-disable -->

<a href="../src/strapi_client/base_document.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `strapi_client.base_document`





---

<a href="../src/strapi_client/base_document.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `DocumentField`

```python
DocumentField(*args, unique: bool = False, relation: bool = False, **kwargs)
```






---

<a href="../src/strapi_client/base_document.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BaseDocument`
Experimental ORM class for Strapi document. 


---

#### <kbd>property</kbd> model_extra

Get extra fields set during validation. 



**Returns:**
  A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`. 

---

#### <kbd>property</kbd> model_fields_set

Returns the set of fields that have been explicitly set on this model instance. 



**Returns:**
  A set of strings representing the fields that have been set,  i.e. that were not filled from defaults. 



---

<a href="../src/strapi_client/base_document.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_document`

```python
create_document(client: StrapiClientAsync) → Self
```





---

<a href="../src/strapi_client/base_document.py#L108"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_document`

```python
delete_document(client: StrapiClientAsync) → None
```





---

<a href="../src/strapi_client/base_document.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_document`

```python
get_document(
    client: StrapiClientAsync,
    document_id: str,
    populate_all: bool = True
) → Self
```





---

<a href="../src/strapi_client/base_document.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_documents`

```python
get_documents(
    client: StrapiClientAsync,
    populate_all: bool = True,
    sort: list[str] | None = None,
    filters: dict[str, Any] | None = None,
    publication_state: str | None = None,
    locale: str | None = None,
    start: int | None = 0,
    page: int | None = None,
    limit: int = 25,
    with_count: bool = True
) → list[Self]
```





---

<a href="../src/strapi_client/base_document.py#L162"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `model_dump_variable`

```python
model_dump_variable(exclude: set[str] | None = None) → dict[str, Any]
```





---

<a href="../src/strapi_client/base_document.py#L170"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `model_hash`

```python
model_hash() → str
```





---

<a href="../src/strapi_client/base_document.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `refresh`

```python
refresh(client: StrapiClientAsync, populate_all: bool = True) → Self
```





---

<a href="../src/strapi_client/base_document.py#L116"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `relations_populated`

```python
relations_populated() → bool
```





---

<a href="../src/strapi_client/base_document.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_relations_populated`

```python
set_relations_populated(value: bool) → Self
```





---

<a href="../src/strapi_client/base_document.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_document`

```python
update_document(client: StrapiClientAsync) → Self
```





---

<a href="../src/strapi_client/base_document.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upsert_document`

```python
upsert_document(client: StrapiClientAsync) → Self
```

Create document or update fields. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
