## API endpoint standards and conventions

- **RESTful Design**: Follow REST principles with clear resource-based URLs and appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **Consistent Naming**: Use consistent, lowercase, hyphenated or underscored naming conventions for endpoints across the API
- **Versioning**: Implement API versioning strategy (URL path or headers) to manage breaking changes without disrupting existing clients
- **Plural Nouns**: Use plural nouns for resource endpoints (e.g., `/users`, `/products`) for consistency
- **Nested Resources**: Limit nesting depth to 2-3 levels maximum to keep URLs readable and maintainable
- **Query Parameters**: Use query parameters for filtering, sorting, pagination, and search rather than creating separate endpoints
- **HTTP Status Codes**: Return appropriate, consistent HTTP status codes that accurately reflect the response (200, 201, 400, 404, 500, etc.)
- **Rate Limiting Headers**: Include rate limit information in response headers to help clients manage their usage
- **Consistent Throttling**: Surface `429 Too Many Requests` responses with retry hints whenever requests violate published rate limits
- **Response Envelope**: Return a predictable JSON body shaped as `{ data, errors, meta }` so clients can rely on a single parsing path
- **Pagination Defaults**: Offer cursor-based pagination with sensible defaults and include `next_cursor`/`prev_cursor` metadata in responses
- **Idempotent Mutations**: Require `Idempotency-Key` headers for POST/PUT/PATCH endpoints that mutate state to guard against retries
- **Error Triplets**: When an error occurs, include a machine-readable `code`, a user-friendly `message`, and a developer-focused `hint`
- **OpenAPI First**: Keep an OpenAPI spec up-to-date and generate TypeScript clients/types from it so backend and frontend stay in lockstep
