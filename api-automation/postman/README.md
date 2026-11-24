# Postman Collection

File: `JSONPlaceholder-Posts.postman_collection.json`

## Import

1. Open Postman.
2. Select **Import**.
3. Choose `JSONPlaceholder-Posts.postman_collection.json`.
4. Open the collection and run requests individually or use Collection Runner.

## Configuration

The collection includes a collection variable:

| Variable | Default value |
|---|---|
| `baseUrl` | `https://jsonplaceholder.typicode.com` |

Change `baseUrl` in the collection variables to point to another compatible environment.

## Included requests

- Read: list posts, get post by ID, filter by user, and retrieve comments through the nested `/posts/{id}/comments` route.
- CRUD: create, replace with PUT, partially update with PATCH, delete.
- Negative: unknown post ID.

Each request has Postman test scripts for HTTP status, response content and important fields.

## Demo API limitation

JSONPlaceholder simulates write operations. POST/PUT/PATCH/DELETE responses demonstrate request/response behavior, but the remote data is not persistently changed. In particular, a generated post ID cannot be fetched later as a stored resource. See the [official guide](https://jsonplaceholder.typicode.com/guide.html).
