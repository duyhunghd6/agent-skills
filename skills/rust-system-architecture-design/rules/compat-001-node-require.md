---
title: "Node Compatibility Layer"
impact: "Seamless Node.js module loading in non-Node runtimes"
tags: ["node", "compatibility", "require", "modules", "interop"]
category: "compatibility"
level: "2-data"
champion: "Deno"
---

# Node Compatibility Layer

## Context

Runtimes that want to support Node.js packages must implement the CommonJS `require()` resolution algorithm, handle package.json exports, and bridge between ESM and CJS module systems.

## Problem

How do you create a Node.js compatibility layer that:

- Resolves `require()` calls following Node's algorithm
- Handles package.json exports and imports fields
- Bridges ESM and CJS module systems
- Integrates with npm package resolution

## Solution

Use a **Loader + Resolver + Ops Bridge** pattern with generic system traits.

### Incorrect ❌

```rust
// Hardcoded Node logic without abstraction
fn require(specifier: &str, parent: &str) -> Result<Module> {
    // Directly implemented Node logic
    let paths = vec![format!("{}/node_modules", parent)];
    for path in paths {
        let file = Path::new(&path).join(specifier);
        if file.exists() {
            return load_file(&file);
        }
    }
    Err(Error::NotFound)
}
```

### Correct ✅

```rust
use std::path::{Path, PathBuf};
use std::borrow::Cow;
use deno_core::op2;

/// Trait for Node module loading - allows different implementations
pub trait NodeRequireLoader: 'static {
    /// Load file contents as text (lossy for non-UTF8)
    fn load_text_file_lossy(&self, path: &Path) -> Result<String, AnyError>;

    /// Check read permissions for file access
    fn ensure_read_permission(
        &self,
        permissions: &mut dyn NodePermissions,
        path: &Path,
    ) -> Result<Cow<'_, Path>, AnyError>;

    /// Resolve node_modules paths for a given directory
    fn resolve_require_node_module_paths(
        &self,
        from: &Path,
    ) -> Vec<String>;

    /// Check if a file is potentially CommonJS
    fn is_maybe_cjs(&self, url: &Url) -> Result<bool, ClosestPkgJsonError>;
}

/// Generic system trait for filesystem operations
pub trait ExtNodeSys: Clone + Send + Sync + 'static {
    fn fs_metadata(&self, path: &Path) -> std::io::Result<Metadata>;
    fn fs_is_dir_no_err(&self, path: &Path) -> bool;
    fn fs_canonicalize(&self, path: &Path) -> std::io::Result<PathBuf>;
    fn env_current_dir(&self) -> std::io::Result<PathBuf>;
}

/// Op for resolving require paths - generic over system trait
#[op2]
pub fn op_require_node_module_paths<TSys: ExtNodeSys + 'static>(
    state: &mut OpState,
    #[string] from: &str,
) -> Result<Vec<String>, RequireError> {
    let sys = state.borrow::<TSys>().clone();
    let loader = state.borrow::<NodeRequireLoaderRc>().clone();

    // Normalize the path
    let from = if from.starts_with("file:///") {
        Cow::Owned(url_to_file_path(&Url::parse(from)?)?)
    } else {
        let current_dir = sys.env_current_dir()
            .map_err(|e| RequireErrorKind::UnableToGetCwd(e))?;
        normalize_path(Cow::Owned(current_dir.join(from)))
    };

    // Platform-specific handling
    if cfg!(windows) {
        let from_str = from.to_str().unwrap();
        if from_str.len() >= 3 {
            let bytes = from_str.as_bytes();
            if bytes[from_str.len() - 1] == b'\\'
                && bytes[from_str.len() - 2] == b':'
            {
                return Ok(vec![format!("{}node_modules", from_str)]);
            }
        }
    }

    // Unix root special case
    if from.to_string_lossy() == "/" {
        return Ok(vec!["/node_modules".to_string()]);
    }

    Ok(loader.resolve_require_node_module_paths(&from))
}
```

