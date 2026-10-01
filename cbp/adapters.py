"""Per-language execution adapters.

Each adapter wraps the user's source in a generated harness, runs it once per
submission in a subprocess with a hard timeout, and returns one value per test
case. The harness prints a tagged JSON envelope per case so the string "true"
never collapses into the boolean true across the process boundary.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from typing import Any, List, Optional

from .errors import RunError
from .strictness import LIST_TYPES, RETURN_TYPES
from . import toolchain as _toolchain
from .toolchain import find as _find_binary

TIMEOUT_SECONDS = 10
COMPILE_TIMEOUT = 180


# --------------------------------------------------------------------------
# Literal rendering
# --------------------------------------------------------------------------

def _py_literal(value: Any, kind: str = "array") -> str:
    """Render one argument as a Python expression.

    `kind` is the contract type from the signature, not the Python type. They
    usually agree, and where they do not -- a string argument is `stri` inside
    a list -- the contract is the one that decides.
    """
    return repr(value)


def _cpp_literal(value: Any, kind: str = "array") -> str:
    """Render one argument as a C++ expression of the type its contract names.

    `kind` is the contract type from the signature, not the Python type of the
    value. The two agree for scalars and disagree for the structural ones,
    where the contract is the only thing that knows the shape: a tree is a
    vector of optionals and a matrix is a vector of vectors, and both have to
    be written out in full or the compiler cannot tell an empty one from a
    mistake.
    """
    if kind == "tree":
        return _braced("vector<optional<int>>",
                       ["nullopt" if v is None else repr(v) for v in value])
    if kind in ("matrix", "graph"):
        return "vector<vector<int>>{" + ", ".join(
            "{" + ", ".join(str(cell) for cell in row) + "}" for row in value) + "}"
    if kind in ("charmatrix", "strmatrix"):
        return "vector<vector<string>>{" + ", ".join(
            "{" + ", ".join(_c_quote(cell, "cpp") for cell in row) + "}"
            for row in value) + "}"
    if kind in ("strarray", "stri"):
        return _braced("vector<string>", [_c_quote(v, "cpp") for v in value])
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _c_quote(value, "cpp")
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        if value and isinstance(value[0], str):
            return "{" + ", ".join(_c_quote(v, "cpp") for v in value) + "}"
        return "{" + ", ".join(_cpp_literal(v) for v in value) + "}"
    raise RunError("interface", f"cannot pass {type(value).__name__} to C++")


def _braced(type_name: str, items: List[str]) -> str:
    """`vector<string>{ "a", "b" }`, and `vector<string>{}` when there are none."""
    return type_name + "{" + ", ".join(items) + "}"


def _cs_literal(value: Any, kind: str = "array") -> str:
    if kind == "tree":
        return _cs_new("int?[]", ["null" if v is None else repr(v) for v in value])
    if kind in ("matrix", "graph"):
        return "new int[][] { " + ", ".join(
            _cs_new("int[]", [str(cell) for cell in row]) for row in value) + " }"
    if kind in ("charmatrix", "strmatrix"):
        return "new string[][] { " + ", ".join(
            _cs_new("string[]", [_c_quote(cell, "csharp") for cell in row])
            for row in value) + " }"
    if kind in ("strarray", "stri"):
        return _cs_new("string[]", [_c_quote(v, "csharp") for v in value])
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _c_quote(value, "csharp")
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        if value and isinstance(value[0], str):
            return "new string[] { " + ", ".join(_c_quote(v, "csharp") for v in value) + " }"
        return "new int[] { " + ", ".join(_cs_literal(v) for v in value) + " }"
    raise RunError("interface", f"cannot pass {type(value).__name__} to C#")


def _cs_new(type_name: str, items: List[str]) -> str:
    """C# will not write an empty array literal, so an empty one is spelled out."""
    if not items:
        return f"new {type_name.replace('[]', '[0]')}"
    return f"new {type_name} {{ " + ", ".join(items) + " }"


def _java_literal(value: Any, kind: str = "array") -> str:
    if kind == "tree":
        return _java_new("Integer[]", ["null" if v is None else repr(v) for v in value])
    if kind in ("matrix", "graph"):
        return "new int[][] { " + ", ".join(
            _java_new("int[]", [str(cell) for cell in row]) for row in value) + " }"
    if kind in ("charmatrix", "strmatrix"):
        return "new String[][] { " + ", ".join(
            _java_new("String[]", [_c_quote(cell, "java") for cell in row])
            for row in value) + " }"
    if kind in ("strarray", "stri"):
        return _java_new("String[]", [_c_quote(v, "java") for v in value])
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _c_quote(value, "java")
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        if value and isinstance(value[0], str):
            return "new String[] { " + ", ".join(_c_quote(v, "java") for v in value) + " }"
        return "new int[] { " + ", ".join(_java_literal(v) for v in value) + " }"
    raise RunError("interface", f"cannot pass {type(value).__name__} to Java")


def _java_new(type_name: str, items: List[str]) -> str:
    if not items:
        return f"new {type_name.replace('[]', '[0]')}"
    return f"new {type_name} {{ " + ", ".join(items) + " }"


