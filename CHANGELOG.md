# CHANGELOG


## v5.0.4 (2025-10-24)

### Bug Fixes

- **media**: Optional width, height
  ([`94b19c0`](https://github.com/Roslovets-Inc/strapi-client/commit/94b19c00d4a59bb3cb0052181dbb52d18e409504))


## v5.0.3 (2025-10-24)

### Bug Fixes

- **media**: Formats field is optional
  ([`52420c5`](https://github.com/Roslovets-Inc/strapi-client/commit/52420c553d7df94f3dd9aa05f3114f01f3ed175e))


## v5.0.2 (2025-08-19)

### Bug Fixes

- **SmartDocument**: Inherit definitive fields
  ([`070d9bc`](https://github.com/Roslovets-Inc/strapi-client/commit/070d9bce59c6fddbbea5743d368bc256da638b7a))

by fixing ClassVar propagation

### Continuous Integration

- Trigger on tests
  ([`eeac3d6`](https://github.com/Roslovets-Inc/strapi-client/commit/eeac3d6a2543ea4585794dfb7c78d7c2accc5f86))


## v5.0.1 (2025-08-19)

### Bug Fixes

- **SmartDocument**: Remove warning for lazy mode
  ([`8555f34`](https://github.com/Roslovets-Inc/strapi-client/commit/8555f34d9d514bc8ad9d05b306eeb6e3c9a675b0))

Eliminated the warning that indicated lazy mode with populated fields is not supported. This
  simplifies the logic and avoids unnecessary warnings when using lazy mode.


## v5.0.0 (2025-08-13)

### Bug Fixes

- Export ResponseMeta model
  ([`e48a106`](https://github.com/Roslovets-Inc/strapi-client/commit/e48a10614059b60e3b1337ff236cc26468dd21b5))

Added ResponseMeta to the list of exports in __init__.py to make it available for import from the
  package.

- **client**: Upload_files returns list of MediaImageDocument
  ([`efb5286`](https://github.com/Roslovets-Inc/strapi-client/commit/efb5286e9430d8a585eb5a84e2832641a3485def))

Renamed the file and imports from media_image_documents.py to media_image_document.py for
  consistency. Updated all references and changed the return type of file upload methods to return a
  list of MediaImageDocument instances instead of raw dicts.

### Features

- Update SmartDocument update and file upload logic
  ([`3dec1b7`](https://github.com/Roslovets-Inc/strapi-client/commit/3dec1b756ab64e7a2545403fbad05e75cc973195))

Refactored SmartDocument to split update_document and lazy_update_document, improving clarity and
  testability. Enhanced file upload methods to support more binary types and added single-file
  upload helpers to both sync and async clients. Moved is_populatable_model and related utilities to
  smart_document_utils, and updated tests to match the new method names and behaviors.


## v4.2.1 (2025-08-06)

### Bug Fixes

- **SmartDocument**: `patch_document` is lazy by default
  ([`6aae4d8`](https://github.com/Roslovets-Inc/strapi-client/commit/6aae4d8c16cf47d59365e0fa924ae5986891e073))

Replaces the 'lazy' parameter with 'force' in SmartDocument.patch_document for clarity. Adds an
  option to exclude specific fields from comparison during updates. Updates all relevant tests to
  use the new 'force' parameter.


## v4.2.0 (2025-08-06)

### Bug Fixes

- **SmartDocument**: Optimize `update_document` method
  ([`7c66125`](https://github.com/Roslovets-Inc/strapi-client/commit/7c66125c3be60ff63404516c8580bb28a742d3e5))

### Features

- **SmartDocument**: `model_dump_data` method
  ([`2575f51`](https://github.com/Roslovets-Inc/strapi-client/commit/2575f51e624d749bc26d7e0e10482ccff78a2cc5))

to get plain data patch as a dictionary

- **SmartDocument**: `patch_document` method
  ([`965419a`](https://github.com/Roslovets-Inc/strapi-client/commit/965419aa3db182e56826811a677b0a9b54955ebc))

for quick one-way data udpating

- **util**: `hash_model` method
  ([`fda56a4`](https://github.com/Roslovets-Inc/strapi-client/commit/fda56a4532ab088f0e5175e6f5439ab3637695db))


## v4.1.6 (2025-07-27)

### Bug Fixes

- Export BaseComponent in package init
  ([`8bdc253`](https://github.com/Roslovets-Inc/strapi-client/commit/8bdc2534b539221fed5cd61a78060e1bd44e767d))

Added BaseComponent to the imports and __all__ list in src/strapi_client/__init__.py to make it
  available for external use.


## v4.1.5 (2025-07-26)

### Bug Fixes

- **SmartDocument**: Default pagination and sorting
  ([`317d08f`](https://github.com/Roslovets-Inc/strapi-client/commit/317d08fba40094acd65007f493ad82819b5d5fe1))

Increased the default 'limit' from 25 to 100 and set the default 'sort' to ['id'] in SmartDocument
  methods. Also changed the default 'start' parameter to None for consistency. These changes improve
  API usability and provide more predictable defaults.


## v4.1.4 (2025-07-25)

### Bug Fixes

- **SmartDocument **: Use correct response parsing on creation
  ([`0f937b3`](https://github.com/Roslovets-Inc/strapi-client/commit/0f937b38ff4dc5737ccd5ed2104e9f327cefcc84))

Changed SmartDocument.create to use BaseDocument.from_scalar_response for initial parsing, then
  return the correct class instance. This ensures the returned object is of the expected type when
  populate is False.


## v4.1.3 (2025-07-24)

### Bug Fixes

- **SmartDocument**: Add missing delete_document method
  ([`f38e470`](https://github.com/Roslovets-Inc/strapi-client/commit/f38e47015595d33a2ab960476af961ee337c2370))

Introduces an async delete_document method to the SmartDocument class, allowing documents to be
  deleted via the provided StrapiClientAsync instance.


## v4.1.2 (2025-07-24)


## v4.1.1 (2025-07-23)

### Bug Fixes

- Set default 'start' parameter to None in client methods
  ([`0732270`](https://github.com/Roslovets-Inc/strapi-client/commit/0732270d1926a0708a424854ecc1eaa5ef264f1e))

Changed the default value of the 'start' parameter from 0 to None in SmartDocument, StrapiClient,
  and StrapiClientAsync. This allows for clearer handling of pagination when 'start' is not
  explicitly provided.

- **SmartDocument**: Serialize data in json mode
  ([`48cb21c`](https://github.com/Roslovets-Inc/strapi-client/commit/48cb21c93975437067ce665f65eff4e8af007bc6))

to fix create/update


## v4.1.0 (2025-07-18)

### Features

- Prepare API parameters with qs-codec
  ([`97170c3`](https://github.com/Roslovets-Inc/strapi-client/commit/97170c3277913311b8b9eaed9fb9e4d048311ab9))

Replaced custom parameter stringification logic with qs-codec for Strapi API requests. Updated
  dependencies and type hints to support URL-encoded query strings, and removed unused utility
  functions.


## v4.0.0 (2025-07-17)

### Continuous Integration

- Run tests
  ([`10c5aaa`](https://github.com/Roslovets-Inc/strapi-client/commit/10c5aaa25072ad9661aff13e5f8eab474b55e56f))

### Features

- Refactor models and file upload, add new API utilities
  ([`aafa701`](https://github.com/Roslovets-Inc/strapi-client/commit/aafa7014c1f69ae9bb612f4c8e98dc3902f3122f))

Moved API parameter, response, auth, and file payload models into dedicated modules under models/.
  Refactored file upload logic in StrapiClient and StrapiClientAsync to use the new FilePayload
  class and support both file paths and in-memory files. Enhanced SmartDocument with update,
  relation, and file upload methods. Removed deprecated model_dump_to_create logic and its tests.
  Cleaned up types.py, moving most model definitions to their own files.

- Refactor models structure and improve document serialization
  ([`b4e1263`](https://github.com/Roslovets-Inc/strapi-client/commit/b4e12634860e06288566d31d67a612f63411ab63))

Moved document and model classes into a new 'models' subpackage, splitting out base, media, and
  utility logic. Removed 'model_utils.py' and replaced its logic with
  'models/smart_document_utils.py'. Updated imports throughout the package to use the new structure.
  Enhanced document serialization and population logic, and added tests for model serialization.
  Updated dev dependencies and added pytest for testing.

### Testing

- Add Strapi client mock tests
  ([`a6095a3`](https://github.com/Roslovets-Inc/strapi-client/commit/a6095a3b81bcfc878d2eca73e9700378b8a91479))


## v3.10.1 (2025-07-12)

### Bug Fixes

- Remove debug logging
  ([`8978a27`](https://github.com/Roslovets-Inc/strapi-client/commit/8978a27c372bc4aa59a73f8e6da36a4f196013a5))


## v3.10.0 (2025-07-12)

### Bug Fixes

- Optional fields population
  ([`2ff7fbb`](https://github.com/Roslovets-Inc/strapi-client/commit/2ff7fbb578d3e15c120c881ab091d148c2aebcc6))

### Features

- **SmartDocument**: Add `get_documents_with_meta` method
  ([`5c7722c`](https://github.com/Roslovets-Inc/strapi-client/commit/5c7722c5a46141497a0c5fc0eda5316a76286603))

to work with pagination


## v3.9.0 (2025-07-11)

### Features

- Add WebhookPayload model
  ([`4039a72`](https://github.com/Roslovets-Inc/strapi-client/commit/4039a72d03772515bf5a578540062edfec4f43eb))

Introduces the WebhookPayload model and WebhookEventName literal to support webhook event handling:
  https://docs.strapi.io/cms/backend-customization/webhooks


## v3.8.0 (2025-07-05)


## v3.7.4 (2025-07-05)

### Bug Fixes

- Populate components with `BaseComponent`
  ([`0de8648`](https://github.com/Roslovets-Inc/strapi-client/commit/0de86482fb53f2a485c371ee73c2d675d8e880c7))

and 'BasePopulatable` as a root class

- Replace async methods in sync client
  ([`a15c30f`](https://github.com/Roslovets-Inc/strapi-client/commit/a15c30fd518a895025b4f619f2ae3bdea0cd05fb))

### Features

- Add health check methods to Strapi clients
  ([`3aa0e28`](https://github.com/Roslovets-Inc/strapi-client/commit/3aa0e28a95252be2175603343897038fe85fb63a))

Introduced check_health methods to both StrapiClient and StrapiClientAsync classes to verify Strapi
  API availability. These methods perform a GET request to the '_health' endpoint and return a
  boolean indicating the API's status.


## v3.7.3 (2025-06-13)

### Bug Fixes

- Singlesmartdocument bugs
  ([`ecc4c41`](https://github.com/Roslovets-Inc/strapi-client/commit/ecc4c41f6f0f032a9c7c817e7451eaf427668c65))


## v3.7.2 (2025-06-13)

### Bug Fixes

- Add missing SingleSmartDocument
  ([`5546c95`](https://github.com/Roslovets-Inc/strapi-client/commit/5546c9530e9af462b8da74ede8bb936b667f7468))


## v3.7.1 (2025-06-05)


## v3.7.0 (2025-06-05)

### Bug Fixes

- Send `locale` parameter to endpoint
  ([`363a4a1`](https://github.com/Roslovets-Inc/strapi-client/commit/363a4a11f6dd974089fc88ee3e03951ce7002872))

- **media**: Add `largest_format` property
  ([`0ff994c`](https://github.com/Roslovets-Inc/strapi-client/commit/0ff994cae1f7ab4b527772bfbae75ddc73c2836a))

- **smart_document**: Remove print
  ([`f0d6d2f`](https://github.com/Roslovets-Inc/strapi-client/commit/f0d6d2f829b6781a1e19e3255321ed5a4d16df65))

### Chores

- Bump dev deps
  ([`d38e5cf`](https://github.com/Roslovets-Inc/strapi-client/commit/d38e5cfb487798552061326cd45968bec4be9813))

- Ignore test scripts
  ([`19b8da5`](https://github.com/Roslovets-Inc/strapi-client/commit/19b8da56dcba56637068a380d7b0c9432ecc46fe))

### Documentation

- Smartdocument example
  ([`7610c79`](https://github.com/Roslovets-Inc/strapi-client/commit/7610c79d85b1760ca81d3528c045857e6d7f31a2))

### Features

- `basedocumentwithlocale` model
  ([`a8d223b`](https://github.com/Roslovets-Inc/strapi-client/commit/a8d223b2d17ca36fbf96085641420bf4b52913d2))

and remove `locale` from `BaseDocument`

- `populate` parameter can be dictionary
  ([`07de12d`](https://github.com/Roslovets-Inc/strapi-client/commit/07de12d0fd8a0701f5a9e10a7e28a319815951f3))

- `smartdocument` model
  ([`3b7b02d`](https://github.com/Roslovets-Inc/strapi-client/commit/3b7b02d6c119ac253000570e7f0cc3a4102edd45))

to read and parse nested documents in automated way


## v3.6.0 (2025-05-22)

### Features

- First_from_list_response method of BaseDocument
  ([`daf5447`](https://github.com/Roslovets-Inc/strapi-client/commit/daf5447e03889620dc265562ba0e7e5e495418ec))

to easily get first record after search


## v3.5.1 (2025-05-22)

### Bug Fixes

- Mediaimageformats always has largest variant
  ([`41f916c`](https://github.com/Roslovets-Inc/strapi-client/commit/41f916cd3aeff4f70401dab60d98815917923d23))

### Chores

- Bump dev deps
  ([`94bf006`](https://github.com/Roslovets-Inc/strapi-client/commit/94bf006a2b0c8f24e10b04c2c5556fca5b7133a3))

### Continuous Integration

- Add check code step
  ([`d32f3a3`](https://github.com/Roslovets-Inc/strapi-client/commit/d32f3a347b84d4cbf8b1c7d195fc65b0780fcbb1))

- Fix mypy step
  ([`b7c1c09`](https://github.com/Roslovets-Inc/strapi-client/commit/b7c1c09df80e9ac2db933d8215e188286f36f5cc))


## v3.5.0 (2025-05-21)

### Features

- Mediaimagedocument type for responsive images
  ([`5c31a4a`](https://github.com/Roslovets-Inc/strapi-client/commit/5c31a4af80df5c04997841831585d50fba9113a1))


## v3.4.0 (2025-03-18)

### Features

- Work with single type documents.
  ([`5dec0a7`](https://github.com/Roslovets-Inc/strapi-client/commit/5dec0a75e432c0f36810c2e1ef6104a9c18197b9))

get_single_document(), create_or_update_single_document(), delete_single_document()


## v3.3.0 (2025-03-05)

### Features

- Create BaseDocument from API response.
  ([`f5c8ce8`](https://github.com/Roslovets-Inc/strapi-client/commit/f5c8ce86b0e381d3695d11b523afdea2a20d0b51))

`from_scalar_response` and `from_list_response` class methods


## v3.2.1 (2025-02-25)

### Bug Fixes

- Provide Timeout to init
  ([`78629a4`](https://github.com/Roslovets-Inc/strapi-client/commit/78629a49fdc8e60666fdb8b220fedd1a82d5fbf5))

### Documentation

- Pypi link
  ([`d129235`](https://github.com/Roslovets-Inc/strapi-client/commit/d129235bf629f2a35267b41b9bb831e2b36e2455))


## v3.2.0 (2025-02-25)

### Documentation

- Update and links
  ([`b593fc8`](https://github.com/Roslovets-Inc/strapi-client/commit/b593fc85026731361f4c799581bef9866edf7e57))

### Features

- Optional Timeout settings
  ([`55080ef`](https://github.com/Roslovets-Inc/strapi-client/commit/55080ef2a9a79cf1d50512d0ce40ac4bc4f2aec9))

- Rename ORM class to ActiveDocument.
  ([`6c5e283`](https://github.com/Roslovets-Inc/strapi-client/commit/6c5e2835151cd04656e313606836464c1eb2173e))

BaseDocument is static pydantic class


## v3.1.0 (2025-02-25)

### Continuous Integration

- Fix docs
  ([`4804a3b`](https://github.com/Roslovets-Inc/strapi-client/commit/4804a3bf2ea865ed88b6ddefe81b15bfd712e89d))

### Documentation

- Customize
  ([`550bd18`](https://github.com/Roslovets-Inc/strapi-client/commit/550bd18a91d6493cf0912a427309f2a8de33dc0f))

### Features

- Derive docs to GH Pages
  ([`4fdd5d1`](https://github.com/Roslovets-Inc/strapi-client/commit/4fdd5d1da882cb87186991e165059e9359502453))


## v3.0.4 (2025-02-25)

### Bug Fixes

- Add py.typed for mypy
  ([`e8ff25c`](https://github.com/Roslovets-Inc/strapi-client/commit/e8ff25c087c36e665e696db065341245fd237a80))


## v3.0.3 (2025-02-25)

### Bug Fixes

- Orm description
  ([`3ccc874`](https://github.com/Roslovets-Inc/strapi-client/commit/3ccc874de7b8c1c7a8194e17a6574573bdd5dce5))


## v3.0.2 (2025-02-25)

### Bug Fixes

- Project description
  ([`14a450c`](https://github.com/Roslovets-Inc/strapi-client/commit/14a450c69daad14f987054543849ea90a0219833))

### Continuous Integration

- Fix permissions
  ([`ce3831a`](https://github.com/Roslovets-Inc/strapi-client/commit/ce3831a729285c6d7204ff192abe88386f89f337))

- Fix permissions
  ([`66e63f0`](https://github.com/Roslovets-Inc/strapi-client/commit/66e63f06a4159c96830d71ba86a7e618095927b7))


## v3.0.1 (2025-02-25)

### Bug Fixes

- Build package for pypi
  ([`162ec29`](https://github.com/Roslovets-Inc/strapi-client/commit/162ec2962027d1e1b06a428f6749404c211b2de2))


## v3.0.0 (2025-02-25)

### Bug Fixes

- Imports
  ([`e3bede9`](https://github.com/Roslovets-Inc/strapi-client/commit/e3bede9736caadddcb46aaa75f665216c4c4bcc3))

- Upsert to Strapi v5
  ([`f467868`](https://github.com/Roslovets-Inc/strapi-client/commit/f46786876705ccda8a199c55cfe39466d269126e))

### Continuous Integration

- Fix deployment
  ([`3e499a1`](https://github.com/Roslovets-Inc/strapi-client/commit/3e499a10b63d5dc0eef13a43afa17cbb4820504e))

- Fix deployment
  ([`91bd42d`](https://github.com/Roslovets-Inc/strapi-client/commit/91bd42d22add5750570a4b19dfe1f65669594775))

- Fix publish
  ([`f9b54c7`](https://github.com/Roslovets-Inc/strapi-client/commit/f9b54c7a4cb871cfa4e34acea7cf5d095755664e))

### Features

- Derive sync version from async
  ([`68ffbc4`](https://github.com/Roslovets-Inc/strapi-client/commit/68ffbc4efd1abfdcdabd5eb9ab4b108f84870082))

using requests library

- Document_id is str for Strapi v5
  ([`02c6535`](https://github.com/Roslovets-Inc/strapi-client/commit/02c6535495d273b59e0ad53c26ff94b548a2435a))

- Drop process_response, process_data
  ([`de8eeed`](https://github.com/Roslovets-Inc/strapi-client/commit/de8eeed62ab72300876bbce04f9dc155a5b7aa9f))

because these methods are not needed for v5

- Redesign clients. Experimental ORM
  ([`669f4a9`](https://github.com/Roslovets-Inc/strapi-client/commit/669f4a9bb5df8a53f1e17c726bb17cb9acee1c1d))

- Upgrade python requirement to 3.10, bump deps
  ([`02524de`](https://github.com/Roslovets-Inc/strapi-client/commit/02524decf66d5e3f1db676eb424230b8450a2317))

### Refactoring

- Refactor typing
  ([`b048579`](https://github.com/Roslovets-Inc/strapi-client/commit/b048579c43b36d83ff350f5cdee92cb4170d4411))

- Reorganize src files
  ([`c7f8c83`](https://github.com/Roslovets-Inc/strapi-client/commit/c7f8c830f73fc079c5c4d830dbe5a61800e9518a))


## v2.9.1 (2023-09-25)

### Bug Fixes

- Format list of values for query parameters
  ([`5e74db5`](https://github.com/Roslovets-Inc/strapi-client/commit/5e74db526d240e5a1e60ef9906a90b4607613d80))

### Chores

- **release**: 2.9.1 [skip ci]
  ([`1815d63`](https://github.com/Roslovets-Inc/strapi-client/commit/1815d636da5da05d5dfcfed1523dc1360e24e499))

## [2.9.1](https://github.com/Roslovets-Inc/strapi-client/compare/v2.9.0...v2.9.1) (2023-09-25)

### Bug Fixes

* format list of values for query parameters
  ([5e74db5](https://github.com/Roslovets-Inc/strapi-client/commit/5e74db526d240e5a1e60ef9906a90b4607613d80))


## v2.9.0 (2023-09-24)

### Chores

- **release**: 2.9.0 [skip ci]
  ([`8c23d99`](https://github.com/Roslovets-Inc/strapi-client/commit/8c23d9938c0ad3013b905c9e594b88c4f677174d))

## [2.9.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.8.0...v2.9.0) (2023-09-24)

### Features

* upload_files(), get_uploaded_files()
  ([8dd6305](https://github.com/Roslovets-Inc/strapi-client/commit/8dd630568b6cc43b5d5932d3f43275f45f1d3802))

### Features

- Upload_files(), get_uploaded_files()
  ([`8dd6305`](https://github.com/Roslovets-Inc/strapi-client/commit/8dd630568b6cc43b5d5932d3f43275f45f1d3802))


## v2.8.0 (2023-09-16)

### Chores

- **release**: 2.8.0 [skip ci]
  ([`f61a09c`](https://github.com/Roslovets-Inc/strapi-client/commit/f61a09c4ee2c46525e7a5cbfd766eb00e1d52724))

## [2.8.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.7.0...v2.8.0) (2023-09-16)

### Features

* send_post_request(), send_get_request()
  ([2b9e168](https://github.com/Roslovets-Inc/strapi-client/commit/2b9e168d1445f27a87c1cd451207b97305ea3394))

### Features

- Send_post_request(), send_get_request()
  ([`2b9e168`](https://github.com/Roslovets-Inc/strapi-client/commit/2b9e168d1445f27a87c1cd451207b97305ea3394))

to send requests to custom endpoints


## v2.7.0 (2023-09-08)

### Chores

- **release**: 2.7.0 [skip ci]
  ([`a7decdb`](https://github.com/Roslovets-Inc/strapi-client/commit/a7decdbab71f799334df70210af0e52215c2efeb))

## [2.7.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.6.1...v2.7.0) (2023-09-08)

### Features

* authorize() with token, typing
  ([7bcc9a8](https://github.com/Roslovets-Inc/strapi-client/commit/7bcc9a8704ca525637a2d00e7070dc56447833c6))

### Continuous Integration

- Update semantic release action
  ([`5bb1065`](https://github.com/Roslovets-Inc/strapi-client/commit/5bb106530350d751f030170f9e8918fb9ce6047c))

### Features

- Authorize() with token, typing
  ([`7bcc9a8`](https://github.com/Roslovets-Inc/strapi-client/commit/7bcc9a8704ca525637a2d00e7070dc56447833c6))


## v2.6.1 (2023-04-05)

### Bug Fixes

- **process_data**: Return empty dict if no data
  ([`814e25e`](https://github.com/Roslovets-Inc/strapi-client/commit/814e25e5ce7ff82d7c50451f4502a61c8d5b2f41))

### Chores

- Fix typo in comment
  ([`e273a24`](https://github.com/Roslovets-Inc/strapi-client/commit/e273a245bf3e84a80f829b31b740a6a4ff205a26))

- **release**: 2.6.1 [skip ci]
  ([`46b19a3`](https://github.com/Roslovets-Inc/strapi-client/commit/46b19a35c30de743d859e9dd9dd0c28c7dbfdca9))

### [2.6.1](https://github.com/Roslovets-Inc/strapi-client/compare/v2.6.0...v2.6.1) (2023-04-05)

### Bug Fixes

* **process_data:** return empty dict if no data
  ([814e25e](https://github.com/Roslovets-Inc/strapi-client/commit/814e25e5ce7ff82d7c50451f4502a61c8d5b2f41))


## v2.6.0 (2022-11-20)

### Chores

- **release**: 2.6.0 [skip ci]
  ([`08693df`](https://github.com/Roslovets-Inc/strapi-client/commit/08693df291153c4434469c77a23c06af16df1eb8))

## [2.6.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.5.0...v2.6.0) (2022-11-20)

### Features

* upsert_entry works with not unique entries
  ([bf7ff9c](https://github.com/Roslovets-Inc/strapi-client/commit/bf7ff9ce92a2b65b65f9e477b34fe14ad3e0d926))

### Features

- Upsert_entry works with not unique entries
  ([`bf7ff9c`](https://github.com/Roslovets-Inc/strapi-client/commit/bf7ff9ce92a2b65b65f9e477b34fe14ad3e0d926))


## v2.5.0 (2022-05-11)

### Chores

- **release**: 2.5.0 [skip ci]
  ([`79aaf65`](https://github.com/Roslovets-Inc/strapi-client/commit/79aaf65494f1ffe525c24bedc9898ec59261e20a))

## [2.5.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.4.0...v2.5.0) (2022-05-11)

### Features

* populate and fields opts for get_entry
  ([bc6a1ab](https://github.com/Roslovets-Inc/strapi-client/commit/bc6a1abec61acf845ae23da9fc743af8b8a2f6d8))

### Code Style

- Rename method
  ([`8284917`](https://github.com/Roslovets-Inc/strapi-client/commit/828491746c84a0cdb62dedef62f03abea299ca70))

### Features

- Populate and fields opts for get_entry
  ([`bc6a1ab`](https://github.com/Roslovets-Inc/strapi-client/commit/bc6a1abec61acf845ae23da9fc743af8b8a2f6d8))


## v2.4.0 (2022-05-05)

### Chores

- **release**: 2.4.0 [skip ci]
  ([`4c23492`](https://github.com/Roslovets-Inc/strapi-client/commit/4c234921d19e814b5c38b8caf8d58bf33b55c074))

## [2.4.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.3.0...v2.4.0) (2022-05-05)

### Features

* process_data()
  ([fc58542](https://github.com/Roslovets-Inc/strapi-client/commit/fc585424f3d17c12e4f3e6d6f87b3f6e87f45966))

### Features

- Process_data()
  ([`fc58542`](https://github.com/Roslovets-Inc/strapi-client/commit/fc585424f3d17c12e4f3e6d6f87b3f6e87f45966))


## v2.3.0 (2022-04-07)

### Chores

- **release**: 2.3.0 [skip ci]
  ([`d6156b1`](https://github.com/Roslovets-Inc/strapi-client/commit/d6156b1d6c3364e2342ae3709a25576ac62581ef))

## [2.3.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.2.0...v2.3.0) (2022-04-07)

### Features

* create_entry(), upsert_entry()
  ([e008099](https://github.com/Roslovets-Inc/strapi-client/commit/e008099ac51ecba504131954a868896cc23211d5))
  * delete_entry()
  ([2c2e35d](https://github.com/Roslovets-Inc/strapi-client/commit/2c2e35d17ffe740c04513b67b521d0876fe71708))
  * get_entry()
  ([d44ad7d](https://github.com/Roslovets-Inc/strapi-client/commit/d44ad7db8c42296c9890be9b3d965b66435c020e))
  * StrapiClientSync
  ([e7299d8](https://github.com/Roslovets-Inc/strapi-client/commit/e7299d8f7cc09e7b82615a04c6f169a556125ab2))

### Features

- Create_entry(), upsert_entry()
  ([`e008099`](https://github.com/Roslovets-Inc/strapi-client/commit/e008099ac51ecba504131954a868896cc23211d5))

- Delete_entry()
  ([`2c2e35d`](https://github.com/Roslovets-Inc/strapi-client/commit/2c2e35d17ffe740c04513b67b521d0876fe71708))

- Get_entry()
  ([`d44ad7d`](https://github.com/Roslovets-Inc/strapi-client/commit/d44ad7db8c42296c9890be9b3d965b66435c020e))

- Strapiclientsync
  ([`e7299d8`](https://github.com/Roslovets-Inc/strapi-client/commit/e7299d8f7cc09e7b82615a04c6f169a556125ab2))

for synchronous operations


## v2.2.0 (2022-04-05)

### Chores

- **release**: 2.2.0 [skip ci]
  ([`de1f059`](https://github.com/Roslovets-Inc/strapi-client/commit/de1f059f91b2775b0ef316a6b88e6c0d8653c5aa))

## [2.2.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.1.0...v2.2.0) (2022-04-05)

### Features

* get_all, batch_size opts for get_entities()
  ([2aebf7a](https://github.com/Roslovets-Inc/strapi-client/commit/2aebf7ac54d0b33778aaf95ebdf6cf63f232d93b))

### Features

- Get_all, batch_size opts for get_entities()
  ([`2aebf7a`](https://github.com/Roslovets-Inc/strapi-client/commit/2aebf7ac54d0b33778aaf95ebdf6cf63f232d93b))


## v2.1.0 (2022-04-03)

### Chores

- **release**: 2.1.0 [skip ci]
  ([`7fa69fd`](https://github.com/Roslovets-Inc/strapi-client/commit/7fa69fdb099a0787be612274e4b49a3fd393875b))

## [2.1.0](https://github.com/Roslovets-Inc/strapi-client/compare/v2.0.0...v2.1.0) (2022-04-03)

### Features

* fields opt for get_entries()
  ([58e0044](https://github.com/Roslovets-Inc/strapi-client/commit/58e0044db9f01aadd2f1bdf77e807e46f90b7bd2))

### Features

- Fields opt for get_entries()
  ([`58e0044`](https://github.com/Roslovets-Inc/strapi-client/commit/58e0044db9f01aadd2f1bdf77e807e46f90b7bd2))


## v2.0.0 (2022-04-01)

### Chores

- **release**: 2.0.0 [skip ci]
  ([`7dc5548`](https://github.com/Roslovets-Inc/strapi-client/commit/7dc554868e28f427dd78230761dfedec64121f4a))

## [2.0.0](https://github.com/Roslovets-Inc/strapi-client/compare/v1.2.0...v2.0.0) (2022-04-01)

### ⚠ BREAKING CHANGES

* convert code to async

### Features

* convert code to async
  ([e3c403c](https://github.com/Roslovets-Inc/strapi-client/commit/e3c403c27adcc7b19f7fafbd6b8b1ca92414d69d))

### Features

- Convert code to async
  ([`e3c403c`](https://github.com/Roslovets-Inc/strapi-client/commit/e3c403c27adcc7b19f7fafbd6b8b1ca92414d69d))

### Refactoring

- Typing
  ([`445ade4`](https://github.com/Roslovets-Inc/strapi-client/commit/445ade45af07ce047365517e7586abe3ba172aae))


## v1.2.0 (2022-04-01)

### Chores

- **release**: 1.2.0 [skip ci]
  ([`6eee113`](https://github.com/Roslovets-Inc/strapi-client/commit/6eee113e7f2e3f73565b6bb1516ee443347ad88b))

## [1.2.0](https://github.com/Roslovets-Inc/strapi-client/compare/v1.1.1...v1.2.0) (2022-04-01)

### Features

* sort, populate opts for get_entries()
  ([43b6719](https://github.com/Roslovets-Inc/strapi-client/commit/43b67193d8aebecdd572a92a6d8370bbe353a4bb))

### Features

- Sort, populate opts for get_entries()
  ([`43b6719`](https://github.com/Roslovets-Inc/strapi-client/commit/43b67193d8aebecdd572a92a6d8370bbe353a4bb))


## v1.1.1 (2022-03-31)

### Bug Fixes

- Export process_response()
  ([`f39dca3`](https://github.com/Roslovets-Inc/strapi-client/commit/f39dca3db5054febd3dec3f41c16fd7dba18531b))

### Chores

- **release**: 1.1.1 [skip ci]
  ([`dd3b4b2`](https://github.com/Roslovets-Inc/strapi-client/commit/dd3b4b2c89330afab99ba00bda83334919b93d98))

### [1.1.1](https://github.com/Roslovets-Inc/strapi-client/compare/v1.1.0...v1.1.1) (2022-03-31)

### Bug Fixes

* export process_response()
  ([f39dca3](https://github.com/Roslovets-Inc/strapi-client/commit/f39dca3db5054febd3dec3f41c16fd7dba18531b))


## v1.1.0 (2022-03-31)

### Chores

- Fix typing
  ([`d84bb41`](https://github.com/Roslovets-Inc/strapi-client/commit/d84bb412704c802aecb682ab143105994fbfe1ef))

- **release**: 1.1.0 [skip ci]
  ([`859974b`](https://github.com/Roslovets-Inc/strapi-client/commit/859974b64143d5c8d3bc36dd43e50451a43e5773))

## [1.1.0](https://github.com/Roslovets-Inc/strapi-client/compare/v1.0.0...v1.1.0) (2022-03-31)

### Features

* pagination opt for get_entries()
  ([73b1912](https://github.com/Roslovets-Inc/strapi-client/commit/73b19124e063ddfcf532016a7f87f327c1aafb2b))
  * process_response() for fetched entries
  ([11a7e22](https://github.com/Roslovets-Inc/strapi-client/commit/11a7e22e2c5e29f205a8bfbb449de3ef6904e019))
  * publication_state opt for get_entries()
  ([9b98091](https://github.com/Roslovets-Inc/strapi-client/commit/9b9809150479293a6eae0ad96111f010edde87ff))

### Features

- Pagination opt for get_entries()
  ([`73b1912`](https://github.com/Roslovets-Inc/strapi-client/commit/73b19124e063ddfcf532016a7f87f327c1aafb2b))

- Process_response() for fetched entries
  ([`11a7e22`](https://github.com/Roslovets-Inc/strapi-client/commit/11a7e22e2c5e29f205a8bfbb449de3ef6904e019))

- Publication_state opt for get_entries()
  ([`9b98091`](https://github.com/Roslovets-Inc/strapi-client/commit/9b9809150479293a6eae0ad96111f010edde87ff))


## v1.0.0 (2022-03-30)

### Chores

- **release**: 1.0.0 [skip ci]
  ([`c47928e`](https://github.com/Roslovets-Inc/strapi-client/commit/c47928e07acb6ed031880d190de923f7081d6b16))

## 1.0.0 (2022-03-30)

### Features

* get_entities(), update_entity()
  ([6a2d2b4](https://github.com/Roslovets-Inc/strapi-client/commit/6a2d2b40e1768f2658ef3b298aec7d7a257bd718))

### Continuous Integration

- Build and publish
  ([`c2b6819`](https://github.com/Roslovets-Inc/strapi-client/commit/c2b6819e576205d33a402510dc044525c0592534))

### Features

- Get_entities(), update_entity()
  ([`6a2d2b4`](https://github.com/Roslovets-Inc/strapi-client/commit/6a2d2b40e1768f2658ef3b298aec7d7a257bd718))
