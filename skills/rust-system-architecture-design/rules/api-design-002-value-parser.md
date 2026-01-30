# Value Parser Pipeline

**Category**: API Design  
**Context**: Your CLI framework needs to convert command-line strings to typed values with validation.  
**Source**: Extracted from **Clap** `builder/value_parser.rs`.

## The Problem

CLI arguments come as strings but applications need typed values. Different types require different parsing, validation, and error messages.

## The Solution

Use a **parser pipeline** with factory traits that produce composable, type-safe parsers.

### Core Architecture

```rust
/// Type-erased parser that can parse into any type
pub struct ValueParser(Box<dyn AnyValueParser>);

/// Type-safe parser trait
pub trait TypedValueParser: Clone + Send + Sync {
    type Value: Send + Sync + Clone;

    fn parse_ref(
        &self,
        cmd: &Command,
        arg: Option<&Arg>,
        value: &OsStr,
    ) -> Result<Self::Value, Error>;
}

/// Factory trait - types declare their own parser
pub trait ValueParserFactory {
    type Parser: TypedValueParser + Send + Sync + Clone;
    fn value_parser() -> Self::Parser;
}
```

### Built-in Parsers

```rust
// String types
impl ValueParserFactory for String {
    type Parser = ValueParser;
    fn value_parser() -> Self::Parser {
        ValueParser::string()
    }
}

// Numeric types with range validation
impl ValueParserFactory for u32 {
    type Parser = RangedI64ValueParser<u32>;
    fn value_parser() -> Self::Parser {
        let start: i64 = u32::MIN.into();
        let end: i64 = u32::MAX.into();
        RangedI64ValueParser::new().range(start..=end)
    }
}

// Path types
impl ValueParserFactory for PathBuf {
    type Parser = PathBufValueParser;
    fn value_parser() -> Self::Parser {
        PathBufValueParser::new()
    }
}
```

### Parser Combinators

```rust
/// Map parsed value to another type
pub struct MapValueParser<P, F> {
    parser: P,
    func: F,
}

impl<T> ValueParserFactory for Box<T>
where
    T: ValueParserFactory + Send + Sync + Clone,
{
    type Parser = MapValueParser<<T as ValueParserFactory>::Parser, fn(T) -> Box<T>>;

    fn value_parser() -> Self::Parser {
        T::value_parser().map(Box::new)
    }
}
```

## Key Components

| Component              | Role                          |
| ---------------------- | ----------------------------- |
| `ValueParser`          | Type-erased container         |
| `TypedValueParser`     | Strongly-typed parsing trait  |
| `ValueParserFactory`   | Associates types with parsers |
| `MapValueParser`       | Transform parsed values       |
| `RangedI64ValueParser` | Numeric range validation      |

## Best Practices

1. **Factory pattern**: Types opt-in to parsing via trait impl
2. **Composable via map**: Build complex parsers from simple ones
3. **Rich error context**: Include command and argument info in errors
4. **Range validation**: Catch overflow before runtime
