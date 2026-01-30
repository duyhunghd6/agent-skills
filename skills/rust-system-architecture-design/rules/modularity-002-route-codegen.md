---
title: Route Codegen Macro Pattern
impact: MEDIUM
impactDescription: declarative route registration
tags: macro, proc-macro, routing, codegen, web
---

## Route Codegen Macro Pattern

Procedural macro architecture for declarative HTTP route registration. This pattern from actix-web-codegen demonstrates attribute macro design with validation, error recovery, and guard generation.

**Source**: `actix-web-codegen/src/route.rs`

### Attribute Macro API

```rust
// Single method shortcuts
#[get("/users")]
async fn list_users() -> impl Responder { ... }

#[post("/users")]
async fn create_user(body: Json<User>) -> impl Responder { ... }

// Multi-method with options
#[route("/resource", method = "GET", method = "HEAD", guard = "my_guard")]
async fn resource() -> impl Responder { ... }
```

### Argument Parsing

```rust
pub struct RouteArgs {
    pub path: syn::LitStr,
    pub options: Punctuated<syn::MetaNameValue, Token![,]>,
}

impl Parse for RouteArgs {
    fn parse(input: ParseStream<'_>) -> syn::Result<Self> {
        // Parse path literal: "/foo"
        let path = input.parse::<syn::LitStr>().map_err(|mut err| {
            err.combine(syn::Error::new(
                err.span(),
                r#"expected path literal, e.g., "/path""#,
            ));
            err
        })?;

        // Validate path pattern at compile time
        let _ = ResourceDef::new(path.value());

        // Parse remaining options
        if !input.peek(Token![,]) {
            return Ok(Self { path, options: Punctuated::new() });
        }

        input.parse::<Token![,]>()?;
        let options = input.parse_terminated(syn::MetaNameValue::parse, Token![,])?;

        Ok(Self { path, options })
    }
}
```

### Method Type Handling

```rust
macro_rules! standard_method_type {
    ($($method:ident),*) => {
        pub enum MethodType { $($method),* }

        impl MethodType {
            fn parse(method: &str) -> Result<Self, String> {
                match method {
                    $(stringify!($method) => Ok(Self::$method),)*
                    _ => Err(format!("unknown HTTP method: {}", method)),
                }
            }
        }
    };
}

standard_method_type!(Get, Post, Put, Delete, Head, Connect, Options, Trace, Patch);

// Extended type for custom methods
enum MethodTypeExt {
    Standard(MethodType),
    Custom(syn::LitStr), // e.g., "CUSTOM"
}
```

### Guard Token Generation

```rust
impl MethodTypeExt {
    fn to_tokens_single_guard(&self) -> TokenStream2 {
        match self {
            MethodTypeExt::Standard(m) => quote! {
                .guard(::actix_web::guard::#m())
            },
            MethodTypeExt::Custom(lit) => {
                let ident = Ident::new(lit.value().as_str(), Span::call_site());
                quote! {
                    .guard(::actix_web::guard::Method(
                        ::actix_web::http::Method::#ident
                    ))
                }
            }
        }
    }

    fn to_tokens_multi_guard(&self, or_chain: Vec<impl ToTokens>) -> TokenStream2 {
        debug_assert!(!or_chain.is_empty());
        quote! {
            .guard(
                ::actix_web::guard::Any(::actix_web::guard::#self())
                    #(.or(::actix_web::guard::#or_chain()))*
            )
        }
    }
}
```

### Route Struct Code Generation

```rust
impl ToTokens for Route {
    fn to_tokens(&self, output: &mut TokenStream2) {
        let name = &self.name;
        let ast = &self.ast;
        let methods = &self.args.methods;

        // Generate method guard
        let guard = if methods.len() > 1 {
            let others: Vec<_> = methods.iter().skip(1).collect();
            methods[0].to_tokens_multi_guard(others)
        } else {
            methods[0].to_tokens_single_guard()
        };

        let stream = quote! {
            #[allow(non_camel_case_types)]
            pub struct #name;

            impl ::actix_web::dev::HttpServiceFactory for #name {
                fn register(self, config: &mut ::actix_web::dev::AppService) {
                    #ast // Original function

                    let resource = ::actix_web::Resource::new(#path)
                        .name(#resource_name)
                        #guard
                        .to(#name);

                    ::actix_web::dev::HttpServiceFactory::register(resource, config);
                }
            }
        };

        output.extend(stream);
    }
}
```

### Error Recovery Pattern

```rust
pub(crate) fn with_method(
    method: Option<MethodType>,
    args: TokenStream,
    input: TokenStream,
) -> TokenStream {
    let args = match syn::parse(args) {
        Ok(args) => args,
        Err(err) => return input_and_compile_error(input, err),
    };

    let ast = match syn::parse::<syn::ItemFn>(input.clone()) {
        Ok(ast) => ast,
        Err(err) => return input_and_compile_error(input, err),
    };

    match Route::new(args, ast, method) {
        Ok(route) => route.into_token_stream().into(),
        Err(err) => input_and_compile_error(input, err),
    }
}

// Preserve original input on error for better IDE support
fn input_and_compile_error(input: TokenStream, err: syn::Error) -> TokenStream {
    let compile_error = err.to_compile_error();
    quote! { #compile_error #input }.into()
}
```

### When to Use

- Creating declarative APIs with attribute macros
- Generating boilerplate from function signatures
- Validating DSL syntax at compile time
- Building framework-like registration systems