### Key Pattern: Package Exports Resolution

```rust
#[op2]
#[string]
pub fn op_require_resolve_exports<TSys: ExtNodeSys + 'static>(
    state: &mut OpState,
    #[string] name: &str,
    #[string] expansion: &str,
    #[string] modules_path_str: &str,
    #[string] parent_path: &str,
) -> Result<Option<String>, RequireError> {
    let node_resolver = state.borrow::<NodeResolverRc>().clone();
    let pkg_json_resolver = state.borrow::<PackageJsonResolverRc>().clone();
    let sys = state.borrow::<TSys>().clone();

    // Find package.json with exports field
    let modules_specifier = url_from_file_path(Path::new(modules_path_str))?;

    let pkg_path = if node_resolver.in_npm_package(&modules_specifier) {
        // Different resolution for npm packages
        resolve_from_npm_folder(...)
    } else {
        path_resolve([modules_path_str, name].into_iter())
    };

    if !sys.fs_is_dir_no_err(&pkg_path) {
        return Ok(None);
    }

    // Load package.json
    let pkg = pkg_json_resolver
        .load_package_json(&pkg_path.join("package.json"))?;

    if pkg.exports.is_none() {
        return Ok(None);
    }

    // Build referrer for resolution context
    let referrer = if parent_path.is_empty() {
        None
    } else {
        Some(PathBuf::from(parent_path))
    };

    // Resolve through exports field
    let result = node_resolver.package_exports_resolve(
        &pkg_path,
        &format!(".{expansion}"),
        &pkg,
        referrer.as_ref().map(|r| UrlOrPathRef::from_path(r)),
        node_resolver.require_conditions(),
        ResolutionMode::Import,
    )?;

    Ok(Some(url_or_path_to_string(result)?))
}
```

### Key Pattern: Self-Reference Resolution

```rust
#[op2]
#[string]
pub fn op_require_try_self<TSys: ExtNodeSys + 'static>(
    state: &mut OpState,
    #[string] parent_path: &str,
    #[string] request: &str,
) -> Result<Option<String>, RequireError> {
    let pkg_json_resolver = state.borrow::<PackageJsonResolverRc>().clone();
    let node_resolver = state.borrow::<NodeResolverRc>().clone();

    // Find closest package.json
    let pkg = pkg_json_resolver
        .get_closest_package_json(Path::new(parent_path))?
        .flatten();

    let Some(pkg) = pkg else {
        return Ok(None);
    };

    // Check if exports field exists
    if pkg.exports.is_none() {
        return Ok(None);
    }

    // Extract package name from request
    let pkg_name = &pkg.name;
    let slash_with_export = request
        .strip_prefix(pkg_name)
        .filter(|t| t.starts_with('/'));

    let expansion = match slash_with_export {
        Some(exp) => Cow::Owned(format!(".{}", exp)),
        None => Cow::Borrowed("."),
    };

    // Invalidate cache and resolve
    NodeResolutionThreadLocalCache::invalidate();

    let result = node_resolver.package_exports_resolve(
        &pkg.path,
        &expansion,
        &pkg,
        Some(&UrlOrPathRef::from_path(parent_path)),
        node_resolver.require_conditions(),
        ResolutionMode::Require,
    )?;

    Ok(Some(url_or_path_to_string(result)?))
}
```

## Impact

- **Compatibility**: Run Node.js packages without modification
- **Extensibility**: Generic traits allow custom implementations
- **Performance**: Cache-aware resolution
- **Security**: Permission checks on file access

## When NOT to Use

- Pure ESM-only environments
- Sandboxed environments without filesystem
- When Node compatibility isn't required

## References

- Deno: [ext/node/ops/require.rs](https://github.com/denoland/deno/blob/main/ext/node/ops/require.rs)
- Node.js module resolution algorithm
- package.json exports specification