def _rust_literal(value: Any, kind: str = "array") -> str:
    """Render one argument as a Rust expression of the type its contract names.

    An empty list is left as a bare `Vec::new()`. A turbofish pins the element
    type, and an empty list carries no evidence about that type, so the
    parameter is the only thing that can settle it.
    """
    if kind == "tree":
        return _rust_vec(["None" if v is None else f"Some({_rust_literal(v)})"
                          for v in value])
    if kind in ("matrix", "graph"):
        return _rust_vec([_rust_vec([_rust_literal(cell) for cell in row])
                          for row in value])
    if kind in ("charmatrix", "strmatrix"):
        return _rust_vec([_rust_vec([f"{_rust_quote(cell)}.to_string()" for cell in row])
                          for row in value])
    if kind in ("strarray", "stri"):
        return _rust_vec([f"{_rust_quote(v)}.to_string()" for v in value])
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _rust_quote(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, int):
        return f"{value}i64"
    if isinstance(value, (list, tuple)):
        if not value:
            return "Vec::new()"
        if isinstance(value[0], str):
            return _rust_vec([f"{_rust_quote(v)}.to_string()" for v in value])
        return _rust_vec([_rust_literal(v) for v in value])
    raise RunError("interface", f"cannot pass {type(value).__name__} to Rust")


def _rust_vec(items: List[str]) -> str:
    """`vec![1i64, 2i64]`, and an untyped `Vec::new()` when there are no items.

    The empty form is deliberate: `vec![]` has no element type either, but
    `Vec::new()` at least says a collection is expected, and the parameter
    supplies the rest. Three questions in the dataset pass an empty list.
    """
    if not items:
        return "Vec::new()"
    return "vec![" + ", ".join(items) + "]"


def _rust_quote(text: str) -> str:
    """Quote a Rust string literal, leaving UTF-8 intact.

    Rust's own Debug formatting would work, but it escapes every non-ASCII
    character into a `\\u{...}` escape, which turns "Ünïcödé" into noise in a
    file the user is meant to read. Only the characters that would end the
    literal or break the line are escaped.
    """
    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


def _c_quote(text: str, lang: str) -> str:
    """Quote a string for C++, C# or Java.

    C++ gets a raw string literal so that backslashes in the input survive
    intact; Word Count and similar questions pass regex-ish test data, and
    mangling it would make the harness lie about the argument. C# and Java have
    no raw literal, so they get conventional escaping.
    """
    if lang == "cpp" and "#" not in text and '"' not in text:
        return f'R"({text})"'
    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'


# --------------------------------------------------------------------------
# Type helpers
# --------------------------------------------------------------------------

# Each contract type rendered as a language type. The structural types are
# listed explicitly rather than derived from `array`, because the language
# types genuinely differ: a tree needs a null in every language, and there is
# no way to spell that by extending a table entry.
_CPP_RETURN = {"string": "string", "int": "int", "float": "double", "bool": "bool",
               "array": "vector<int>", "list": "vector<int>",
               "tree": "vector<optional<int>>",
               "matrix": "vector<vector<int>>", "graph": "vector<vector<int>>",
               "charmatrix": "vector<vector<string>>",
               "strmatrix": "vector<vector<string>>", "strarray": "vector<string>"}
_CPP_ARG = dict(_CPP_RETURN, stri="vector<string>")
_CS_RETURN = {"string": "string", "int": "int", "float": "double", "bool": "bool",
              "array": "int[]", "list": "int[]", "tree": "int?[]",
              "matrix": "int[][]", "graph": "int[][]", "charmatrix": "string[][]",
              "strmatrix": "string[][]", "strarray": "string[]"}
_CS_ARG = dict(_CS_RETURN, stri="string[]")
_JAVA_RETURN = {"string": "String", "int": "int", "float": "double", "bool": "boolean",
                "array": "int[]", "list": "int[]", "tree": "Integer[]",
                "matrix": "int[][]", "graph": "int[][]", "charmatrix": "String[][]",
                "strmatrix": "String[][]", "strarray": "String[]"}
_JAVA_ARG = dict(_JAVA_RETURN, stri="String[]")
_RUST_RETURN = {"string": "String", "int": "i64", "float": "f64", "bool": "bool",
                "array": "Vec<i64>", "list": "Vec<i64>", "tree": "Vec<Option<i64>>",
                "matrix": "Vec<Vec<i64>>", "graph": "Vec<Vec<i64>>",
                "charmatrix": "Vec<Vec<String>>", "strmatrix": "Vec<Vec<String>>",
                "strarray": "Vec<String>"}
_RUST_ARG = dict(_RUST_RETURN, string="&str", stri="Vec<String>")


def _contract_type(question: dict) -> str:
    """The question's return contract in Coderbyte terms (not a language type)."""
    for case in question["cases"]:
        if case["expectedType"] in RETURN_TYPES:
            return case["expectedType"]
    raise RunError("interface", f"no supported return type for {question['id']}")


def effective_arg_types(question: dict) -> List[str]:
    """Resolve each argument's contract type, pinning down the ambiguous one.

    The dataset records `array` for every plain list argument, which is
    ambiguous: Array Matching takes a string array while Simple Adding takes an
    int array. The structural types are not ambiguous -- a `tree` is a tree
    whatever it holds -- so the declared name is taken as it stands and only
    `array` is resolved from the first test case. The generated harness needs
    the resolved list to write the literals, and the browser needs it to write
    a starter signature that compiles.
    """
    declared = question["signature"]["argTypes"]
    first = question["cases"][0]["args"]
    kinds = []
    for index, name in enumerate(declared):
        if name != "array":
            kinds.append(name)
            continue
        value = first[index] if index < len(first) else []
        element = value[0] if isinstance(value, (list, tuple)) and value else 0
        kinds.append("stri" if isinstance(element, str) else "array")
    return kinds


def _return_type(question: dict, table: dict) -> str:
    """Pick the return type from the first case's expected type."""
    for case in question["cases"]:
        if case["expectedType"] in table:
            return table[case["expectedType"]]
    raise RunError("interface", f"no supported return type for {question['id']}")


def _is_list_contract(kind: str) -> bool:
    return kind in LIST_TYPES


