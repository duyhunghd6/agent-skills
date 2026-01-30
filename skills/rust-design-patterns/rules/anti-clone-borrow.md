---
title: Clone to Satisfy Borrow Checker
impact: MEDIUM
impactDescription: avoid performance overhead from unnecessary cloning
tags: anti-pattern, clone, borrow-checker, performance, ownership
---

## Clone to Satisfy Borrow Checker (Anti-pattern)

Don't clone values just to make the borrow checker happy. Find the proper ownership pattern instead.

**Incorrect (unnecessary clone):**

```rust
fn process(data: &Vec<String>) {
    let data = data.clone(); // Expensive clone!
    for item in data {
        println!("{}", item);
    }
}

// Or this common mistake:
fn get_item(map: &HashMap<String, Item>, key: &str) -> Item {
    map.get(key).unwrap().clone() // Cloning just to return
}
```

**Correct (proper borrowing):**

```rust
fn process(data: &[String]) {
    for item in data {
        println!("{}", item);
    }
}

fn get_item<'a>(map: &'a HashMap<String, Item>, key: &str) -> &'a Item {
    map.get(key).unwrap() // Return reference instead
}

// Or if ownership transfer is needed, take ownership:
fn process_owned(data: Vec<String>) {
    for item in data {
        println!("{}", item);
    }
}
```

**When Clone IS Appropriate:**

```rust
// 1. When you need independent copies
let config = shared_config.clone();
modify_for_this_request(&mut config);

// 2. For cheap-to-clone types (Rc, Arc, small Copy types)
let handle = arc_handle.clone(); // Arc clone is cheap

// 3. When crossing thread boundaries
let data = shared_data.clone();
std::thread::spawn(move || {
    process(data);
});
```

**Motivation:**

- Cloning can be expensive (O(n) for collections)
- Often hides underlying design issues
- Proper borrowing is usually possible with refactoring

**Discussion:**

If you find yourself cloning to satisfy the borrow checker, consider:

1. Can you return a reference instead?
2. Can you restructure to avoid simultaneous borrows?
3. Should the caller provide owned data?
4. Would `Rc`/`Arc` be more appropriate?

Reference: [Rust Design Patterns - Clone/Borrow](https://rust-unofficial.github.io/patterns/anti_patterns/borrow_clone.html)
