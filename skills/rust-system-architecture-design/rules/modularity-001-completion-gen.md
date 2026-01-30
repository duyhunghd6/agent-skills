# Shell Completion Generator

**Category**: Modularity & Extensibility  
**Context**: Your CLI tool needs to generate shell completion scripts for multiple shells (Bash, Zsh, Fish, PowerShell).  
**Source**: Extracted from **Clap** `clap_complete/src/aot/generator/`.

## The Problem

Each shell has a different syntax for completion scripts. Manually writing and maintaining completions for each shell is tedious and error-prone.

## The Solution

Use a **generator trait** that produces shell-specific completion code from a unified `Command` AST.

### Core Architecture

```rust
/// Trait for shell completion generators
pub trait Generator {
    /// Return the file name for the generated completions
    fn file_name(&self, name: &str) -> String;

    /// Generate completions and write to buffer
    fn generate(&self, cmd: &Command, buf: &mut dyn Write);

    /// Fallible generation (default: infallible wrapper)
    fn try_generate(&self, cmd: &Command, buf: &mut dyn Write) -> Result<(), Error> {
        self.generate(cmd, buf);
        Ok(())
    }
}

/// Generate completions to a specific directory
pub fn generate_to<G, S, T>(
    generator: G,
    cmd: &mut Command,
    bin_name: S,
    out_dir: T,
) -> Result<PathBuf, Error>
where
    G: Generator,
    S: Into<String>,
    T: Into<OsString>,
{
    cmd.set_bin_name(bin_name);
    let out_dir = PathBuf::from(out_dir.into());
    let file_name = generator.file_name(cmd.get_bin_name().unwrap());
    let path = out_dir.join(file_name);
    let mut file = File::create(&path)?;
    generator.generate(cmd, &mut file);
    Ok(path)
}
```

### Shell Implementations

```rust
pub struct Bash;
impl Generator for Bash {
    fn file_name(&self, name: &str) -> String {
        format!("{}.bash", name)
    }

    fn generate(&self, cmd: &Command, buf: &mut dyn Write) {
        // Generate Bash completion script
        writeln!(buf, "_{}() {{", cmd.get_name()).unwrap();
        // ... generate subcommand matching, option lists, etc.
    }
}

pub struct Zsh;
impl Generator for Zsh {
    fn file_name(&self, name: &str) -> String {
        format!("_{}", name)
    }

    fn generate(&self, cmd: &Command, buf: &mut dyn Write) {
        // Generate Zsh completion script
        writeln!(buf, "#compdef {}", cmd.get_name()).unwrap();
        // ...
    }
}

pub struct Fish;
pub struct PowerShell;
pub struct Elvish;
```

### Utility Functions

```rust
/// Get all subcommands as (name, bin_name) pairs
pub fn all_subcommands(cmd: &Command) -> Vec<(String, String)>;

/// Get short options and their aliases
pub fn shorts_and_visible_aliases(p: &Command) -> Vec<char>;

/// Get long options and their aliases
pub fn longs_and_visible_aliases(p: &Command) -> Vec<String>;
```

## Key Components

| Component     | Role                               |
| ------------- | ---------------------------------- |
| `Generator`   | Shell-agnostic generation trait    |
| `generate_to` | File-based output helper           |
| Shell structs | Implement Generator for each shell |
| `utils`       | Extract info from Command tree     |

## Best Practices

1. **AST-driven**: Generate from the same Command used for parsing
2. **Multi-shell support**: Same codebase serves all shells
3. **Build-time generation**: Include in build.rs for freshness
4. **Value hints**: Use `ValueHint` to improve completions
