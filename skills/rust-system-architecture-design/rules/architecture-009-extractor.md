# Extractor Pattern

**Category**: Architecture  
**Context**: Your web framework needs to extract typed data from HTTP requests (path params, query strings, JSON bodies, headers).  
**Source**: Extracted from **Actix Web** `extract.rs`.

## The Problem

HTTP request data comes in many forms. Each handler has different extraction needs. Extracting manually in every handler is repetitive and error-prone.

## The Solution

Use a **FromRequest trait** that allows types to declare how they're extracted, then compose extractors as function parameters.

### Core Trait

```rust
/// Trait for types that can be extracted from an HTTP request
pub trait FromRequest: Sized {
    /// Error type if extraction fails
    type Error: Into<Error>;

    /// Future type for async extraction
    type Future: Future<Output = Result<Self, Self::Error>>;

    /// Extract from request parts and payload
    fn from_request(req: &HttpRequest, payload: &mut Payload) -> Self::Future;

    /// Shorthand for extracting from request only
    fn extract(req: &HttpRequest) -> Self::Future {
        Self::from_request(req, &mut Payload::None)
    }
}
```

### Built-in Extractors

```rust
// Path parameters: /users/{id}
impl<T: DeserializeOwned> FromRequest for Path<T> {
    type Error = PathError;
    type Future = Ready<Result<Self, Self::Error>>;
    // ...
}

// Query string: ?page=1&limit=10
impl<T: DeserializeOwned> FromRequest for Query<T> {
    // ...
}

// JSON body
impl<T: DeserializeOwned> FromRequest for Json<T> {
    // Uses async future for streaming body
}

// Application state
impl<T: 'static> FromRequest for Data<T> {
    // Looks up type in app extensions
}
```

### Error Handling Wrappers

```rust
// Make extraction infallible - returns None on error
impl<T: FromRequest> FromRequest for Option<T> {
    type Error = Infallible;
    type Future = FromRequestOptFuture<T::Future>;

    fn from_request(req: &HttpRequest, payload: &mut Payload) -> Self::Future {
        FromRequestOptFuture {
            fut: T::from_request(req, payload),
        }
    }
}

// Expose extraction error to handler
impl<T: FromRequest> FromRequest for Result<T, T::Error> {
    type Error = Infallible;
    // ...
}
```

### Handler Integration

```rust
// Extractors are composed via function parameters
async fn handler(
    path: Path<(u32, String)>,
    query: Query<Pagination>,
    body: Json<CreateUser>,
    state: Data<AppState>,
) -> impl Responder {
    // All extracted and type-safe
}
```

## Key Components

| Component      | Role                        |
| -------------- | --------------------------- |
| `FromRequest`  | Base extraction trait       |
| `Path<T>`      | URL path parameters         |
| `Query<T>`     | Query string parsing        |
| `Json<T>`      | JSON body deserialization   |
| `Option<T>`    | Optional extraction wrapper |
| `Result<T, E>` | Error-passing wrapper       |

## Best Practices

1. **Composition via tuples**: Handlers get multiple extractors as params
2. **Wrapper types**: `Option<T>` and `Result<T, E>` for error control
3. **Async futures**: Support streaming body extraction
4. **Error conversion**: Use `Into<Error>` for unified responses
