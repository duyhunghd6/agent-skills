# Builder Pattern

**Category**: API Design  
**Context**: Your type has many optional configuration parameters. Constructor with many args is error-prone.  
**Source**: Extracted from **Rust Design Patterns** and common idioms.

## The Problem

Types with many optional fields lead to constructors with numerous parameters, making call sites confusing and brittle.

## The Solution

Use a **builder struct** with method chaining for incremental, readable construction.

### Owned Builder Pattern

```rust
pub struct Request {
    url: String,
    method: Method,
    headers: HashMap<String, String>,
    body: Option<Vec<u8>>,
    timeout: Duration,
}

pub struct RequestBuilder {
    url: String,
    method: Method,
    headers: HashMap<String, String>,
    body: Option<Vec<u8>>,
    timeout: Option<Duration>,
}

impl RequestBuilder {
    /// Start building a request
    pub fn new(url: impl Into<String>) -> Self {
        Self {
            url: url.into(),
            method: Method::GET,
            headers: HashMap::new(),
            body: None,
            timeout: None,
        }
    }

    /// Set HTTP method
    pub fn method(mut self, method: Method) -> Self {
        self.method = method;
        self
    }

    /// Add header
    pub fn header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.insert(key.into(), value.into());
        self
    }

    /// Set body
    pub fn body(mut self, body: Vec<u8>) -> Self {
        self.body = Some(body);
        self
    }

    /// Set timeout
    pub fn timeout(mut self, timeout: Duration) -> Self {
        self.timeout = Some(timeout);
        self
    }

    /// Consume builder and create Request
    pub fn build(self) -> Request {
        Request {
            url: self.url,
            method: self.method,
            headers: self.headers,
            body: self.body,
            timeout: self.timeout.unwrap_or(Duration::from_secs(30)),
        }
    }
}
```

### Usage

```rust
let request = RequestBuilder::new("https://api.example.com/users")
    .method(Method::POST)
    .header("Content-Type", "application/json")
    .body(json.into_bytes())
    .timeout(Duration::from_secs(10))
    .build();
```

### Fallible Build

```rust
impl RequestBuilder {
    /// Build with validation
    pub fn try_build(self) -> Result<Request, BuildError> {
        if self.url.is_empty() {
            return Err(BuildError::MissingUrl);
        }
        Ok(Request { /* ... */ })
    }
}
```

## Key Patterns

| Pattern             | Use Case                         |
| ------------------- | -------------------------------- |
| `self` methods      | Owned builder, consumed on build |
| `&mut self` methods | Reusable builder                 |
| `try_build()`       | Validation may fail              |
| `Default` trait     | Builder with all defaults        |

## Best Practices

1. **Take `self` for chaining**: Enables fluent API
2. **Use `impl Into<T>`**: Accept both `&str` and `String`
3. **Provide defaults**: sensible timeout, empty headers
4. **Validate in build()**: Catch errors at construction time
