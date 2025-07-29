# Changelog

### Version - 0.3.0 (2025-05-20)

- `Endpoint.method` now has a default value of `GET`.
- `Endpoint.method` type changed from str to Literal['GET', 'POST', 'PUT', 'DELETE'].

### Version - 0.2.0 (2025-05-20)

- `Endpoint.service_name` is now optionally loaded from the `SERVICE_NAME` environment variable during serialization (`model_dump`), if it is `None`.

### Version - 0.1.8 (2024-10-24)

- Updated the expected status code for a successful endpoint registration response from 200 to 204 in the Gateway class.

### Version - 0.1.7 (2024-10-24)

- Added Exceptions for the Gateway class.
- Improve the register_endpoints method in Gateway class.
- Restructure module.
- Added Changelog.
