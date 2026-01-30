---
title: "Permission Descriptor System"
impact: "Fine-grained capability-based security for resource access"
tags: ["security", "permissions", "capabilities", "descriptors"]
category: "security"
level: "1-system"
champion: "Deno"
---

# Permission Descriptor System

## Context

Secure runtimes need granular control over resource access (files, network, environment). A simple allow/deny model is insufficient for complex applications that need partial access or runtime permission requests.

## Problem

How do you implement a permission system that:

- Supports hierarchical permissions (allow read for `/home`, deny for `/home/secrets`)
- Tracks permission state (granted, prompt, denied)
- Allows runtime permission requests with user prompts
- Supports auditing and broker patterns

## Solution

Use the **Descriptor Pattern** with traits for different permission scopes.

### Incorrect ❌

```rust
// Boolean flags - no granularity
struct Permissions {
    allow_read: bool,
    allow_write: bool,
    allow_net: bool,
}

impl Permissions {
    fn check_read(&self, _path: &Path) -> bool {
        self.allow_read  // No path-specific control
    }
}
```

### Correct ✅

```rust
use std::collections::HashSet;
use std::path::PathBuf;

/// Permission states following W3C permissions model
#[derive(Clone, Copy, PartialEq)]
pub enum PermissionState {
    Granted,
    Prompt,    // User can be asked
    Denied,
}

/// Trait for allow descriptors (what's permitted)
pub trait AllowDescriptor: Debug + Eq + Clone + Hash {
    type QueryDesc<'a>: QueryDescriptor;

    /// Display name for prompts
    fn display_name(&self) -> Cow<'_, str>;
}

/// Trait for query descriptors (what's being checked)
pub trait QueryDescriptor: Debug {
    type AllowDesc: AllowDescriptor;

    /// Check against permission
    fn check_in_permission(
        &self,
        permission: &UnaryPermission<Self::AllowDesc>,
        api_name: Option<&str>,
    ) -> Result<(), PermissionDeniedError>;

    /// Flag name for CLI
    fn flag_name() -> &'static str;
}

/// Unified permission container with sorted descriptors
#[derive(Clone)]
pub struct UnaryPermission<TAllowDesc: AllowDescriptor> {
    /// Sorted list mixing granted, denied, and ignored items
    descriptors: Vec<UnaryPermissionDesc<TAllowDesc>>,
    /// Global grant flag for performance
    granted_global: bool,
    /// Prompt denied for all
    prompt_denied_global: bool,
}

/// Internal descriptor that tracks both allows and denies
enum UnaryPermissionDesc<TAllowDesc: AllowDescriptor> {
    Granted(TAllowDesc),
    PromptDenied(Option<TAllowDesc::DenyDesc>),
    Ignored(TAllowDesc::DenyDesc),
}

impl<TAllowDesc: AllowDescriptor> UnaryPermission<TAllowDesc> {
    /// Fast path for full permission
    pub fn is_allow_all(&self) -> bool {
        self.granted_global
            && !self.descriptors.iter().any(|d| matches!(d,
                UnaryPermissionDesc::PromptDenied(_) |
                UnaryPermissionDesc::Ignored(_)
            ))
    }

    /// Check permission with optional prompting
    pub fn check_desc(
        &self,
        desc: Option<&TAllowDesc::QueryDesc<'_>>,
        api_name: Option<&str>,
    ) -> Result<(), PermissionDeniedError> {
        // Fast path: global allow
        if self.is_allow_all() {
            return Ok(());
        }

        let state = self.query_desc(desc);
        match state {
            PermissionState::Granted => Ok(()),
            PermissionState::Prompt => {
                // Trigger user prompt
                self.request_desc(desc, api_name)
            }
            PermissionState::Denied => {
                Err(PermissionDeniedError {
                    access: format!("{} access", TAllowDesc::QueryDesc::flag_name()),
                    name: TAllowDesc::QueryDesc::flag_name(),
                })
            }
        }
    }
}

/// Example: Read permission descriptor
#[derive(Clone, Debug, Eq, PartialEq, Hash)]
pub struct ReadDescriptor(pub PathBuf);

impl AllowDescriptor for ReadDescriptor {
    type QueryDesc<'a> = ReadDescriptor;

    fn display_name(&self) -> Cow<'_, str> {
        self.0.display().to_string().into()
    }
}

/// Permissions container with all permission types
pub struct PermissionsContainer {
    pub read: UnaryPermission<ReadDescriptor>,
    pub write: UnaryPermission<WriteDescriptor>,
    pub net: UnaryPermission<NetDescriptor>,
    pub env: UnaryPermission<EnvDescriptor>,
    // ... other permission types
}

impl PermissionsContainer {
    /// Create child permissions (for workers)
    pub fn create_child_permissions(
        &self,
        arg: ChildPermissionArg,
    ) -> Result<PermissionsContainer, PermissionError> {
        // Child can only have subset of parent permissions
        Ok(PermissionsContainer {
            read: self.read.create_child(arg.read)?,
            write: self.write.create_child(arg.write)?,
            // ...
        })
    }
}
```

### Key Pattern: Broker for External Authorization

```rust
/// External permission broker (for sandboxed deployments)
pub struct PermissionBroker {
    socket: Mutex<IpcPipe>,
}

impl PermissionBroker {
    pub fn check(
        &self,
        name: &str,
        value: String,
    ) -> io::Result<BrokerResponse> {
        let request = PermissionBrokerRequest {
            name,
            value: &value,
            datetime: chrono::Utc::now().to_rfc3339(),
        };

        // Send to external broker process
        let mut stream = self.socket.lock();
        serde_json::to_writer(&mut *stream, &request)?;

        // Wait for response
        let response: PermissionBrokerResponse =
            serde_json::from_reader(&mut *stream)?;

        Ok(response.into())
    }
}
```

## Impact

- **Security**: Fine-grained, hierarchical permission control
- **UX**: Runtime permission prompts like browsers
- **Flexibility**: Supports external brokers for enterprise deployments
- **Auditability**: All permission checks can be logged

## When NOT to Use

- Fully trusted execution environments
- Simple scripts with all-or-nothing access
- Performance-critical inner loops (use allow_all fast path)

## References

- Deno: [runtime/permissions/lib.rs](https://github.com/denoland/deno/blob/main/runtime/permissions/lib.rs)
- W3C Permissions API
- Capability-based security principles