def _is_polymorphic(question: dict) -> bool:
    """True when the cases disagree on return type.

    A handful of Coderbyte questions (Arith Geo II is the canonical one) return
    an int -1 for the "no match" case and a string otherwise. A statically typed
    function cannot do that, so those questions use a variant/object return and
    the harness decides the type tag at runtime.
    """
    return bool(question.get("polymorphic"))


# --------------------------------------------------------------------------
# Envelope emission
# --------------------------------------------------------------------------

# The language type of each structural return, in every language that has one.
# The dispatch below goes on the rendered type rather than the contract name
# because that is what the generated code declares the variable as -- `int[]`
# is a linked list on one question and a plain array on the next, and the
# harness cannot tell them apart after the fact.
_TREE_TYPES = {"vector<optional<int>>", "int?[]", "Integer[]", "Vec<Option<i64>>"}
_ROWS_TYPES = {"vector<vector<int>>", "int[][]", "Vec<Vec<i64>>"}
# Both the C# and the Java spelling of a string matrix, because Java uppercases
# its array types and the dispatch below is shared. Listing only one of them
# silently routes the other to the scalar string emitter, which produces a
# compile error rather than a wrong answer -- so the probe suite is what
# catches a gap here, not a practice question.
_CHAR_ROWS_TYPES = {"vector<vector<string>>", "string[][]", "String[][]",
                    "Vec<Vec<String>>"}
_WORDS_TYPES = {"vector<string>", "string[]", "String[]", "Vec<String>"}


def _emit_statement(lang: str, var: str, result_type: str, tag: str) -> str:
    """Return a statement printing one tagged JSON envelope for `var`.

    `tag` is the contract the question asked for, so the envelope records what
    was wanted rather than the generic JSON shape it arrived as.
    """
    if lang == "rust":
        return _emit_statement_rust(var, result_type, tag)
    emit = "Emitter.Emit" if lang == "csharp" else "__emit"
    if result_type in ("int", "long", "Integer"):
        return f'{emit}("int", {var});'
    if result_type in ("double", "float", "Double"):
        return f'{emit}("float", {var});'
    if result_type in ("bool", "boolean", "Boolean"):
        return f'{emit}("bool", {var});'
    if result_type in _TREE_TYPES:
        return f'{emit}Tree("{tag}", {var});'
    if result_type in _ROWS_TYPES:
        return f'{emit}Rows("{tag}", {var});'
    if result_type in _CHAR_ROWS_TYPES:
        return f'{emit}WordRows("{tag}", {var});'
    if result_type in _WORDS_TYPES:
        return f'{emit}Words("{tag}", {var});'
    if result_type in ("vector<int>", "int[]"):
        # Arrays need a loop to serialise element by element.
        return _emit_array(lang, emit, var, tag)
    return f'{emit}("string", {var});'


def _emit_statement_rust(var: str, result_type: str, tag: str) -> str:
    """Rust does not overload, so each envelope kind gets its own function."""
    if result_type == "i64":
        return f'__emit_int("int", {var});'
    if result_type == "f64":
        return f'__emit_float("float", {var});'
    if result_type == "bool":
        return f'__emit_bool("bool", {var});'
    if result_type in _TREE_TYPES:
        return f'__emit_tree("{tag}", &{var});'
    if result_type in _ROWS_TYPES:
        return f'__emit_rows("{tag}", &{var});'
    if result_type in _CHAR_ROWS_TYPES:
        return f'__emit_word_rows("{tag}", &{var});'
    if result_type in _WORDS_TYPES:
        return f'__emit_words("{tag}", &{var});'
    if result_type == "Vec<i64>":
        return f'__emit_array("{tag}", &{var});'
    return f'__emit("string", &{var});'


def _emit_array(lang: str, emit: str, var: str, tag: str) -> str:
    if lang == "cpp":
        return (f'cout << "{{\\"t\\":\\"{tag}\\",\\"v\\":[" << std::flush; for (size_t _i = 0; _i < {var}.size(); ++_i)'
                f' {{ if (_i) cout << ","; cout << {var}[_i]; }} cout << "]}}" << endl;')
    if lang == "csharp":
        return (f'Console.WriteLine("{{\\"t\\":\\"{tag}\\",\\"v\\":[" + '
                f'string.Join(",", {var}.Select(v => v.ToString())) + "]}}");')
    return (f'System.out.println("{{\\"t\\":\\"{tag}\\",\\"v\\":[" + '
            f'java.util.Arrays.stream({var}).mapToObj(String::valueOf)'
            f'.collect(java.util.stream.Collectors.joining(",")) + "]}}");')



