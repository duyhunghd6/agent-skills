# Derive Macro Architecture

**Category**: Architecture  
**Context**: Your library needs declarative attribute-based configuration that generates builder code.  
**Source**: Extracted from **Clap** `clap_derive/` and **Diesel** `diesel_derives/`.

## The Problem

Users want declarative APIs (like `#[derive(Parser)]`) but the implementation requires complex code generation. Proc macros are powerful but error-prone.

## The Solution

Use a **separation of concerns** architecture: derive macros generate builder calls, builders provide the runtime logic.

### Architecture Layers

```
User Code               Derive Macro               Builder/Runtime
─────────────        ──────────────────         ─────────────────
#[derive(Parser)]    → Parse attributes         → Command::new()
#[arg(short)]        → Extract field info       → .arg(Arg::new()
struct Cli {         → Generate FromArgMatches    .short('n'))
    #[arg(short)]    → Output TokenStream       → .value_parser()
    name: String,                               → ArgMatches
}
```

### Proc Macro Layer

```rust
// clap_derive/src/lib.rs
#[proc_macro_derive(Parser, attributes(command, arg))]
pub fn derive_parser(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);

    // Parse attributes into intermediate representation
    let ir = parse_attrs(&input);

    // Generate builder code
    let expanded = generate_parser_impl(&ir);

    TokenStream::from(expanded)
}
```

### Intermediate Representation

```rust
// Parsed structure
struct StructInfo {
    name: Ident,
    attrs: CommandAttrs,
    fields: Vec<FieldInfo>,
}

struct FieldInfo {
    name: Ident,
    ty: Type,
    attrs: ArgAttrs,
}

struct ArgAttrs {
    short: Option<char>,
    long: Option<String>,
    default: Option<Expr>,
    value_parser: Option<Expr>,
}
```

### Generated Code Example

```rust
// User writes:
#[derive(Parser)]
struct Cli {
    #[arg(short, long)]
    name: String,
}

// Macro generates:
impl clap::FromArgMatches for Cli {
    fn from_arg_matches(matches: &ArgMatches) -> Result<Self, Error> {
        Ok(Self {
            name: matches.get_one::<String>("name")
                .ok_or_else(|| Error::missing_argument("name"))?
                .clone(),
        })
    }
}

impl clap::CommandFactory for Cli {
    fn command() -> Command {
        Command::new("cli")
            .arg(Arg::new("name")
                .short('n')
                .long("name")
                .value_parser(clap::value_parser!(String)))
    }
}
```

## Key Components

| Component         | Role                                     |
| ----------------- | ---------------------------------------- |
| Derive macro      | Parse attributes, generate impl          |
| Attribute helpers | `#[command]`, `#[arg]` for configuration |
| Builder/Runtime   | `Command`, `Arg`, `ArgMatches`           |
| Trait bridge      | `FromArgMatches`, `CommandFactory`       |

## Best Practices

1. **IR separation**: Parse once, generate multiple impls
2. **Builder delegation**: Derive generates builder calls, not raw logic
3. **Error spans**: Use `syn::Error::new_spanned` for good error locations
4. **Fallback trait impls**: Provide non-derive alternative for flexibility
