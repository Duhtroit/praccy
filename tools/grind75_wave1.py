#!/usr/bin/env python3
"""Grind 75, wave 1: the opening block.

Positions 1-12 of the canonical list, minus the two the Coderbyte set already
carries (Two Sum, Valid Anagram) and the two that cannot be expressed here at
all (Implement Queue using Stacks is a design problem; Linked List Cycle asks
whether a list points back at itself, and an array has no pointers for Floyd's
algorithm to chase).
"""

from __future__ import annotations

from grind75_common import (ALGO, ARR, BOOL, INT, LC, LINKED_LIST_NOTE, LIST, MATRIX,
                            SEARCH, SM, STRETCH, STR, TREE, TREE_NOTE, c, q, S)

QUESTIONS = [    # ══ wave 1: the opening block ══════════════════════════════════════
    # Positions 1-12 of the canonical list, minus the two the dataset already
    # has (Two Sum, Valid Anagram) and minus the two that cannot be expressed
    # (Implement Queue using Stacks, Linked List Cycle).

    q("g-valid-parentheses", "Valid Parentheses", STRETCH, [ALGO, "stack"], "ValidParentheses",
      "Have the function ValidParentheses(s) take a string of the characters "
      "( ) [ ] { } and return the boolean true if every bracket in the string is "
      "closed by the same type of bracket in the correct order, otherwise return "
      "false.\n\n" + "A closing bracket must match the most recent unmatched opening "
      "bracket, which is what makes a stack the right shape for this.",
      (["s"], [STR]),
      [c(["()"], True, BOOL), c(["()[]{}"], True, BOOL), c(["(]"], False, BOOL),
       c(["([)]"], False, BOOL), c(["{[()]}"], True, BOOL), c([""], True, BOOL)],
      S('''def ValidParentheses(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
''',
        """
bool ValidParentheses(const string& s) {
  const string open = "([{", close = ")]}";
  vector<char> stack;
  for (char ch : s) {
    size_t i = open.find(ch);
    if (i != string::npos) { stack.push_back(ch); continue; }
    size_t j = close.find(ch);
    if (j == string::npos) continue;
    if (stack.empty() || stack.back() != open[j]) return false;
    stack.pop_back();
  }
  return stack.empty();
}
""",
        """
using System.Collections.Generic;

public class Solution
{
    public static bool ValidParentheses(string s)
    {
        var pairs = new Dictionary<char, char> { { ')', '(' }, { ']', '[' }, { '}', '{' } };
        var stack = new Stack<char>();
        foreach (char ch in s)
        {
            if (ch == '(' || ch == '[' || ch == '{') { stack.Push(ch); continue; }
            if (!pairs.ContainsKey(ch)) continue;
            if (stack.Count == 0 || stack.Pop() != pairs[ch]) return false;
        }
        return stack.Count == 0;
    }
}
""",
        """
public class Solution {
    public static boolean validParentheses(String s) {
        java.util.Deque<Character> stack = new java.util.ArrayDeque<>();
        for (char ch : s.toCharArray()) {
            if (ch == '(' || ch == '[' || ch == '{') { stack.push(ch); continue; }
            if (ch != ')' && ch != ']' && ch != '}') continue;
            char want = ch == ')' ? '(' : ch == ']' ? '[' : '{';
            if (stack.isEmpty() || stack.pop() != want) return false;
        }
        return stack.isEmpty();
    }
}
"""),
      position=2, source=LC, sourceId=20,
      sourceNote="LeetCode 20 (Easy). A stack, and the reason a stack rather than a counter."),

    q("g-merge-two-sorted-lists", "Merge Two Sorted Lists", STRETCH, [ALGO, "linked list"],
      "MergeTwoSortedLists",
      "Have the function MergeTwoSortedLists(a, b) take two linked lists, each "
      "already sorted from smallest to largest, and return one list holding every "
      "value from both, still sorted from smallest to largest.\n\n" + LINKED_LIST_NOTE +
      "\n\nBecause both inputs are already sorted there is no reason to sort the "
      "output, and no reason to look at a value again once it has been placed.",
      (["a", "b"], [LIST, LIST]),
      [c([[1, 2, 4], [1, 3, 4]], [1, 1, 2, 3, 4, 4], LIST),
       c([[], []], [], LIST),
       c([[], [0]], [0], LIST),
       c([[1, 2, 3], [4, 5, 6]], [1, 2, 3, 4, 5, 6], LIST)],
      S('''def MergeTwoSortedLists(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
''',
        """
vector<int> MergeTwoSortedLists(const vector<int>& a, const vector<int>& b) {
  vector<int> out;
  size_t i = 0, j = 0;
  while (i < a.size() && j < b.size())
    out.push_back(a[i] <= b[j] ? a[i++] : b[j++]);
  while (i < a.size()) out.push_back(a[i++]);
  while (j < b.size()) out.push_back(b[j++]);
  return out;
}
""",
        """
public class Solution
{
    public static int[] MergeTwoSortedLists(int[] a, int[] b)
    {
        var outp = new int[a.Length + b.Length];
        int i = 0, j = 0, k = 0;
        while (i < a.Length && j < b.Length) outp[k++] = a[i] <= b[j] ? a[i++] : b[j++];
        while (i < a.Length) outp[k++] = a[i++];
        while (j < b.Length) outp[k++] = b[j++];
        return outp;
    }
}
""",
        """
public class Solution {
    public static int[] mergeTwoSortedLists(int[] a, int[] b) {
        int[] outp = new int[a.length + b.length];
        int i = 0, j = 0, k = 0;
        while (i < a.length && j < b.length) outp[k++] = a[i] <= b[j] ? a[i++] : b[j++];
        while (i < a.length) outp[k++] = a[i++];
        while (j < b.length) outp[k++] = b[j++];
        return outp;
    }
}
"""),
      position=3, source=LC, sourceId=21,
      sourceNote="LeetCode 21 (Easy). Two cursors, no comparisons that are not needed."),

    q("g-best-time-to-trade", "Best Time to Buy and Sell Stock", STRETCH, [ALGO], "BestTimeToBuyAndSellStock",
      "Have the function BestTimeToBuyAndSellStock(prices) take the daily price of a "
      "stock, one price per day in order, and return the largest profit that could "
      "have been made by buying on one day and selling on a later day. Return 0 if "
      "no such profit is possible.\n\nThe obvious three-nested-loop answer is O(n^3). "
      "The only thing that matters about a buy day is the cheapest price seen so far, "
      "so one pass is enough.",
      (["prices"], [ARR]),
      [c([[7, 1, 5, 3, 6, 4]], 5, INT), c([[7, 6, 4, 3, 1]], 0, INT),
       c([[1]], 0, INT), c([[1, 2]], 1, INT), c([[]], 0, INT),
       c([[2, 4, 1]], 2, INT)],
      S('''def BestTimeToBuyAndSellStock(prices):
    best = 0
    low = 0
    for i, price in enumerate(prices):
        if i == 0 or price < low:
            low = price
        elif price - low > best:
            best = price - low
    return best
''',
        """
int BestTimeToBuyAndSellStock(const vector<int>& prices) {
  int best = 0, low = 0;
  for (size_t i = 0; i < prices.size(); ++i) {
    if (i == 0 || prices[i] < low) low = prices[i];
    else if (prices[i] - low > best) best = prices[i] - low;
  }
  return best;
}
""",
        """
public class Solution
{
    public static int BestTimeToBuyAndSellStock(int[] prices)
    {
        int best = 0, low = 0;
        for (int i = 0; i < prices.Length; i++)
        {
            if (i == 0 || prices[i] < low) low = prices[i];
            else if (prices[i] - low > best) best = prices[i] - low;
        }
        return best;
    }
}
""",
        """
public class Solution {
    public static int bestTimeToBuyAndSellStock(int[] prices) {
        int best = 0, low = 0;
        for (int i = 0; i < prices.length; i++) {
            if (i == 0 || prices[i] < low) low = prices[i];
            else if (prices[i] - low > best) best = prices[i] - low;
        }
        return best;
    }
}
"""),
      position=4, source=LC, sourceId=121,
      sourceNote="LeetCode 121 (Easy). One pass, tracking the cheapest price so far."),

    q("g-valid-palindrome", "Valid Palindrome", STRETCH, [ALGO, SM, "two pointers"], "ValidPalindrome",
      "Have the function ValidPalindrome(s) take a string and return the boolean true "
      "if it reads the same forwards and backwards once everything that is not a "
      "letter or a digit is removed and the letters are lowercased, otherwise return "
      "false.\n\nTwo pointers from both ends never have to build the cleaned string at "
      "all, though building it is the more obvious route and is not wrong.",
      (["s"], [STR]),
      [c(["A man, a plan, a canal: Panama"], True, BOOL), c(["race a car"], False, BOOL),
       c([" "], True, BOOL), c([""], True, BOOL), c(["0P"], False, BOOL),
       c([".,"], True, BOOL)],
      S('''def ValidPalindrome(s):
    clean = [ch.lower() for ch in s if ch.isalnum()]
    return clean == clean[::-1]
''',
        """
bool ValidPalindrome(const string& s) {
  string clean;
  for (char ch : s)
    if (isalnum((unsigned char)ch)) clean.push_back(tolower((unsigned char)ch));
  for (size_t i = 0; i < clean.size() / 2; ++i)
    if (clean[i] != clean[clean.size() - 1 - i]) return false;
  return true;
}
""",
        """
public class Solution
{
    public static bool ValidPalindrome(string s)
    {
        var clean = new System.Text.StringBuilder();
        foreach (char ch in s)
            if (char.IsLetterOrDigit(ch)) clean.Append(char.ToLowerInvariant(ch));
        string text = clean.ToString();
        for (int i = 0; i < text.Length / 2; i++)
            if (text[i] != text[text.Length - 1 - i]) return false;
        return true;
    }
}
""",
        """
public class Solution {
    public static boolean validPalindrome(String s) {
        StringBuilder clean = new StringBuilder();
        for (char ch : s.toCharArray())
            if (Character.isLetterOrDigit(ch)) clean.append(Character.toLowerCase(ch));
        for (int i = 0; i < clean.length() / 2; i++)
            if (clean.charAt(i) != clean.charAt(clean.length() - 1 - i)) return false;
        return true;
    }
}
"""),
      position=5, source=LC, sourceId=125,
      sourceNote="LeetCode 125 (Easy). Cleaning the string first is the honest way in."),

    q("g-invert-binary-tree", "Invert Binary Tree", STRETCH, [ALGO, "tree"], "InvertBinaryTree",
      "Have the function InvertBinaryTree(root) take a binary tree and return the same "
      "tree with every node's left and right children swapped.\n\n" + TREE_NOTE +
      "\n\nNote that the answer can be a longer array than the one you were given: "
      "a node that was a left child with no right sibling becomes a right child "
      "with no left sibling, so a value moves to an index the input never "
      "reached. The tree's shape is not preserved, only its set of values.",
      (["root"], [TREE]),
      [c([[1, 2, 3, None, None, None, 5]], [1, 3, 2, None, None, 5], TREE),
       c([[4, 7, 2, 9, None, 6, None, 3]], [4, 2, 7, None, 9, None, 6, 3], TREE),
       c([[1, 2]], [1, None, 2], TREE),
       c([[1]], [1], TREE),
       c([[]], [], TREE)],
      S('''def InvertBinaryTree(root):
    size = len(root)
    tree = list(root) + [None] * (size + 1)
    for position in range(size):
        if tree[position] is None:
            continue
        left, right = 2 * position + 1, 2 * position + 2
        left_value, right_value = tree[left], tree[right]
        tree[left] = right_value
        tree[right] = left_value
    while tree and tree[-1] is None:
        tree.pop()
    return tree
''',
        """
vector<optional<int>> InvertBinaryTree(const vector<optional<int>>& root) {
  // A swap can move a value to an index past the end of the input, so the array
  // is widened first. Two children per node, one more level, is enough.
  vector<optional<int>> tree(2 * root.size() + 1);
  for (size_t i = 0; i < root.size(); ++i) tree[i] = root[i];
  for (size_t p = 0; p < root.size(); ++p) {
    if (!tree[p].has_value()) continue;
    size_t left = 2 * p + 1, right = left + 1;
    optional<int> left_value = tree[left], right_value = tree[right];
    tree[left] = right_value;
    tree[right] = left_value;
  }
  while (!tree.empty() && !tree.back().has_value()) tree.pop_back();
  return tree;
}
""",
        """
public class Solution
{
    public static int?[] InvertBinaryTree(int?[] root)
    {
        var tree = new int?[2 * root.Length + 1];
        Array.Copy(root, tree, root.Length);
        for (int p = 0; p < root.Length; p++)
        {
            if (!tree[p].HasValue) continue;
            int left = 2 * p + 1, right = left + 1;
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
        """
public class Solution {
    public static Integer[] invertBinaryTree(Integer[] root) {
        Integer[] tree = new Integer[2 * root.length + 1];
        System.arraycopy(root, 0, tree, 0, root.length);
        for (int p = 0; p < root.length; p++) {
            if (tree[p] == null) continue;
            int left = 2 * p + 1, right = left + 1;
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
"""),
      position=6, source=LC, sourceId=226,
      sourceNote="LeetCode 226 (Easy). The first tree on the list, and a good one to meet the encoding on."),

    q("g-binary-search", "Binary Search", STRETCH, [SEARCH, ALGO], "BinarySearch",
      "Have the function BinarySearch(nums, target) take a list of distinct integers "
      "sorted from smallest to largest and return the index of target in it, or -1 if "
      "target is not there.\n\nEach comparison should throw away half of what is "
      "left. If an implementation only ever discards one element, it is not this "
      "question.",
      (["nums", "target"], [ARR, INT]),
      [c([[-1, 0, 3, 5, 9, 12], 9], 4, INT), c([[-1, 0, 3, 5, 9, 12], 2], -1, INT),
       c([[5], 5], 0, INT), c([[1, 2, 3], 5], -1, INT), c([[], 1], -1, INT)],
      S('''def BinarySearch(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
''',
        """
int BinarySearch(const vector<int>& nums, int target) {
  int low = 0, high = (int)nums.size() - 1;
  while (low <= high) {
    int mid = low + (high - low) / 2;
    if (nums[mid] == target) return mid;
    if (nums[mid] < target) low = mid + 1; else high = mid - 1;
  }
  return -1;
}
""",
        """
public class Solution
{
    public static int BinarySearch(int[] nums, int target)
    {
        int low = 0, high = nums.Length - 1;
        while (low <= high)
        {
            int mid = low + (high - low) / 2;
            if (nums[mid] == target) return mid;
            if (nums[mid] < target) low = mid + 1; else high = mid - 1;
        }
        return -1;
    }
}
""",
        """
public class Solution {
    public static int binarySearch(int[] nums, int target) {
        int low = 0, high = nums.length - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (nums[mid] == target) return mid;
            if (nums[mid] < target) low = mid + 1; else high = mid - 1;
        }
        return -1;
    }
}
"""),
      position=8, source=LC, sourceId=704,
      sourceNote="LeetCode 704 (Easy). The half-open interval is the fiddly part, not the idea."),

    q("g-flood-fill", "Flood Fill", STRETCH, [ALGO, "matrix", "search"], "FloodFill",
      "Have the function FloodFill(image, sr, sc, color) take a grid of integers, each "
      "representing a pixel colour, plus the row and column of a starting pixel and a "
      "new colour. Return the grid with every pixel connected to the starting pixel "
      "through four-directional neighbours of the same original colour repainted.\n\n"
      "The original colour has to be captured before any painting starts, or the flood "
      "stops the moment it fills in the pixel it just reached.",
      (["image", "sr", "sc", "color"], [MATRIX, INT, INT, INT]),
      [c([[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2], [[2, 2, 2], [2, 2, 0], [2, 0, 1]], MATRIX),
       c([[[0, 0, 0], [0, 0, 0]], 0, 0, 0], [[0, 0, 0], [0, 0, 0]], MATRIX),
       c([[[0, 0, 0], [0, 1, 1]], 1, 1, 1], [[0, 0, 0], [0, 1, 1]], MATRIX),
       c([[[1, 1, 1], [1, 1, 1], [1, 1, 1]], 1, 1, 2],
         [[2, 2, 2], [2, 2, 2], [2, 2, 2]], MATRIX)],
      S('''def FloodFill(image, sr, sc, color):
    if not image or not image[0]:
        return image
    start = image[sr][sc]
    if start == color:
        return image
    stack = [(sr, sc)]
    while stack:
        row, column = stack.pop()
        if not (0 <= row < len(image)):
            continue
        if not (0 <= column < len(image[row])):
            continue
        if image[row][column] != start:
            continue
        image[row][column] = color
        stack.append((row + 1, column))
        stack.append((row - 1, column))
        stack.append((row, column + 1))
        stack.append((row, column - 1))
    return image
''',
        """
vector<vector<int>> FloodFill(vector<vector<int>> image, int sr, int sc, int color) {
  if (image.empty() || image[0].empty()) return image;
  int start = image[sr][sc];
  if (start == color) return image;
  vector<pair<int, int>> stack;
  stack.push_back({sr, sc});
  while (!stack.empty()) {
    pair<int, int> top = stack.back();
    stack.pop_back();
    int row = top.first, column = top.second;
    if (row < 0 || row >= (int)image.size()) continue;
    if (column < 0 || column >= (int)image[row].size()) continue;
    if (image[row][column] != start) continue;
    image[row][column] = color;
    stack.push_back({row + 1, column});
    stack.push_back({row - 1, column});
    stack.push_back({row, column + 1});
    stack.push_back({row, column - 1});
  }
  return image;
}
""",
        """
using System.Collections.Generic;

public class Solution
{
    public static int[][] FloodFill(int[][] image, int sr, int sc, int color)
    {
        if (image.Length == 0 || image[0].Length == 0) return image;
        int start = image[sr][sc];
        if (start == color) return image;
        var stack = new Stack<int[]>();
        stack.Push(new[] { sr, sc });
        while (stack.Count > 0)
        {
            int[] top = stack.Pop();
            int row = top[0], column = top[1];
            if (row < 0 || row >= image.Length) continue;
            if (column < 0 || column >= image[row].Length) continue;
            if (image[row][column] != start) continue;
            image[row][column] = color;
            stack.Push(new[] { row + 1, column });
            stack.Push(new[] { row - 1, column });
            stack.Push(new[] { row, column + 1 });
            stack.Push(new[] { row, column - 1 });
        }
        return image;
    }
}
""",
        """
public class Solution {
    public static int[][] floodFill(int[][] image, int sr, int sc, int color) {
        if (image.length == 0 || image[0].length == 0) return image;
        int start = image[sr][sc];
        if (start == color) return image;
        java.util.ArrayDeque<int[]> stack = new java.util.ArrayDeque<>();
        stack.push(new int[] { sr, sc });
        while (!stack.isEmpty()) {
            int[] top = stack.pop();
            int row = top[0], column = top[1];
            if (row < 0 || row >= image.length) continue;
            if (column < 0 || column >= image[row].length) continue;
            if (image[row][column] != start) continue;
            image[row][column] = color;
            stack.push(new int[] { row + 1, column });
            stack.push(new int[] { row - 1, column });
            stack.push(new int[] { row, column + 1 });
            stack.push(new int[] { row, column - 1 });
        }
        return image;
    }
}
"""),
      position=9, source=LC, sourceId=733,
      sourceNote="LeetCode 733 (Easy). An iterative flood fill, to keep the recursion bound off the table."),

    q("g-lca-bst", "Lowest Common Ancestor of a BST", STRETCH, [ALGO, "tree", "search"],
      "LowestCommonAncestorBst",
      "Have the function LowestCommonAncestorBst(root, p, q) take a binary search tree "
      "and the values of two of its nodes, and return the value of the lowest ancestor "
      "they share.\n\n" + TREE_NOTE +
      "\n\nThe ordering is the whole question. Because every value to the left of a "
      "node is smaller and every value to the right is larger, knowing which side both "
      "values fall on says which way to walk, and no search of both branches is needed.",
      (["root", "p", "q"], [TREE, INT, INT]),
      [c([[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 8], 6, INT),
       c([[6, 2, 8, 0, 4, 7, 9, None, None, 3, 5], 2, 4], 2, INT),
       c([[2, 1, 3], 1, 3], 2, INT),
       c([[2, 1, 3], 2, 3], 2, INT),
       c([[0], 0, 0], 0, INT)],
      S('''def LowestCommonAncestorBst(root, p, q):
    node = 0
    while node < len(root) and root[node] is not None:
        value = root[node]
        if p < value and q < value:
            node = 2 * node + 1
        elif p > value and q > value:
            node = 2 * node + 2
        else:
            return value
    return -1
''',
        """
int LowestCommonAncestorBst(const vector<optional<int>>& root, int p, int q) {
  size_t node = 0;
  while (node < root.size() && root[node].has_value()) {
    int value = *root[node];
    if (p < value && q < value) { node = 2 * node + 1; continue; }
    if (p > value && q > value) { node = 2 * node + 2; continue; }
    return value;
  }
  return -1;
}
""",
        """
public class Solution
{
    public static int LowestCommonAncestorBst(int?[] root, int p, int q)
    {
        int node = 0;
        while (node < root.Length && root[node].HasValue)
        {
            int value = root[node].GetValueOrDefault();
            if (p < value && q < value) { node = 2 * node + 1; continue; }
            if (p > value && q > value) { node = 2 * node + 2; continue; }
            return value;
        }
        return -1;
    }
}
""",
        """
public class Solution {
    public static int lowestCommonAncestorBst(Integer[] root, int p, int q) {
        int node = 0;
        while (node < root.length && root[node] != null) {
            int value = root[node];
            if (p < value && q < value) { node = 2 * node + 1; continue; }
            if (p > value && q > value) { node = 2 * node + 2; continue; }
            return value;
        }
        return -1;
    }
}
"""),
      position=10, source=LC, sourceId=235,
      sourceNote="LeetCode 235 (Medium). The BST ordering turns a two-tree problem into a walk down one."),

    q("g-balanced-binary-tree", "Balanced Binary Tree", STRETCH, [ALGO, "tree"], "IsBalanced",
      "Have the function IsBalanced(root) take a binary tree and return the boolean true "
      "if, at every node, the heights of the two subtrees below it differ by no more "
      "than one, otherwise return false. An empty tree is balanced.\n\n" + TREE_NOTE +
      "\n\nAsk each node for its height rather than asking for every node's height "
      "separately, and let -1 mean unbalanced so the bad news travels up on its own.",
      (["root"], [TREE]),
      [c([[3, 9, 20, None, None, 15, 7]], True, BOOL),
       c([[1, 2, 2, 3, 3, None, None, 4, 4]], False, BOOL),
       c([[1]], True, BOOL), c([[]], True, BOOL),
       c([[1, 2, None, 3]], False, BOOL),
       c([[1, 2, 2, 3, 3]], True, BOOL)],
      S('''def IsBalanced(root):
    def height(node):
        if node >= len(root) or root[node] is None:
            return 0
        left = height(2 * node + 1)
        right = height(2 * node + 2)
        if left < 0 or right < 0 or abs(left - right) > 1:
            return -1
        return max(left, right) + 1
    return height(0) >= 0
''',
        """
static int __height(const vector<optional<int>>& tree, size_t node) {
  if (node >= tree.size() || !tree[node].has_value()) return 0;
  int left = __height(tree, 2 * node + 1);
  int right = __height(tree, 2 * node + 2);
  if (left < 0 || right < 0 || left - right > 1 || right - left > 1) return -1;
  return max(left, right) + 1;
}

bool IsBalanced(const vector<optional<int>>& root) {
  return __height(root, 0) >= 0;
}
""",
        """
public class Solution
{
    static int Height(int?[] tree, int node)
    {
        if (node >= tree.Length || !tree[node].HasValue) return 0;
        int left = Height(tree, 2 * node + 1);
        int right = Height(tree, 2 * node + 2);
        if (left < 0 || right < 0 || left - right > 1 || right - left > 1) return -1;
        return Math.Max(left, right) + 1;
    }

    public static bool IsBalanced(int?[] root)
    {
        return Height(root, 0) >= 0;
    }
}
""",
        """
public class Solution {
    static int height(Integer[] tree, int node) {
        if (node >= tree.length || tree[node] == null) return 0;
        int left = height(tree, 2 * node + 1);
        int right = height(tree, 2 * node + 2);
        if (left < 0 || right < 0 || left - right > 1 || right - left > 1) return -1;
        return Math.max(left, right) + 1;
    }

    public static boolean isBalanced(Integer[] root) {
        return height(root, 0) >= 0;
    }
}
"""),
      position=11, source=LC, sourceId=110,
      sourceNote="LeetCode 110 (Easy). Height doubles as the verdict, which is the whole trick."),
]