def _emit_definition(lang: str) -> str:
    if lang == "cpp":
        return """static string __json(const string& s);
static void __emit(const string& t, const string& v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":\\"" << __json(v) << "\\"}" << endl;
}
static void __emit(const char* t, int v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":" << v << "}" << endl;
}
static void __emit(const char* t, long long v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":" << v << "}" << endl;
}
static void __emit(const char* t, double v) {
  ostringstream _o; _o << setprecision(17) << v; string _s = _o.str();
  if (_s.find('.') == string::npos && _s.find('e') == string::npos &&
      _s.find("inf") == string::npos && _s.find("nan") == string::npos) _s += ".0";
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":" << _s << "}" << endl;
}
static void __emit(const char* t, bool v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":" << (v ? "true" : "false") << "}" << endl;
}
template <typename T>
static void __emitRows(const char* t, const vector<vector<T>>& v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":[";
  for (size_t i = 0; i < v.size(); ++i) {
    if (i) cout << ",";
    cout << "[";
    for (size_t j = 0; j < v[i].size(); ++j) { if (j) cout << ","; cout << v[i][j]; }
    cout << "]";
  }
  cout << "]}" << endl;
}
static void __emitTree(const char* t, const vector<optional<int>>& v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":[";
  for (size_t i = 0; i < v.size(); ++i) {
    if (i) cout << ",";
    if (v[i].has_value()) cout << *v[i]; else cout << "null";
  }
  cout << "]}" << endl;
}
static void __emitWordRows(const char* t, const vector<vector<string>>& v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":[";
  for (size_t i = 0; i < v.size(); ++i) {
    if (i) cout << ",";
    cout << "[";
    for (size_t j = 0; j < v[i].size(); ++j) {
      if (j) cout << ",";
      cout << '"' << __json(v[i][j]) << '"';
    }
    cout << "]";
  }
  cout << "]}" << endl;
}
static void __emitWords(const char* t, const vector<string>& v) {
  cout << "{\\"t\\":\\"" << t << "\\",\\"v\\":[";
  for (size_t i = 0; i < v.size(); ++i) { if (i) cout << ","; cout << '"' << __json(v[i]) << '"'; }
  cout << "]}" << endl;
}
static string __json(const string& s) {
  string out;
  for (char c : s) {
    if (c == 34 || c == 92) out.push_back(92);
    out.push_back(c);
  }
  return out;
}
"""
    if lang == "csharp":
        return """static void __emit(string t, string v) {
  Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":\\"" + Json(v) + "\\"}");
}
static void __emit(string t, int v) {
  Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":" + v + "}");
}
static void __emit(string t, double v) {
  string _s = v.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
  if (_s.IndexOf('.') < 0 && _s.IndexOf('E') < 0 &&
      _s.IndexOf("Infinity") < 0 && _s.IndexOf("NaN") < 0) _s += ".0";
  Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":" + _s + "}");
}
static void __emit(string t, bool v) {
  Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":" + (v ? "true" : "false") + "}");
}
  public static void EmitTree(string t, int?[] v) {
    Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":[" +
      string.Join(",", v.Select(x => x.HasValue ? x.Value.ToString() : "null")) + "]}");
  }
  public static void EmitRows(string t, int[][] v) {
    Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":[" +
      string.Join(",", v.Select(row => "[" + string.Join(",", row) + "]")) + "]}");
  }
  public static void EmitWordRows(string t, string[][] v)
  {
    // A StringBuilder rather than nested LINQ: C# will not parse a cast as the
    // first token of a lambda body that is itself an argument to another call,
    // so `(char)34 + Json(x) + (char)34` inside a nested Select does not build.
    var sb = new System.Text.StringBuilder();
    for (int i = 0; i < v.Length; i++)
    {
      if (i > 0) sb.Append(",");
      sb.Append("[");
      for (int j = 0; j < v[i].Length; j++)
      {
        if (j > 0) sb.Append(",");
        sb.Append((char)34).Append(Json(v[i][j])).Append((char)34);
      }
      sb.Append("]");
    }
    Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":[" + sb + "]}");
  }
  public static void EmitWords(string t, string[] v) {
    Console.WriteLine("{\\"t\\":\\"" + t + "\\",\\"v\\":[" +
      string.Join(",", v.Select(x => (char)34 + Json(x) + (char)34)) + "]}");
  }
  static string Json(string s) {
    var escaped = new System.Text.StringBuilder();
    foreach (char c in s) {
      if (c == 34 || c == 92) escaped.Append((char)92);
      escaped.Append(c);
    }
    return escaped.ToString();
  }
"""
    if lang == "rust":
        return r'''fn __esc(s: &str) -> String {
    let mut out = String::new();
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out
}
fn __emit(t: &str, v: &str) {
    println!("{{\"t\":\"{}\",\"v\":\"{}\"}}", t, __esc(v));
}
fn __emit_int(t: &str, v: i64) {
    println!("{{\"t\":\"{}\",\"v\":{}}}", t, v);
}
fn __emit_float(t: &str, v: f64) {
    if v.is_nan() {
        println!("{{\"t\":\"float\",\"v\":NaN}}");
    } else if v.is_infinite() {
        println!("{{\"t\":\"float\",\"v\":{}}}", if v > 0.0 { "Infinity" } else { "-Infinity" });
    } else {
        let s = format!("{}", v);
        // Rust prints 1.0 as "1", which would come back as an int.
        let s = if s.contains('.') || s.contains('e') { s } else { s + ".0" };
        println!("{{\"t\":\"float\",\"v\":{}}}", s);
    }
}
fn __emit_bool(t: &str, v: bool) {
    println!("{{\"t\":\"{}\",\"v\":{}}}", t, v);
}
fn __emit_array(t: &str, v: &[i64]) {
    let parts: Vec<String> = v.iter().map(|x| x.to_string()).collect();
    println!("{{\"t\":\"{}\",\"v\":[{}]}}", t, parts.join(","));
}
fn __emit_tree(t: &str, v: &[Option<i64>]) {
    let parts: Vec<String> = v.iter()
        .map(|x| match x { Some(n) => n.to_string(), None => "null".to_string() })
        .collect();
    println!("{{\"t\":\"{}\",\"v\":[{}]}}", t, parts.join(","));
}
fn __emit_rows<T: std::fmt::Display>(t: &str, v: &[Vec<T>]) {
    let rows: Vec<String> = v.iter().map(|row| {
        let cells: Vec<String> = row.iter().map(|c| c.to_string()).collect();
        format!("[{}]", cells.join(","))
    }).collect();
    println!("{{\"t\":\"{}\",\"v\":[{}]}}", t, rows.join(","));
}
fn __emit_word_rows(t: &str, v: &[Vec<String>]) {
let quote = char::from(34);
    let rows: Vec<String> = v.iter().map(|row| {
        let cells: Vec<String> = row.iter()
            .map(|c| format!("{quote}{}{quote}", __esc(c)))
            .collect();
        format!("[{}]", cells.join(","))
    }).collect();
    println!("{{\"t\":\"{}\",\"v\":[{}]}}", t, rows.join(","));
}
fn __emit_words(t: &str, v: &[String]) {
let quote = char::from(34);
    let parts: Vec<String> = v.iter().map(|x| format!("{quote}{}{quote}", __esc(x))).collect();
    println!("{{\"t\":\"{}\",\"v\":[{}]}}", t, parts.join(","));
}
'''
    if lang == "java":
        return """static void __emit(String t, String v) {
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":\\"" + v.replace("\\\\", "\\\\\\\\").replace("\\"", "\\\\\\"") + "\\"}");
}
static void __emit(String t, int v) {
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":" + v + "}");
}
static void __emit(String t, double v) {
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":" + v + "}");
}
static void __emit(String t, boolean v) {
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":" + v + "}");
}
static void __emitTree(String t, Integer[] v) {
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":[" +
    java.util.Arrays.stream(v).map(x -> x == null ? "null" : x.toString())
      .collect(java.util.stream.Collectors.joining(",")) + "]}");
}
static void __emitRows(String t, int[][] v) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length; i++) {
    if (i > 0) sb.append(",");
    sb.append("[");
    for (int j = 0; j < v[i].length; j++) { if (j > 0) sb.append(","); sb.append(v[i][j]); }
    sb.append("]");
  }
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":[" + sb + "]}");
}
static void __emitWordRows(String t, String[][] v) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length; i++) {
    if (i > 0) sb.append(",");
    sb.append("[");
    for (int j = 0; j < v[i].length; j++) {
      if (j > 0) sb.append(",");
      sb.append((char) 34).append(json(v[i][j])).append((char) 34);
    }
    sb.append("]");
  }
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":[" + sb + "]}");
}
static void __emitWords(String t, String[] v) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length; i++) {
    if (i > 0) sb.append(",");
    sb.append((char) 34).append(json(v[i])).append((char) 34);
  }
  System.out.println("{\\"t\\":\\"" + t + "\\",\\"v\\":[" + sb + "]}");
}
static String json(String s) {
  StringBuilder escaped = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == 34 || c == 92) escaped.append((char) 92);
    escaped.append(c);
  }
  return escaped.toString();
}
"""
    return ""


