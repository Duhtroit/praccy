"""Structural conformance probes.

The practice dataset cannot prove the tree, linked list, matrix, graph and
string-list contracts, because every one of the 84 questions it holds returns
a scalar or a flat array. So the structural plumbing gets its own suite: a
handful of small problems, one per contract, each with a reference solution in
all five languages, run by `cbp.selftest` on every pass.

These are not practice questions and they are not shown to anyone. They exist
so that adding a question with a tree argument is a data change rather than a
harness change -- if a new contract type is wired into one language and not
another, this suite fails and says so.

Run with:  python3 -m cbp.structures
"""

from __future__ import annotations

import sys
from typing import List

from .adapters import LANGUAGES
from .engine import evaluate

# The tree encoding, in one place, because five languages and a test suite all
# have to agree on it:
#
#   A tree is a flat array in level order. The node at index p has its left
#   child at 2p+1 and its right child at 2p+2 -- the binary heap layout, which
#   is the one indexing that needs no bookkeeping to walk. A missing child is
#   `null`, and trailing nulls are trimmed: [1, 2, 3, null, null, null, 5] is a
#   root of 1 whose right child 3 has a left child of 5. The empty tree is [].
#
# Keeping the encoding positional is what makes the tree questions worth
# practising. A harness that handed over a ready-made node object would hide
# the one thing the question is about.

