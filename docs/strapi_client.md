<!-- markdownlint-disable -->

<a href="../strapi_client/strapi_client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `strapi_client`






---

<a href="../strapi_client/strapi_client.py#L4"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `StrapiClient`
RESP API client for Strapi. 

<a href="../strapi_client/strapi_client.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(baseurl: str)
```








---

<a href="../strapi_client/strapi_client.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `authorize`

```python
authorize(identifier: str, password: str, token: str = None)
```

Set up or retrieve access token. 

---

<a href="../strapi_client/strapi_client.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_entries`

```python
get_entries(plural_api_id: str, filters: dict = None) → dict
```

Get list of entries. 

---

<a href="../strapi_client/strapi_client.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_entry`

```python
update_entry(plural_api_id: str, document_id: int, data: dict)
```

Update entry fields. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