def _poly_emitter(lang: str) -> str:
    """Serialise a variant/object return whose runtime type decides the tag.

    Polymorphic questions return different types per case, so the harness has to
    pick the JSON type tag from the value itself rather than the contract.
    """
    if lang == "cpp":
        return """static void __emitObj(const CBResult& r) {
  if (std::holds_alternative<string>(r)) {
    cout << "{\\"t\\":\\"string\\",\\"v\\":\\"" << std::get<string>(r) << "\\"}" << endl;
  } else if (std::holds_alternative<int>(r)) {
    cout << "{\\"t\\":\\"int\\",\\"v\\":" << std::get<int>(r) << "}" << endl;
  } else {
    const auto& a = std::get<vector<int>>(r);
    cout << "{\\"t\\":\\"array\\",\\"v\\":[";
    for (size_t i = 0; i < a.size(); i++) { if (i) cout << ","; cout << a[i]; }
    cout << "]}" << endl;
  }
}
"""
    if lang == "csharp":
        return """  public static void EmitObj(object r) {
    if (r is int) Console.WriteLine("{\\"t\\":\\"int\\",\\"v\\":" + r + "}");
    else if (r is bool) Console.WriteLine("{\\"t\\":\\"bool\\",\\"v\\":" + ((bool)r ? "true" : "false") + "}");
    else if (r is int[]) Console.WriteLine("{\\"t\\":\\"array\\",\\"v\\":[" +
        string.Join(",", ((int[])r).Select(v => v.ToString())) + "]}");
    else Console.WriteLine("{\\"t\\":\\"string\\",\\"v\\":\\"" + r + "\\"}");
  }
"""
    if lang == "rust":
        return r'''
enum CBResult { Int(i64), Str(String), Arr(Vec<i64>), Bool(bool) }

fn __emit_obj(r: CBResult) {
    match r {
        CBResult::Int(v) => __emit_int("int", v),
        CBResult::Str(v) => __emit("string", &v),
        CBResult::Arr(v) => __emit_array("array", &v),
        CBResult::Bool(v) => __emit_bool("bool", v),
    }
}
'''
    return """  static void __emitObj(Object r) {
    if (r instanceof Integer) System.out.println("{\\"t\\":\\"int\\",\\"v\\":" + r + "}");
    else if (r instanceof Boolean) System.out.println("{\\"t\\":\\"bool\\",\\"v\\":" + r + "}");
    else if (r instanceof int[]) System.out.println("{\\"t\\":\\"array\\",\\"v\\":[" +
        java.util.Arrays.stream((int[]) r).mapToObj(String::valueOf)
        .collect(java.util.stream.Collectors.joining(",")) + "]}");
    else System.out.println("{\\"t\\":\\"string\\",\\"v\\":\\"" + r + "\\"}");
  }
"""


# --------------------------------------------------------------------------
# Harness builders
# --------------------------------------------------------------------------

