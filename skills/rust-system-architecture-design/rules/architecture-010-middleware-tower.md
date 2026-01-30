# Middleware Transform Tower

**Category**: Architecture  
**Context**: Your service layer needs composable request/response processing (logging, auth, compression, rate limiting).  
**Source**: Extracted from **Actix Web** `awc/src/middleware/`.

## The Problem

Cross-cutting concerns like logging, authentication, and error handling need to wrap multiple services. Manually wrapping creates deep nesting and tight coupling.

## The Solution

Use a **Transform trait** that wraps services to create middleware layers, composable into a tower.

### Core Architecture

```rust
/// Transforms a service type into a wrapped service
pub trait Transform<S, Req> {
    /// The wrapped service type
    type Transform: Service<Req>;

    /// Create wrapped service from inner service
    fn new_transform(self, service: S) -> Self::Transform;
}

/// Identity transform - returns service unchanged
impl<S, Req> Transform<S, Req> for () {
    type Transform = S;

    fn new_transform(self, service: S) -> Self::Transform {
        service
    }
}
```

### Middleware Nesting

```rust
/// Compose two transforms: parent wraps child wraps service
pub struct NestTransform<T1, T2, S, Req> {
    child: T1,  // Inner transform
    parent: T2, // Outer transform
}

impl<T1, T2, S, Req> Transform<S, Req> for NestTransform<T1, T2, S, Req>
where
    T1: Transform<S, Req>,
    T2: Transform<T1::Transform, Req>,
{
    type Transform = T2::Transform;

    fn new_transform(self, service: S) -> Self::Transform {
        let service = self.child.new_transform(service);
        self.parent.new_transform(service)
    }
}
```

### Concrete Middleware Example

```rust
/// Redirect middleware - follows HTTP redirects
pub struct Redirect {
    max_redirects: u8,
}

impl<S> Transform<S, ConnectRequest> for Redirect
where
    S: Service<ConnectRequest, Response = ConnectResponse>,
{
    type Transform = RedirectService<S>;

    fn new_transform(self, service: S) -> Self::Transform {
        RedirectService {
            connector: service,
            max_redirect_times: self.max_redirects,
        }
    }
}

pub struct RedirectService<S> {
    connector: S,
    max_redirect_times: u8,
}

impl<S> Service<ConnectRequest> for RedirectService<S> {
    type Response = ConnectResponse;
    type Error = SendRequestError;
    type Future = RedirectServiceFuture<S>;

    fn call(&self, req: ConnectRequest) -> Self::Future {
        // Wrap inner call, handle redirects
    }
}
```

## Key Components

| Component          | Role                               |
| ------------------ | ---------------------------------- |
| `Transform`        | Create wrapped services            |
| `NestTransform`    | Compose transforms                 |
| `Service`          | Base service trait (actix-service) |
| Middleware structs | Implement Transform for behavior   |

## Best Practices

1. **Separate config from service**: Transform holds config, Service runs requests
2. **Automatic nesting**: Use `.wrap()` builder for clean chaining
3. **Type-level composition**: Compiler resolves final service type
4. **State ownership**: Service owns cloned config, Transform is consumed