PROBES: List[dict] = [
    {
        "id": "struct-tree-depth",
        "title": "Depth of a tree given in level order",
        "functionName": "MaxDepth",
        "expectedType": "int",
        "signature": {"argNames": ["root"], "argTypes": ["tree"]},
        "cases": [
            {"args": [[1, 2, 3, None, None, None, 5]], "expected": 3, "expectedType": "int"},
            {"args": [[1]], "expected": 1, "expectedType": "int"},
            {"args": [[]], "expected": 0, "expectedType": "int"},
            {"args": [[1, 2, 3, 4, 5]], "expected": 3, "expectedType": "int"},
        ],
        "solution": {
            "python": '''
def MaxDepth(root):
    depth = 0
    index = 0
    while index < len(root):
        depth += 1
        index = 2 * index + 1
    return depth
''',
            "cpp": """
int MaxDepth(const vector<optional<int>>& root) {
  int depth = 0;
  for (size_t index = 0; index < root.size(); index = 2 * index + 1) depth++;
  return depth;
}
""",
            "csharp": """
public class Solution
{
    public static int MaxDepth(int?[] root)
    {
        int depth = 0, index = 0;
        while (index < root.Length)
        {
            depth++;
            index = 2 * index + 1;
        }
        return depth;
    }
}
""",
            "java": """
public class Solution {
    public static int maxDepth(Integer[] root) {
        int depth = 0, index = 0;
        while (index < root.length) {
            depth++;
            index = 2 * index + 1;
        }
        return depth;
    }
}
""",
            "rust": """
impl Solution {
    pub fn max_depth(root: Vec<Option<i64>>) -> i64 {
        let mut depth = 0i64;
        let mut index = 0usize;
        while index < root.len() {
            depth += 1;
            index = 2 * index + 1;
        }
        depth
    }
}
""",
        },
    },
    {
        "id": "struct-tree-invert",
        "title": "Invert a tree, returned in the same encoding",
        "functionName": "InvertTree",
        "expectedType": "tree",
        "signature": {"argNames": ["root"], "argTypes": ["tree"]},
        "cases": [
            {"args": [[1, 2, 3, None, None, None, 5]],
             "expected": [1, 3, 2, None, None, 5], "expectedType": "tree"},
            {"args": [[1, 2, 3]], "expected": [1, 3, 2], "expectedType": "tree"},
            {"args": [[1, None, 2]], "expected": [1, 2], "expectedType": "tree"},
            {"args": [[1, 2]], "expected": [1, None, 2], "expectedType": "tree"},
            {"args": [[]], "expected": [], "expectedType": "tree"},
        ],
        "solution": {
            "python": '''
def InvertTree(root):
    size = len(root)
    out = list(root) + [None] * (size + 1)
    for position in range(size):
        if out[position] is None:
            continue
        left = 2 * position + 1
        right = left + 1
        left_value, right_value = out[left], out[right]
        out[left] = right_value
        out[right] = left_value
    while out and out[-1] is None:
        out.pop()
    return out
''',
            "cpp": """
vector<optional<int>> InvertTree(const vector<optional<int>>& root) {
  vector<optional<int>> out(2 * root.size() + 1);
  for (size_t i = 0; i < root.size(); ++i) out[i] = root[i];
  for (size_t position = 0; position < root.size(); ++position) {
    if (!out[position].has_value()) continue;
    size_t left = 2 * position + 1, right = left + 1;
    optional<int> left_value = out[left], right_value = out[right];
    out[left] = right_value;
    out[right] = left_value;
  }
  while (!out.empty() && !out.back().has_value()) out.pop_back();
  return out;
}
""",
            "csharp": """
public class Solution
{
    public static int?[] InvertTree(int?[] root)
    {
        var tree = new int?[2 * root.Length + 1];
        Array.Copy(root, tree, root.Length);
        for (int position = 0; position < root.Length; position++)
        {
            if (!tree[position].HasValue) continue;
            int left = 2 * position + 1, right = left + 1;
            int? left_value = tree[left], right_value = tree[right];
            tree[left] = right_value;
            tree[right] = left_value;
        }
        int size = tree.Length;
        while (size > 0 && !tree[size - 1].HasValue) size--;
        var trimmed = new int?[size];
        Array.Copy(tree, trimmed, size);
        return trimmed;
    }
}
""",
            "java": """
public class Solution {
    public static Integer[] invertTree(Integer[] root) {
        Integer[] tree = new Integer[2 * root.length + 1];
        System.arraycopy(root, 0, tree, 0, root.length);
        for (int position = 0; position < root.length; position++) {
            if (tree[position] == null) continue;
            int left = 2 * position + 1, right = left + 1;
            Integer left_value = tree[left], right_value = tree[right];
            tree[left] = right_value;
            tree[right] = left_value;
        }
        int size = tree.length;
        while (size > 0 && tree[size - 1] == null) size--;
        Integer[] trimmed = new Integer[size];
        System.arraycopy(tree, 0, trimmed, 0, size);
        return trimmed;
    }
}
""",
            "rust": """
impl Solution {
    pub fn invert_tree(root: Vec<Option<i64>>) -> Vec<Option<i64>> {
        let size = root.len();
        let mut tree = vec![None; 2 * size + 1];
        for (i, value) in root.iter().enumerate() {
            tree[i] = *value;
        }
        for position in 0..size {
            if tree[position].is_none() {
                continue;
            }
            let left = 2 * position + 1;
            let right = left + 1;
            let left_value = tree[left];
            let right_value = tree[right];
            tree[left] = right_value;
            tree[right] = left_value;
        }
        while tree.last() == Some(&None) {
            tree.pop();
        }
        tree
    }
}
""",
        },
    },
    {
        "id": "struct-list-reverse",
        "title": "Reverse a singly linked list handed over by its values",
        "functionName": "ReverseList",
        "expectedType": "list",
        "signature": {"argNames": ["head"], "argTypes": ["list"]},
        "cases": [
            {"args": [[1, 2, 3]], "expected": [3, 2, 1], "expectedType": "list"},
            {"args": [[]], "expected": [], "expectedType": "list"},
            {"args": [[1]], "expected": [1], "expectedType": "list"},
            {"args": [[4, 5, 6, 7]], "expected": [7, 6, 5, 4], "expectedType": "list"},
        ],
        "solution": {
            "python": '''
def ReverseList(head):
    return list(reversed(head))
''',
            "cpp": """
vector<int> ReverseList(const vector<int>& head) {
  vector<int> out;
  for (size_t i = head.size(); i > 0; --i) out.push_back(head[i - 1]);
  return out;
}
""",
            "csharp": """
using System.Linq;

public class Solution
{
    public static int[] ReverseList(int[] head)
    {
        return head.Reverse().ToArray();
    }
}
""",
            "java": """
public class Solution {
    public static int[] reverseList(int[] head) {
        int[] out = new int[head.length];
        for (int i = 0; i < head.length; i++) out[i] = head[head.length - 1 - i];
        return out;
    }
}
""",
            "rust": """
impl Solution {
    pub fn reverse_list(head: Vec<i64>) -> Vec<i64> {
        let mut out = head.clone();
        out.reverse();
        out
    }
}
""",
        },
    },
    {
        "id": "struct-matrix-rotate",
        "title": "Rotate a square matrix a quarter turn clockwise",
        "functionName": "RotateMatrix",
        "expectedType": "matrix",
        "signature": {"argNames": ["matrix"], "argTypes": ["matrix"]},
        "cases": [
            {"args": [[[1, 2], [3, 4]]], "expected": [[3, 1], [4, 2]], "expectedType": "matrix"},
            {"args": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]],
             "expected": [[7, 4, 1], [8, 5, 2], [9, 6, 3]], "expectedType": "matrix"},
            {"args": [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]],
             "expected": [[13, 9, 5, 1], [14, 10, 6, 2],
                          [15, 11, 7, 3], [16, 12, 8, 4]], "expectedType": "matrix"},
            {"args": [[[1]]], "expected": [[1]], "expectedType": "matrix"},
        ],
        "solution": {
            "python": '''
def RotateMatrix(matrix):
    return [list(row) for row in zip(*matrix[::-1])]
''',
            "cpp": """
vector<vector<int>> RotateMatrix(const vector<vector<int>>& matrix) {
  int n = matrix.size();
  vector<vector<int>> out(n, vector<int>(n));
  for (int row = 0; row < n; ++row)
    for (int column = 0; column < n; ++column)
      out[column][n - 1 - row] = matrix[row][column];
  return out;
}
""",
            "csharp": """
public class Solution
{
    public static int[][] RotateMatrix(int[][] matrix)
    {
        int n = matrix.Length;
        var rotated = new int[n][];
        for (int i = 0; i < n; i++) rotated[i] = new int[n];
        for (int row = 0; row < n; row++)
            for (int column = 0; column < n; column++)
                rotated[column][n - 1 - row] = matrix[row][column];
        return rotated;
    }
}
""",
            "java": """
public class Solution {
    public static int[][] rotateMatrix(int[][] matrix) {
        int n = matrix.length;
        int[][] rotated = new int[n][n];
        for (int row = 0; row < n; row++)
            for (int column = 0; column < n; column++)
                rotated[column][n - 1 - row] = matrix[row][column];
        return rotated;
    }
}
""",
            "rust": """
impl Solution {
    pub fn rotate_matrix(matrix: Vec<Vec<i64>>) -> Vec<Vec<i64>> {
        let n = matrix.len();
        let mut out = vec![vec![0i64; n]; n];
        for row in 0..n {
            for column in 0..n {
                out[column][n - 1 - row] = matrix[row][column];
            }
        }
        out
    }
}
""",
        },
    },
    {
        "id": "struct-graph-reachable",
        "title": "Adjacency list of the nodes reachable from a start node",
        "functionName": "Reachable",
        "expectedType": "graph",
        "signature": {"argNames": ["graph", "start"], "argTypes": ["graph", "int"]},
        "cases": [
            {"args": [[[1], [0], [3], [2], []], 0],
             "expected": [[1], [0], [], [], []], "expectedType": "graph"},
            {"args": [[[1], [], [2], [], []], 0],
             "expected": [[1], [], [], [], []], "expectedType": "graph"},
            {"args": [[[1], [], [2], [], []], 2],
             "expected": [[], [], [2], [], []], "expectedType": "graph"},
            {"args": [[[], [3], [], [4], []], 0],
             "expected": [[], [], [], [], []], "expectedType": "graph"},
        ],
        "solution": {
            "python": '''
def Reachable(graph, start):
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbour in graph[node]:
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    return [row if node in seen else [] for node, row in enumerate(graph)]
''',
            "cpp": """
vector<vector<int>> Reachable(const vector<vector<int>>& graph, int start) {
  vector<bool> seen(graph.size(), false);
  vector<int> stack;
  seen[start] = true;
  stack.push_back(start);
  while (!stack.empty()) {
    int node = stack.back();
    stack.pop_back();
    for (int next : graph[node]) {
      if (!seen[next]) {
        seen[next] = true;
        stack.push_back(next);
      }
    }
  }
  vector<vector<int>> out;
  for (size_t node = 0; node < graph.size(); ++node)
    out.push_back(seen[node] ? graph[node] : vector<int>());
  return out;
}
""",
            "csharp": """
using System.Collections.Generic;

public class Solution
{
    public static int[][] Reachable(int[][] graph, int start)
    {
        var seen = new bool[graph.Length];
        var stack = new Stack<int>();
        seen[start] = true;
        stack.Push(start);
        while (stack.Count > 0)
        {
            int node = stack.Pop();
            foreach (int next in graph[node])
            {
                if (seen[next]) continue;
                seen[next] = true;
                stack.Push(next);
            }
        }
        var outp = new int[graph.Length][];
        for (int node = 0; node < graph.Length; node++)
            outp[node] = seen[node] ? graph[node] : new int[0];
        return outp;
    }
}
""",
            "java": """
public class Solution {
    public static int[][] reachable(int[][] graph, int start) {
        boolean[] seen = new boolean[graph.length];
        java.util.ArrayDeque<Integer> stack = new java.util.ArrayDeque<>();
        seen[start] = true;
        stack.push(start);
        while (!stack.isEmpty()) {
            int node = stack.pop();
            for (int next : graph[node]) {
                if (seen[next]) continue;
                seen[next] = true;
                stack.push(next);
            }
        }
        int[][] outp = new int[graph.length][];
        for (int node = 0; node < graph.length; node++)
            outp[node] = seen[node] ? graph[node] : new int[0];
        return outp;
    }
}
""",
            "rust": """
impl Solution {
    pub fn reachable(graph: Vec<Vec<i64>>, start: i64) -> Vec<Vec<i64>> {
        let mut seen = vec![false; graph.len()];
        let mut stack = vec![start as usize];
        seen[start as usize] = true;
        while let Some(node) = stack.pop() {
            for &next in &graph[node] {
                if !seen[next as usize] {
                    seen[next as usize] = true;
                    stack.push(next as usize);
                }
            }
        }
        graph
            .into_iter()
            .enumerate()
            .map(|(node, row)| if seen[node] { row } else { Vec::new() })
            .collect()
    }
}
""",
        },
    },
    {
        "id": "struct-words-group",
        "title": "Group anagrams, groups in first-seen order",
        "functionName": "GroupAnagrams",
        "expectedType": "strarray",
        "signature": {"argNames": ["words"], "argTypes": ["stri"]},
        "cases": [
            {"args": [["eat", "tea", "tan", "ate", "nat", "bat"]],
             "expected": ["eat", "tea", "ate", "tan", "nat", "bat"], "expectedType": "strarray"},
            {"args": [["ab", "ba", "abc"]], "expected": ["ab", "ba", "abc"], "expectedType": "strarray"},
            {"args": [["a"]], "expected": ["a"], "expectedType": "strarray"},
            {"args": [["listen", "silent", "enlist", "google", "goog"]],
             "expected": ["listen", "silent", "enlist", "google", "goog"],
             "expectedType": "strarray"},
        ],
        "solution": {
            "python": '''
def GroupAnagrams(words):
    order = []
    groups = {}
    for word in words:
        key = "".join(sorted(word))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(word)
    out = []
    for key in order:
        out.extend(groups[key])
    return out
''',
            "cpp": """
vector<string> GroupAnagrams(const vector<string>& words) {
  map<string, vector<string>> groups;
  vector<string> order;
  for (const string& word : words) {
    string key = word;
    sort(key.begin(), key.end());
    if (groups.find(key) == groups.end()) order.push_back(key);
    groups[key].push_back(word);
  }
  vector<string> out;
  for (const string& key : order)
    for (const string& word : groups[key]) out.push_back(word);
  return out;
}
""",
            "csharp": """
using System.Collections.Generic;
using System.Linq;

public class Solution
{
    public static string[] GroupAnagrams(string[] words)
    {
        var order = new List<string>();
        var groups = new Dictionary<string, List<string>>();
        foreach (string word in words)
        {
            string key = new string(word.OrderBy(c => c).ToArray());
            if (!groups.ContainsKey(key))
            {
                groups[key] = new List<string>();
                order.Add(key);
            }
            groups[key].Add(word);
        }
        return order.SelectMany(key => groups[key]).ToArray();
    }
}
""",
            "java": """
public class Solution {
    public static String[] groupAnagrams(String[] words) {
        java.util.LinkedHashMap<String, java.util.List<String>> groups =
            new java.util.LinkedHashMap<>();
        for (String word : words) {
            char[] letters = word.toCharArray();
            java.util.Arrays.sort(letters);
            groups.computeIfAbsent(new String(letters), key -> new java.util.ArrayList<>())
                  .add(word);
        }
        java.util.List<String> out = new java.util.ArrayList<>();
        for (java.util.List<String> group : groups.values()) out.addAll(group);
        return out.toArray(new String[0]);
    }
}
""",
            "rust": """
use std::collections::HashMap;

impl Solution {
    pub fn group_anagrams(words: Vec<String>) -> Vec<String> {
        let mut order: Vec<String> = Vec::new();
        let mut groups: HashMap<String, Vec<String>> = HashMap::new();
        for word in words {
            let mut letters: Vec<char> = word.chars().collect();
            letters.sort();
            let key: String = letters.into_iter().collect();
            if !groups.contains_key(&key) {
                order.push(key.clone());
            }
            groups.entry(key).or_default().push(word);
        }
        let mut out = Vec::new();
        for key in order {
            out.extend(groups[&key].iter().cloned());
        }
        out
    }
}
""",
        },
    },
    {
        "id": "struct-charmatrix-word",
        "title": "Does a word appear in a grid of characters, four ways",
        "functionName": "WordExists",
        "expectedType": "bool",
        "signature": {"argNames": ["board", "word"], "argTypes": ["charmatrix", "string"]},
        "cases": [
            {"args": [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"],
             "expected": True, "expectedType": "bool"},
            {"args": [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "SEE"],
             "expected": True, "expectedType": "bool"},
            {"args": [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"],
             "expected": False, "expectedType": "bool"},
            {"args": [[["a"]], "a"], "expected": True, "expectedType": "bool"},
            {"args": [[["a"]], "b"], "expected": False, "expectedType": "bool"},
        ],
        "solution": {
            "python": '''
def WordExists(board, word):
    if not word:
        return True
    rows = len(board)
    cols = len(board[0]) if rows else 0

    def search(row, column, index):
        if index == len(word):
            return True
        if row < 0 or row >= rows or column < 0 or column >= cols:
            return False
        if board[row][column] != word[index]:
            return False
        saved = board[row][column]
        board[row][column] = ""
        found = (search(row + 1, column, index + 1)
                 or search(row - 1, column, index + 1)
                 or search(row, column + 1, index + 1)
                 or search(row, column - 1, index + 1))
        board[row][column] = saved
        return found

    for row in range(rows):
        for column in range(cols):
            if search(row, column, 0):
                return True
    return False
''',
            "cpp": """
static bool __searchWord(vector<vector<string>>& board, int row, int column,
                         int index, const string& word) {
  if (index == (int)word.size()) return true;
  int rows = board.size(), cols = board[0].size();
  if (row < 0 || row >= rows || column < 0 || column >= cols) return false;
  if (board[row][column] != string(1, word[index])) return false;
  string saved = board[row][column];
  board[row][column] = "";
  bool found = __searchWord(board, row + 1, column, index + 1, word)
            || __searchWord(board, row - 1, column, index + 1, word)
            || __searchWord(board, row, column + 1, index + 1, word)
            || __searchWord(board, row, column - 1, index + 1, word);
  board[row][column] = saved;
  return found;
}

bool WordExists(vector<vector<string>> board, const string& word) {
  if (word.empty()) return true;
  for (int row = 0; row < (int)board.size(); ++row)
    for (int column = 0; column < (int)board[row].size(); ++column)
      if (__searchWord(board, row, column, 0, word)) return true;
  return false;
}
""",
            "csharp": """
public class Solution
{
    static bool Search(string[][] board, int row, int column, int index, string word)
    {
        if (index == word.Length) return true;
        if (row < 0 || row >= board.Length || column < 0 || column >= board[row].Length) return false;
        if (board[row][column] != word.Substring(index, 1)) return false;
        string saved = board[row][column];
        board[row][column] = "";
        bool found = Search(board, row + 1, column, index + 1, word)
                  || Search(board, row - 1, column, index + 1, word)
                  || Search(board, row, column + 1, index + 1, word)
                  || Search(board, row, column - 1, index + 1, word);
        board[row][column] = saved;
        return found;
    }

    public static bool WordExists(string[][] board, string word)
    {
        if (word.Length == 0) return true;
        for (int row = 0; row < board.Length; row++)
            for (int column = 0; column < board[row].Length; column++)
                if (Search(board, row, column, 0, word)) return true;
        return false;
    }
}
""",
            "java": """
public class Solution {
    static boolean search(String[][] board, int row, int column, int index, String word) {
        if (index == word.length()) return true;
        if (row < 0 || row >= board.length || column < 0 || column >= board[row].length) return false;
        if (board[row][column].isEmpty()
                || board[row][column].charAt(0) != word.charAt(index)) return false;
        String saved = board[row][column];
        board[row][column] = "";
        boolean found = search(board, row + 1, column, index + 1, word)
                     || search(board, row - 1, column, index + 1, word)
                     || search(board, row, column + 1, index + 1, word)
                     || search(board, row, column - 1, index + 1, word);
        board[row][column] = saved;
        return found;
    }

    public static boolean wordExists(String[][] board, String word) {
        if (word.isEmpty()) return true;
        for (int row = 0; row < board.length; row++)
            for (int column = 0; column < board[row].length; column++)
                if (search(board, row, column, 0, word)) return true;
        return false;
    }
}
""",
            "rust": """
impl Solution {
    fn search(board: &mut Vec<Vec<String>>, row: i64, column: i64, index: usize,
              word: &[char]) -> bool {
        let rows = board.len() as i64;
        let cols = board[0].len() as i64;
        if index == word.len() {
            return true;
        }
        if row < 0 || row >= rows || column < 0 || column >= cols {
            return false;
        }
        let cell = board[row as usize][column as usize].clone();
        if cell.chars().next() != Some(word[index]) {
            return false;
        }
        board[row as usize][column as usize] = String::new();
        let found = Solution::search(board, row + 1, column, index + 1, word)
            || Solution::search(board, row - 1, column, index + 1, word)
            || Solution::search(board, row, column + 1, index + 1, word)
            || Solution::search(board, row, column - 1, index + 1, word);
        board[row as usize][column as usize] = cell;
        found
    }

    pub fn word_exists(mut board: Vec<Vec<String>>, word: &str) -> bool {
        if word.is_empty() {
            return true;
        }
        let letters: Vec<char> = word.chars().collect();
        for row in 0..board.len() {
            for column in 0..board[row].len() {
                if Solution::search(&mut board, row as i64, column as i64, 0, &letters) {
                    return true;
                }
            }
        }
        false
    }
}
""",
        },
    },
    {
        # `strmatrix` is rows of words, and it is the only contract whose cells
        # are strings of any length. A charmatrix cell is exactly one character,
        # so a word in a charmatrix is a type error, not a value.
        "id": "struct-strmatrix-group",
        "title": "Flatten rows into groups by first word, groups in first-seen order",
        "functionName": "GroupByFirst",
        "expectedType": "strmatrix",
        "signature": {"argNames": ["rows"], "argTypes": ["strmatrix"]},
        "cases": [
            {"args": [[["apple", "red"], ["banana", "yellow"], ["apple", "green"]]],
             "expected": [["apple", "red", "apple", "green"], ["banana", "yellow"]],
             "expectedType": "strmatrix"},
            {"args": [[["only", "one"]]],
             "expected": [["only", "one"]], "expectedType": "strmatrix"},
            {"args": [[[]]], "expected": [], "expectedType": "strmatrix"},
            {"args": [[]], "expected": [], "expectedType": "strmatrix"},
            # A cell longer than one character is the whole point: this would be
            # malformed as a charmatrix.
            {"args": [[["alpha", "one"], ["alpine", "two"], ["alpha", "two"]]],
             "expected": [["alpha", "one", "alpha", "two"], ["alpine", "two"]],
             "expectedType": "strmatrix"},
        ],
        "solution": {
            "python": '''
def GroupByFirst(rows):
    order = []
    groups = {}
    for row in rows:
        if not row:
            continue
        key = row[0]
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].extend(row)
    return [groups[key] for key in order]
''',
            "cpp": """
#include <map>
#include <string>
#include <vector>
using namespace std;

vector<vector<string>> GroupByFirst(const vector<vector<string>>& rows) {
  vector<string> order;
  map<string, vector<string>> groups;
  for (const auto& row : rows) {
    if (row.empty()) continue;
    const string key = row[0];
    if (groups.find(key) == groups.end()) order.push_back(key);
    vector<string>& group = groups[key];
    for (const string& word : row) group.push_back(word);
  }
  vector<vector<string>> out;
  for (const string& key : order) out.push_back(groups[key]);
  return out;
}
""",
            "csharp": """
using System.Collections.Generic;
using System.Linq;

public class Solution
{
    public static string[][] GroupByFirst(string[][] rows)
    {
        var order = new List<string>();
        var groups = new Dictionary<string, List<string>>();
        foreach (string[] row in rows)
        {
            if (row.Length == 0) continue;
            string key = row[0];
            if (!groups.ContainsKey(key))
            {
                order.Add(key);
                groups[key] = new List<string>();
            }
            groups[key].AddRange(row);
        }
        return order.Select(key => groups[key].ToArray()).ToArray();
    }
}
""",
            "java": """
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Solution {
    public static String[][] groupByFirst(String[][] rows) {
        Map<String, List<String>> groups = new LinkedHashMap<>();
        for (String[] row : rows) {
            if (row.length == 0) continue;
            groups.computeIfAbsent(row[0], key -> new ArrayList<>()).addAll(List.of(row));
        }
        List<String[]> out = new ArrayList<>();
        for (List<String> group : groups.values()) out.add(group.toArray(new String[0]));
        return out.toArray(new String[0][]);
    }
}
""",
            "rust": """
impl Solution {
    pub fn group_by_first(rows: Vec<Vec<String>>) -> Vec<Vec<String>> {
        use std::collections::HashMap;
        let mut order: Vec<String> = Vec::new();
        let mut groups: HashMap<String, Vec<String>> = HashMap::new();
        for row in rows {
            if row.is_empty() {
                continue;
            }
            let key = row[0].clone();
            if !groups.contains_key(&key) {
                order.push(key.clone());
                groups.insert(key.clone(), Vec::new());
            }
            let group = groups.get_mut(&key).unwrap();
            for word in row {
                group.push(word);
            }
        }
        order
            .iter()
            .map(|key| groups.get(key).cloned().unwrap_or_default())
            .collect()
    }
}
""",
        },
    },
]


def run(languages=None) -> int:
    """Run every probe in every language. Returns the number of failures."""
    languages = languages or LANGUAGES
    checks = 0
    failures = []

    for language in languages:
        print(f"\n=== {language} ===")
        for probe in PROBES:
            source = probe["solution"].get(language)
            if source is None:
                print(f"  SKIP  {probe['id']:28s} (no {language} solution)")
                continue
            report = evaluate(probe, language, source)
            checks += 1
            if report["error"]:
                failures.append((language, probe["id"], report["error"]["kind"],
                                 report["error"]["message"]))
                print(f"  ERROR {probe['id']:28s} [{report['error']['kind']}]")
                for line in report["error"]["message"].splitlines()[:4]:
                    print(f"          {line}")
            elif not report["all_passed"]:
                bad = [r for r in report["results"] if not r["passed"]]
                message = bad[0]["message"] if bad else "?"
                failures.append((language, probe["id"], "wrong", message))
                print(f"  FAIL  {probe['id']:28s} {message}")
            else:
                print(f"  pass  {probe['id']:28s} ({len(report['results'])} cases)")

    print("\n" + "=" * 60)
    print(f"{checks - len(failures)}/{checks} structural probes passed "
          f"across {len(languages)} language(s)")
    if failures:
        print(f"\n{len(failures)} FAILURE(S) -- a contract type is not wired up:")
        for language, probe_id, kind, message in failures:
            print(f"  [{language}] {probe_id}: {kind}")
            for line in str(message).splitlines()[:3]:
                print(f"      {line}")
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    chosen = [args[args.index("--lang") + 1]] if "--lang" in args else None
    sys.exit(run(chosen))