def _build_cpp(question: dict, source: str) -> str:
    poly = _is_polymorphic(question)
    contract = _contract_type(question)
    ret = "CBResult" if poly else _CPP_RETURN[contract]
    kinds = effective_arg_types(question)
    # The standard library a Coderbyte answer reaches for. It is listed up
    # front rather than per question because a submission cannot add an
    # include of its own -- the file is assembled, not written by the user.
    includes = ("#include <iostream>\n#include <string>\n#include <vector>\n"
               "#include <set>\n#include <map>\n#include <queue>\n#include <stack>\n"
               "#include <sstream>\n#include <iomanip>\n"
               "#include <algorithm>\n")
    if "tree" in kinds or contract == "tree":
        # A tree is a vector of optionals, and optional is not in the headers
        # the plain array questions already pull in.
        includes += "#include <optional>\n"
    if poly:
        includes += "#include <variant>\n"
    includes += "using namespace std;\n"

    preamble = ""
    if poly:
        preamble = """
// A polymorphic Coderbyte question returns a different type depending on the
// input, so the answer travels in a variant.
using CBResult = std::variant<string, int, vector<int>>;

""" + _poly_emitter("cpp")

    lines = [includes, preamble, _emit_definition("cpp"), "\n// ---- user code ----\n",
             source, "\n// ---- end user code ----\n", "\nint main() {\n"]
    for case in question["cases"]:
        args = ", ".join(_cpp_literal(a, k) for a, k in zip(case["args"], kinds))
        call = f"{question['functionName']}({args})"
        if poly:
            lines.append(f"  {{ CBResult r = {call}; __emitObj(r); }}\n")
        else:
            lines.append(f"  {{ {ret} r = {call}; {_emit_statement('cpp', 'r', ret, contract)} }}\n")
    lines.append("  return 0;\n}\n")
    return "".join(lines)


def _split_usings(source: str) -> tuple:
    """Normalise a C# submission: hoist usings, rename the class.

    Two C#-specific problems are solved here:

    1. Every `using` must precede all type declarations, so leading using
       directives are hoisted to the top of the generated file.
    2. `dotnet run file.cs` reserves the name `Program` for the implicit entry
       point, so a user class called `Program` collides with it. It is renamed
       to `Solution` to match the Java convention.
    """
    import re

    usings = []
    body = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("using ") and stripped.endswith(";") and "=" not in stripped:
            usings.append(stripped)
        else:
            body.append(line)

    text = "\n".join(body)
    # Rename the user's class, but not a namespace-qualified reference to one.
    text = re.sub(r"\bclass\s+Program\b", "class Solution", text)
    text = re.sub(r"\bProgram\s*\.", "Solution.", text)
    text = re.sub(r"\bstatic\s+Program\s+(\w+)\s*\(", r"static Solution \1(", text)
    return usings, text


def _build_csharp(question: dict, source: str) -> str:
    poly = _is_polymorphic(question)
    contract = _contract_type(question)
    ret = "object" if poly else _CS_RETURN[contract]
    kinds = effective_arg_types(question)
    user_usings, user_body = _split_usings(source)

    usings = ["using System;", "using System.Linq;", "using System.Collections.Generic;"]
    for using in user_usings:
        if using not in usings:
            usings.append(using)

    # `dotnet run file.cs` compiles the file as top-level statements. Two rules
    # bite here: top-level statements must precede all type declarations, and
    # top-level local functions cannot be overloaded. So the run-cases block
    # goes first, and the overloaded emitters live in a static class declared
    # after it (C# allows a type to be referenced before its declaration).
    lines = ["\n".join(usings) + "\n", "\n// ---- run cases ----\n"]
    for case in question["cases"]:
        # The user's class is renamed to `Solution` (see `_split_usings`).
        args = ", ".join(_cs_literal(a, k) for a, k in zip(case["args"], kinds))
        call = f"Solution.{question['functionName']}({args})"
        if poly:
            lines.append(f"{{ object r = {call}; Emitter.EmitObj(r); }}\n")
        else:
            lines.append(f"{{ {ret} r = {call}; {_emit_statement('csharp', 'r', ret, contract)} }}\n")

    lines.append("\n// ---- harness helpers ----\n")
    lines.append("static class Emitter {\n")
    lines.append(_emit_definition("csharp").replace("static void __emit", "  public static void Emit"))
    if poly:
        lines.append(_poly_emitter("csharp"))
    lines.append("}\n")
    lines.append("\n// ---- user code ----\n")
    lines.append(user_body)
    lines.append("\n// ---- end user code ----\n")
    return "".join(lines)


def _build_java(question: dict, source: str) -> str:
    poly = _is_polymorphic(question)
    contract = _contract_type(question)
    ret = "Object" if poly else _JAVA_RETURN[contract]
    kinds = effective_arg_types(question)
    arg_types = question["signature"]["argTypes"]
    preamble = _poly_emitter("java") if poly else ""
    lines = [source, "\npublic class Main {\n", preamble, _emit_definition("java"),
             "  public static void main(String[] args) {\n"]
    for case in question["cases"]:
        args = ", ".join(_java_literal(a, k) for a, k in zip(case["args"], kinds))
        call = f"Solution.{_java_method(question['functionName'], arg_types)}({args})"
        if poly:
            lines.append(f"    {{ Object r = {call}; __emitObj(r); }}\n")
        else:
            lines.append(f"    {{ {ret} r = {call}; {_emit_statement('java', 'r', ret, contract)} }}\n")
    lines.append("  }\n}\n")
    return "".join(lines)


def _rust_method(function_name: str) -> str:
    """Map a Coderbyte PascalCase function name onto Rust's snake_case.

    The acronym rule matters here: `ABCheck` is `ab_check`, not `a_b_check`,
    and `ExOh` is `ex_oh`. An underscore goes before an uppercase letter that
    follows a lowercase letter or a digit, or that starts a new word inside a
    run of capitals.
    """
    out = []
    for index, char in enumerate(function_name):
        if char.isupper() and index:
            previous = function_name[index - 1]
            following = function_name[index + 1:index + 2]
            if previous.islower() or previous.isdigit() or (previous.isupper() and following.islower()):
                out.append("_")
        out.append(char.lower())
    return "".join(out)


