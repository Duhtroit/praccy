# Language reference

These are the per-language details the course deliberately left out. They are
lookup, not lesson: nobody learns a range convention by being told to, and
putting them in the reading order meant twenty minutes on syntax nobody needed
yet.

Every example here is runnable in this project. `python3 practice.py --tier
easy --lang <language>` is the fastest way to try one.

## Loop ranges, in all five languages

The same loop means different things. This is the single largest source of
silent wrong answers when moving between languages.

| | Python | C++ | C# | Java | Rust |
|---|---|---|---|---|---|
| variable | `i` | `i` | `i` | `i` | `i` |
| declaration | `i = 0` | `int i = 0;` | `int i = 0;` | `int i = 0;` | `let mut i = 0;` |
| exclusive end | `range(n)` | `i < n` | `i < n` | `i < n` | `while i < n` |
| inclusive end | `range(n + 1)` | `i <= n` | `i <= n` | `i <= n` | `while i <= n` |
| last value | `n - 1` | `n` | `n` | `n` | `n` |
| step | `range(0, n, 2)` | `i += 2` | `i += 2` | `i += 2` | `i += 2` |
| reverse | `range(n - 1, -1, -1)` | `i >= 0` | `i >= 0` | `i >= 0` | `while i > 0` |
| length of a list | `len(xs)` | `xs.size()` | `xs.Count` | `xs.length` | `xs.len()` |
| last index | `len(xs) - 1` | `xs.size() - 1` | `xs.Count - 1` | `xs.length - 1` | `xs.len() - 1` |

C++, C# and Java all need a separate variable declared before the loop, and all
three scope it to the loop body only. Python and Rust do not.

## Strings

Strings are immutable in all five. `s[0] = 'x'` is a compile error in four of
them and silently builds a different string in Python's case only if you assign
back to a new name.

```python
s = "abc"
s = s + "d"          # fine, and O(n) each time
"".join(parts)       # better when you are adding in a loop
```

```cpp
string s = "abc";
s += "d";
s.push_back('e');
```

```csharp
string s = "abc";
s += "d";
```

```java
String s = "abc";
s += "d";
```

```rust
let mut s = String::from("abc");
s.push('d');
```

### Char against number

In C++ a character is not a small integer you can compare to a number. `'a' ==
97` is false, and it compiles.

```cpp
char c = 'a';
int code = (int)c;              // explicit
if (c == 'a') { }               // correct
// if (c == 97) { }             // wrong, and quietly so
```

Java is the same, needing `(int) c` or `c - 'a'`. C#, Python and Rust have no
such trap: `'a'` compares to `'a'` and `ord('a')` gives the number.

### Case and membership

```python
s.lower() in "aeiou"             # membership, and a subtlety: a multi-char
                                 # needle can match across the string
set("aeiou") & set(s.lower())   # no such subtlety
```

```cpp
string vowels = "aeiou";
s.find_first_of(vowels) != string::npos
```

```csharp
s.IndexOfAny(vowels) >= 0
```

```java
"aeiou".indexOf(c) >= 0
```

```rust
"aeiou".contains(c)
```

## Sorting

The comparison is the part that differs. Returning a bool is C++ and C#; Java
and Rust want a signed integer.

```python
xs.sort()                                   # in place
ys = sorted(xs, key=lambda x: x[0])        # by a key
```

```cpp
sort(xs.begin(), xs.end());
sort(ys.begin(), ys.end(), [](auto& a, auto& b) { return a[0] < b[0]; });
```

```csharp
xs.Sort();
ys.Sort((a, b) => a[0].CompareTo(b[0]));
```

```java
Collections.sort(xs);
ys.sort((a, b) -> Integer.compare(a[0], b[0]));
```

```rust
xs.sort();
ys.sort_by(|a, b| a[0].cmp(&b[0]));
```

## A function used once

A lambda is worth writing when you need a function as a value, which in this
catalogue means passing one to a sort or a higher-order method. It is not worth
writing to save three lines of a loop you will read again in an hour.

| | |
|---|---|
| Python | `lambda x: x[0]`, or `def f(x): return x[0]` |
| C++ | `[](auto x) { return x[0]; }` |
| C# | `x => x[0]` |
| Java | `x -> x[0]` |
| Rust | `\|x\| x[0]` |

Python has no arrow syntax, so a named `def` is often clearer there.

## Division

Integer division truncates toward zero in C++, C#, Java and Rust. Python's `/`
is true division and floors instead, which rounds negative halves the other way.

```python
-7 / 2      # -3.5   -- not what you want
-7 // 2     # -4     -- floors
round(-7 / 2)  # -4  -- in Python, round() floors
```

```cpp
-7 / 2      # -3
```

```csharp
-7 / 2      # -3
```

```java
-7 / 2      # -3
```

```rust
-7 / 2      # -3
```

If a prompt's expected values are computed with a different convention than the
one you typed, the answers will be off by one on the negatives and nothing else
will explain it.

## Digits

The same loop in all five, with one language-specific trap: in C++ and Java
`char - '0'` gives the number, in C# it needs `(int)(c - '0')`, in Python
`int(c)`, and in Rust `c as u32 - b'0'`.

```python
total = 0
while n > 0:
    total += n % 10
    n //= 10
```

The `n //= 10` at the end is the part people forget, and the reason their digit
questions never terminate.
