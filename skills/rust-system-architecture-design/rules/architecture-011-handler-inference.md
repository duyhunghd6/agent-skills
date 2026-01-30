# Handler Type Inference

**Category**: Architecture  
**Context**: Your web framework needs to support multiple handler signatures (sync, async, different arities) without forcing users to implement traits manually.  
**Source**: Extracted from **Actix Web** `handler.rs`.

## The Problem

Different handlers have different signatures: some are sync, some async, some take 0 args, some take 5. Supporting all permutations through manual trait implementation is impractical.

## The Solution

Use **blanket implementations with marker types** to automatically infer handler behavior from function signatures.

### Core Trait

```rust
/// Marker trait for handlers
pub trait Handler<Args>: Clone + 'static {
    type Output;
    type Future: Future<Output = Self::Output>;

    fn call(&self, args: Args) -> Self::Future;
}
```

### Blanket Implementations via Macro

```rust
// Generate impl for each arity (0..12)
macro_rules! factory_tuple {
    ($($param:ident),*) => {
        impl<Func, Fut, $($param,)*> Handler<($($param,)*)> for Func
        where
            Func: Fn($($param),*) -> Fut + Clone + 'static,
            Fut: Future,
        {
            type Output = Fut::Output;
            type Future = Fut;

            fn call(&self, ($($param,)*): ($($param,)*)) -> Self::Future {
                (self)($($param,)*)
            }
        }
    };
}

factory_tuple!();
factory_tuple!(A);
factory_tuple!(A, B);
factory_tuple!(A, B, C);
// ... up to 12 params
```

### Extractors as Arguments

```rust
/// Route registration uses the Handler trait
pub fn to<F, Args>(handler: F) -> Route
where
    F: Handler<Args>,
    Args: FromRequest + 'static,
    F::Output: Responder + 'static,
{
    // Handler + extractors compose automatically
}

// Usage - extractors are inferred from parameter types
App::new()
    .route("/users/{id}", web::get().to(get_user))

async fn get_user(path: Path<u32>, db: Data<DbPool>) -> impl Responder {
    // Path and Data are automatically extracted
}
```

### Response Inference

```rust
/// Trait for types that can become HTTP responses
pub trait Responder {
    type Body: MessageBody;

    fn respond_to(self, req: &HttpRequest) -> HttpResponse<Self::Body>;
}

// Many types implement Responder
impl Responder for String { /* ... */ }
impl Responder for &'static str { /* ... */ }
impl<T: Serialize> Responder for Json<T> { /* ... */ }
impl<R: Responder, E: ResponseError> Responder for Result<R, E> { /* ... */ }
```

## Key Components

| Component     | Role                            |
| ------------- | ------------------------------- |
| `Handler`     | Marker trait for all handlers   |
| Arity macros  | Generate impls for 0-12 params  |
| `FromRequest` | Extract handler arguments       |
| `Responder`   | Convert return to HTTP response |

## Best Practices

1. **Macro-generated impls**: Cover all arities without repetition
2. **Type inference**: Users write normal functions, framework infers
3. **Tuple-based args**: Extractors compose via (A, B, C) tuples
4. **Dual trait bridge**: FromRequest for input, Responder for output