def _split_rust_struct(source: str) -> str:
    """Drop a user-written `struct Solution` declaration.

    Rust is order-independent, so the generated file can put the user's code
    first and every helper after it -- which means the compiler's line numbers
    point at the line the user actually typed. That only works if the harness
    owns `struct Solution`, and the LeetCode template makes people write it
    anyway, so it is removed rather than left to collide.
    """
    import re

    return re.sub(r"^\s*(?:pub\s+)?struct\s+Solution\s*(?:;|\{\s*\})\s*$", "", source, flags=re.MULTILINE)


def _build_rust(question: dict, source: str) -> str:
    """Assemble a self-contained Rust program that runs every test case.

    The user's code goes in first, byte for byte, so a compiler error on line
    12 means line 12 of what they wrote. Everything the harness needs is
    declared after it; Rust does not care about declaration order.
    """
    poly = _is_polymorphic(question)
    contract = _contract_type(question)
    ret = "CBResult" if poly else _RUST_RETURN[contract]
    kinds = effective_arg_types(question)
    method = _rust_method(question["functionName"])

    lines = [_split_rust_struct(source),
             "\n\n// ---- generated harness ----\n",
             "// The LeetCode template omits this and lets the judge supply it.\n"
             "struct Solution;\n",
             _emit_definition("rust")]
    if poly:
        lines.append(_poly_emitter("rust"))
    lines.append("\nfn main() {\n")
    for case in question["cases"]:
        args = ", ".join(_rust_literal(a, k) for a, k in zip(case["args"], kinds))
        call = f"Solution::{method}({args})"
        if poly:
            lines.append(f"    let r: CBResult = {call}; __emit_obj(r);\n")
        else:
            lines.append(f"    let r = {call}; {_emit_statement('rust', 'r', ret, contract)}\n")
    lines.append("}\n")
    return "".join(lines)


def _java_method(function_name: str, arg_types: List[str]) -> str:
    """Map a Coderbyte function name to the Java solution's method name.

    Java methods are camelCase, so the Coderbyte PascalCase name simply loses
    its leading capital. The bundled reference solutions follow the same rule,
    which is why a hardcoded table is unnecessary and would only go stale.
    """
    return function_name[:1].lower() + function_name[1:]


# --------------------------------------------------------------------------
# Envelope collection
# --------------------------------------------------------------------------

def _collect(stdout: str) -> List[Any]:
    """Take the envelopes out of the program's output, ignoring everything else.

    Only a well-formed envelope counts as a result, and that is load-bearing
    rather than tidy. The toolchain writes to the same stream: `dotnet run`
    prints compiler warnings to stdout ahead of the program's own output, so a
    nullable warning on the C# side used to be read as the first case's return
    value and pushed every later case one slot out of alignment. A submission
    can print whatever it likes for the same reason. Diagnostics that do matter
    -- compile errors, a crash -- already arrive on stderr with a non-zero
    exit status, so nothing is lost by ignoring noise here.
    """
    results = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            envelope = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(envelope, dict) and "t" in envelope and "v" in envelope:
            results.append(envelope["v"])
    return results


def _clean(text: str) -> str:
    """Trim compiler/runtime noise down to what the user needs to act on."""
    import re

    lines = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        if line.strip().startswith("at "):
            continue
        # rustc's trailer repeats what the error above already said, and the
        # output budget is twelve lines, so it is not worth spending two on it.
        if line.startswith("error: aborting due to") or line.startswith("For more information about this error"):
            continue
        # Strip the temp working directory so paths do not leak into the UI.
        line = re.sub(r"(/(?:private/)?(?:var|Users|tmp)/[^\s:]*?/cbp_[a-z]+_[A-Za-z0-9_]+)/", "", line)
        line = re.sub(r"\bcbp_[a-z]+_[A-Za-z0-9_]+/", "", line)
        lines.append(line)
    return "\n".join(lines[:12]) or "your code failed with no output"


# --------------------------------------------------------------------------
# Adapters
# --------------------------------------------------------------------------

class Adapter:
    language = ""
    filename = ""

    def run(self, question: dict, source: str) -> List[Any]:
        raise NotImplementedError

    def _exec(self, command: List[str], cwd: str, language: str,
              timeout: int = TIMEOUT_SECONDS) -> str:
        try:
            proc = subprocess.run(command, cwd=cwd, capture_output=True,
                                  text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise RunError(
                "timeout",
                f"your code ran longer than {timeout}s -- is there an infinite loop?",
                language,
            )
        if proc.returncode != 0:
            raise RunError("runtime", _clean(proc.stderr or proc.stdout), language)
        return proc.stdout


class PythonAdapter(Adapter):
    language = "python"
    filename = "main.py"

    WIRE = """import json as _json

def __wire(v):
    if isinstance(v, bool):
        t = "bool"
    elif isinstance(v, int):
        t = "int"
    elif isinstance(v, float):
        t = "float"
    elif isinstance(v, str):
        t = "string"
    elif isinstance(v, (list, tuple)):
        t = "array"
    else:
        t = type(v).__name__
    return _json.dumps({"t": t, "v": v})
"""

    def run(self, question: dict, source: str) -> List[Any]:
        lines = [self.WIRE, "\n", source, "\n"]
        for case in question["cases"]:
            call = f"{question['functionName']}({', '.join(_py_literal(a) for a in case['args'])})"
            lines.append(f"print(__wire({call}))\n")

        directory = tempfile.mkdtemp(prefix="cbp_python_")
        with open(os.path.join(directory, self.filename), "w") as fh:
            fh.write("".join(lines))
        return _collect(self._exec([sys.executable, self.filename], directory, "python"))


class CppAdapter(Adapter):
    language = "cpp"
    filename = "Solution.cpp"

    def run(self, question: dict, source: str) -> List[Any]:
        directory = tempfile.mkdtemp(prefix="cbp_cpp_")
        path = os.path.join(directory, self.filename)
        with open(path, "w") as fh:
            fh.write(_build_cpp(question, source))

        # Windows needs a different compiler driver, a different standard
        # flag and a different way of naming the output binary. clang-cl is
        # the right driver there rather than clang++: it speaks MSVC's
        # command line and links against the same standard library Visual
        # Studio ships, so a C++17 source that works on the Mac works here
        # without a second standard library. clang-cl also requires /std:c++17
        # and produces .obj and .pdb noise next to the source unless told
        # otherwise, hence /nologo.
        if sys.platform == "win32":
            binary = os.path.join(directory, "out.exe")
            command = [
                _require("clang-cl", "cpp"),
                "/nologo", "/std:c++17", "/O0", "/W3", "/EHsc",
                f"/Fe:{binary}", path,
            ]
        else:
            binary = os.path.join(directory, "out")
            command = [
                _require("clang++", "cpp"),
                "-std=c++17", "-O0", "-o", binary, path,
            ]

        try:
            proc = subprocess.run(
                command,
                capture_output=True, text=True, timeout=COMPILE_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            raise RunError("timeout", "compilation took too long", "cpp")
        if proc.returncode != 0:
            raise RunError("compile", _clean(proc.stderr), "cpp")
        return _collect(self._exec([binary], directory, "cpp"))


class CSharpAdapter(Adapter):
    language = "csharp"
    filename = "Harness.cs"

    def run(self, question: dict, source: str) -> List[Any]:
        directory = tempfile.mkdtemp(prefix="cbp_cs_")
        path = os.path.join(directory, self.filename)
        with open(path, "w") as fh:
            fh.write(_build_csharp(question, source))
        try:
            proc = subprocess.run(
                [_require("dotnet", "csharp"), "run", self.filename],
                cwd=directory, capture_output=True, text=True,
                timeout=COMPILE_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            raise RunError("timeout", "C# build took too long", "csharp")
        if proc.returncode != 0:
            # dotnet writes the real compiler errors to stdout, not stderr.
            raise RunError("compile", _clean(proc.stdout + "\n" + proc.stderr), "csharp")
        return _collect(proc.stdout)


class JavaAdapter(Adapter):
    language = "java"
    filename = "Main.java"

    @staticmethod
    def _demote_public(source: str) -> str:
        """Drop `public` from top-level class declarations.

        Java requires a public class to live in a file named after it, but the
        user's code is compiled inside Main.java. Removing the modifier is
        harmless -- the class is still package-visible, which is all the
        generated harness needs.
        """
        import re

        return re.sub(r"^(\s*)public\s+(class|final\s+class|abstract\s+class)\s",
                      r"\1\2 ", source, flags=re.MULTILINE)

    def run(self, question: dict, source: str) -> List[Any]:
        directory = tempfile.mkdtemp(prefix="cbp_java_")
        path = os.path.join(directory, self.filename)
        with open(path, "w") as fh:
            fh.write(_build_java(question, self._demote_public(source)))
        javac = _require("javac", "java")
        try:
            proc = subprocess.run(
                [javac, "-d", directory, path],
                capture_output=True, text=True, timeout=COMPILE_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            raise RunError("timeout", "javac took too long", "java")
        if proc.returncode != 0:
            raise RunError("compile", _clean(proc.stderr), "java")
        out = self._exec([_require("java", "java"), "-cp", directory, "Main"], directory, "java")
        return _collect(out)


class RustAdapter(Adapter):
    language = "rust"
    filename = "main.rs"

    def run(self, question: dict, source: str) -> List[Any]:
        directory = tempfile.mkdtemp(prefix="cbp_rust_")
        path = os.path.join(directory, self.filename)
        with open(path, "w") as fh:
            fh.write(_build_rust(question, source))
        binary = os.path.join(directory, "out")
        try:
            proc = subprocess.run(
                [_require("rustc", "rust"), "--edition", "2021", "-O",
                 "-A", "warnings", "-o", binary, path],
                capture_output=True, text=True, timeout=COMPILE_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            raise RunError("timeout", "compilation took too long", "rust")
        if proc.returncode != 0:
            raise RunError("compile", _clean(proc.stderr), "rust")
        return _collect(self._exec([binary], directory, "rust"))


def _require(binary: str, language: str) -> str:
    """Absolute path to a toolchain binary, or a RunError explaining its absence.

    `toolchain` probes the paths the installers actually use rather than
    trusting PATH, because a Finder-launched .app inherits almost none.
    """
    # `clang-cl` is the Windows spelling of the same compiler, so a report
    # that names clang++ on a machine that only ever installs clang-cl sends
    # the user looking for something that does not exist.
    reported = "clang++ or clang-cl" if language == "cpp" else binary
    for name in _toolchain.candidates_for(language, binary):
        path = _find_binary(name)
        if path:
            return path
    hint = ("is a JDK installed?" if language == "java"
            else f"is {reported} installed?")
    raise RunError("interface", f"{binary} not found -- {hint}", language)


ADAPTERS = {
    "python": PythonAdapter(),
    "cpp": CppAdapter(),
    "rust": RustAdapter(),
    "csharp": CSharpAdapter(),
    "java": JavaAdapter(),
}

LANGUAGES = list(ADAPTERS)
