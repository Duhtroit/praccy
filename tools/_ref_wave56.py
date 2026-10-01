#!/usr/bin/env python3
"""Reference implementations for Grind 75 waves 5 and 6.

Every expectation in `grind75_wave5.py` and `grind75_wave6.py` comes out of
this file. Wave 3 was written from recall and seven of its answers were wrong;
wave 4 used a reference file and the only things it caught were a genuine
mistake in my own Rotting Oranges solution and the fact that Lowest Common
Ancestor of a Binary Tree is the general tree, not the BST.

So: implement each question once, here, plainly, and let the generated
expectations be what the four inline languages and the Rust entry are then
written against. The solutions in the wave files are free to be cleverer; they
are not free to disagree with this.

It pays for itself immediately. The first draft of this file contained a
Right Side View that returned the leftmost node of each level, a Kth Smallest
whose index arithmetic walked off the tree, a Construct Tree that passed its
root to the encoder as if it were a child, and a Word Ladder that reached the
end word through steps the end word was not part of. All four would have
shipped as wrong answers.

Run with: python3 tools/_ref_wave56.py
"""

from __future__ import annotations

import json
from collections import deque


# --- 50 Word Break ---------------------------------------------------------

def word_break(s, word_dict):
    words = set(word_dict)
    n = len(s)
    # reach[i] is True when s[:i] splits into dictionary words.
    reach = [False] * (n + 1)
    reach[0] = True
    for end in range(1, n + 1):
        for start in range(end):
            if reach[start] and s[start:end] in words:
                reach[end] = True
                break
    return reach[n]


# --- 51 Partition Equal Subset Sum -----------------------------------------

def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    half = total // 2
    possible = [False] * (half + 1)
    possible[0] = True
    for value in nums:
        for target in range(half, value - 1, -1):
            if possible[target - value]:
                possible[target] = True
    return possible[half]


# --- 52 String to Integer (atoi) -------------------------------------------

INT_MAX = 2 ** 31 - 1
INT_MIN = -(2 ** 31)


def atoi(s):
    """Skip spaces, take one sign, take digits until the first non-digit, clamp.

    Clamping while parsing and clamping at the end agree here, because the
    accumulator only grows. Returning 0 when no digit was ever read is what
    makes "words and 987" a zero rather than a nine hundred and eighty seven.
    """
    i, n = 0, len(s)
    while i < n and s[i] == " ":
        i += 1
    sign = 1
    if i < n and s[i] in "+-":
        if s[i] == "-":
            sign = -1
        i += 1
    digits = 0
    value = 0
    while i < n and "0" <= s[i] <= "9":
        value = value * 10 + (ord(s[i]) - 48)
        digits += 1
        i += 1
    if digits == 0:
        return 0
    value *= sign
    return max(INT_MIN, min(INT_MAX, value))


# --- 53 Spiral Matrix -------------------------------------------------------

def spiral_matrix(matrix):
    if not matrix or not matrix[0]:
        return []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            out.append(matrix[top][col])
        top += 1
        for row in range(top, bottom + 1):
            out.append(matrix[row][right])
        right -= 1
        if top <= bottom:
            for col in range(right, left - 1, -1):
                out.append(matrix[bottom][col])
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                out.append(matrix[row][left])
            left += 1
    return out


# --- 54 Subsets -------------------------------------------------------------

def subsets(nums):
    """The order is pinned, because the answer is a list of lists and the
    comparison is order-sensitive. The empty subset first, then for each value
    in turn every subset so far extended by it. Same order a left-to-right
    backtracking search produces."""
    out = [[]]
    for value in nums:
        out = out + [existing + [value] for existing in out]
    return out


# --- 55 Binary Tree Right Side View -----------------------------------------

def right_side_view(root):
    if not root:
        return []
    out = []
    level = [0]
    while level:
        # The rightmost node of the level is the LAST one pushed, because
        # children are visited left child then right child. Taking level[0]
        # returns the leftmost, which is the other question.
        out.append(root[level[-1]])
        nxt = []
        for node in level:
            for child in (2 * node + 1, 2 * node + 2):
                if child < len(root) and root[child] is not None:
                    nxt.append(child)
        level = nxt
    return out


# --- 56 Longest Palindromic Substring ---------------------------------------

def longest_palindrome(s):
    """Centre-outward expansion. Ties go to the leftmost, which the prompt says."""
    best_start, best_length = 0, 0
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                if hi - lo + 1 > best_length:
                    best_start, best_length = lo, hi - lo + 1
                lo -= 1
                hi += 1
    return s[best_start:best_start + best_length]


# --- 57 Unique Paths --------------------------------------------------------

def unique_paths(m, n):
    """m rows, n columns, moving only right or down, counting from the corner."""
    if m <= 0 or n <= 0:
        return 0
    row = [1] * n
    for _ in range(m - 1):
        for col in range(1, n):
            row[col] += row[col - 1]
    return row[-1]


# --- 58 Construct Binary Tree from Preorder and Inorder ---------------------

def level_encode(forest):
    """forest[i] is a (value, left, right) node or None, indexed by heap
    position. Returns the trimmed level-order array the question uses."""
    out = []

    def place(index, node):
        while len(out) <= index:
            out.append(None)
        if node is None:
            return
        value, left, right = node
        out[index] = value
        place(2 * index + 1, left)
        place(2 * index + 2, right)

    for index, node in enumerate(forest):
        place(index, node)
    while out and out[-1] is None:
        out.pop()
    return out


def build_nodes(preorder, inorder):
    """The tree as nested (value, left, right) tuples, or None.

    The first preorder value is the root; the moment it appears in the inorder
    list splits that list into the root's left and right subtrees, and the
    same split divides the rest of the preorder list.
    """
    if not preorder:
        return None
    root_value = preorder[0]
    pivot = inorder.index(root_value)
    left = build_nodes(preorder[1:1 + pivot], inorder[:pivot])
    right = build_nodes(preorder[1 + pivot:], inorder[pivot + 1:])
    return (root_value, left, right)


def build_tree(preorder, inorder):
    """The same tree in the level-order encoding the question uses."""
    root = build_nodes(preorder, inorder)
    if root is None:
        return []
    return level_encode([root])


# --- 59 Container With Most Water -------------------------------------------

def max_area(height):
    best = 0
    left, right = 0, len(height) - 1
    while left < right:
        best = max(best, min(height[left], height[right]) * (right - left))
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


# --- 60 Letter Combinations of a Phone Number -------------------------------

KEYS = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}


def letter_combinations(digits):
    """Leftmost key varies slowest, so the answer is in key order and then
    letter order. No digits, or a digit that is not a key, yields nothing."""
    if not digits or any(digit not in KEYS for digit in digits):
        return []
    out = [""]
    for digit in digits:
        out = [prefix + letter for prefix in out for letter in KEYS[digit]]
    return out


# --- 61 Word Search ---------------------------------------------------------

def word_search(board, word):
    if not word:
        return True
    if not board or not board[0]:
        return False

    def search(row, col, index):
        if board[row][col] != word[index]:
            return False
        if index == len(word) - 1:
            return True
        # A letter cannot be used twice in one word, so blank it while the
        # branch is open and put it back afterwards.
        saved = board[row][col]
        board[row][col] = None
        found = False
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            if (0 <= nr < len(board) and 0 <= nc < len(board[0])
                    and board[nr][nc] is not None):
                if search(nr, nc, index + 1):
                    found = True
                    break
        board[row][col] = saved
        return found

    for row in range(len(board)):
        for col in range(len(board[0])):
            if search(row, col, 0):
                return True
    return False


# --- 62 Find All Anagrams in a String ---------------------------------------

def find_anagrams(s, p):
    if not p or len(p) > len(s):
        return []
    need = [0] * 26
    for ch in p:
        need[ord(ch) - 97] += 1
    window = [0] * 26
    for ch in s[:len(p)]:
        window[ord(ch) - 97] += 1
    out = [0] if window == need else []
    for end in range(len(p), len(s)):
        window[ord(s[end]) - 97] += 1
        window[ord(s[end - len(p)]) - 97] -= 1
        if window == need:
            out.append(end - len(p) + 1)
    return out


# --- 63 Minimum Height Trees ------------------------------------------------

def min_height_trees(n, edges):
    if n <= 0:
        return []
    if n == 1:
        return [0]
    adjacency = [[] for _ in range(n)]
    for a, b in edges:
        adjacency[a].append(b)
        adjacency[b].append(a)
    degree = [len(neighbours) for neighbours in adjacency]
    leaves = deque(i for i in range(n) if degree[i] <= 1)
    remaining = n
    while remaining > 2:
        level = len(leaves)
        remaining -= level
        for _ in range(level):
            leaf = leaves.popleft()
            for neighbour in adjacency[leaf]:
                degree[neighbour] -= 1
                if degree[neighbour] == 1:
                    leaves.append(neighbour)
    return sorted(leaves)


# --- 64 Task Scheduler ------------------------------------------------------

def task_scheduler(tasks):
    """One unit of cooldown after each run of the same task.

    The answer is whichever is larger: doing nothing but the tasks, or the
    frames the most common tasks force. With `most` runs of the most common
    task and `kinds` tasks tied at that count, the schedule is `most - 1`
    frames of `kinds` slots plus one final frame of the `kinds` tasks.
    """
    if not tasks:
        return 0
    counts = {}
    for task in tasks:
        counts[task] = counts.get(task, 0) + 1
    most = max(counts.values())
    kinds = sum(1 for value in counts.values() if value == most)
    return max(len(tasks), (most - 1) * (kinds + 1) + kinds)


# --- 66 Kth Smallest Element in a BST --------------------------------------

def kth_smallest(root, k):
    """In-order without recursion: keep the path down the left spine, and
    after each pop step to the right subtree of the node just consumed."""
    if k < 1:
        return -1
    stack = []
    node = 0
    while True:
        while node < len(root) and root[node] is not None:
            stack.append(node)
            node = 2 * node + 1
        if not stack:
            return -1
        node = stack.pop()
        k -= 1
        if k == 0:
            return root[node]
        node = 2 * node + 2


# --- 67 Minimum Window Substring -------------------------------------------

def min_window(s, t):
    """Brute force on purpose: it is obviously right, which is the property
    the expectations need. Ties go to the leftmost, per the prompt."""
    if not t or len(t) > len(s):
        return ""
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    best = ""
    for start in range(len(s)):
        counts = {}
        for end in range(start, len(s)):
            ch = s[end]
            counts[ch] = counts.get(ch, 0) + 1
            if all(counts.get(k, 0) >= v for k, v in need.items()):
                if not best or end - start + 1 < len(best):
                    best = s[start:end + 1]
                break
    return best


# --- 69 Trapping Rain Water -------------------------------------------------

def trap(height):
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water


# --- 71 Word Ladder ---------------------------------------------------------

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def ladder_length(begin_word, end_word, word_list):
    """Breadth first over the one-letter-apart graph.

    Every word on a rung has to be in `word_list`, `end_word` included, so
    the end word is checked against the list before the search rather than
    discovered on the way. Skipping that check makes a ladder appear out of
    words that were never on the list.
    """
    if begin_word == end_word:
        return 1
    words = set(word_list)
    if end_word not in words:
        return 0
    frontier = {begin_word}
    seen = {begin_word}
    steps = 1
    while frontier:
        steps += 1
        nxt = set()
        for word in frontier:
            for i in range(len(word)):
                for ch in ALPHABET:
                    if ch == word[i]:
                        continue
                    candidate = word[:i] + ch + word[i + 1:]
                    if candidate == end_word:
                        return steps
                    if candidate in words and candidate not in seen:
                        seen.add(candidate)
                        nxt.add(candidate)
        frontier = nxt
    return 0


# --- 72 Basic Calculator ----------------------------------------------------

def calculate(s):
    """Plus, minus, parentheses, spaces, multi-digit operands.

    Two numbers are kept on a stack: the running total outside the current
    parentheses, and the sign that total gets applied with. A minus that is
    not attached to a number -- as in "-(2+3)" -- is absorbed by resetting the
    inner sign, which is why the sign is stored on its own rather than being
    read straight off the character.
    """
    total = 0
    sign = 1
    stack = []
    number = 0
    have_digit = False
    for ch in s:
        if "0" <= ch <= "9":
            number = number * 10 + (ord(ch) - 48)
            have_digit = True
        elif ch in "+-":
            if have_digit:
                total += sign * number
            number = 0
            have_digit = False
            sign = 1 if ch == "+" else -1
        elif ch == "(":
            stack.append(total)
            stack.append(sign)
            total = 0
            sign = 1
        elif ch == ")":
            if have_digit:
                total += sign * number
            number = 0
            have_digit = False
            total = stack[-2] + stack[-1] * total
            stack.pop()
            stack.pop()
            sign = 1
    if have_digit:
        total += sign * number
    return total


# --- 73 Maximum Profit in Job Scheduling ------------------------------------

def max_profit(start_time, end_time, profit):
    """Jobs are half-open: a job ending at t does not block one starting at t.
    That is why the compatibility test is `end <= start` and not `end < start`."""
    jobs = sorted(zip(start_time, end_time, profit))
    # best[i] is the most profit from the first i jobs in end-time order.
    best = [0] * (len(jobs) + 1)
    for i, (start, end, money) in enumerate(jobs):
        # The highest-numbered job that finishes at or before this one starts.
        # Sorted by (start, end), so this scan can stop as soon as a job that
        # starts after `start` is reached -- nothing further along can fit.
        earlier = 0
        for j, (other_start, other_end, _) in enumerate(jobs):
            if other_start > start:
                break
            if other_end <= start:
                earlier = max(earlier, j + 1)
        best[i + 1] = max(best[i], best[earlier] + money)
    return best[len(jobs)]


# --- 74 Merge k Sorted Lists ------------------------------------------------

def merge_k_sorted(lists):
    out = []
    for row in lists:
        out.extend(row)
    out.sort()
    return out


# --- 75 Largest Rectangle in Histogram --------------------------------------

def largest_rectangle(heights):
    """A stack of indices with increasing heights. When a shorter bar arrives
    it closes every taller bar on top of it, and the popped bar's width runs
    from just past the new top of the stack up to the current position."""
    best = 0
    stack = []
    for i in range(len(heights) + 1):
        current = heights[i] if i < len(heights) else 0
        while stack and heights[stack[-1]] >= current:
            height = heights[stack.pop()]
            left = stack[-1] if stack else -1
            best = max(best, height * (i - left - 1))
        stack.append(i)
    return best


CASES = {
    "word_break": [
        (["leetcode", ["leet", "code"]], "bool"),
        (["applepenapple", ["apple", "pen"]], "bool"),
        (["catsandog", ["cats", "dog", "sand", "and", "cat"]], "bool"),
        (["abc", ["a", "b", "c"]], "bool"),
        (["aaaaaaa", ["aaa", "aaaa"]], "bool"),
        (["iloveyou", ["i", "love", "you"]], "bool"),
        (["a", ["b"]], "bool"),
        (["cars", ["car", "ca", "rs"]], "bool"),
        (["", ["a"]], "bool"),
    ],
    "can_partition": [
        ([[1, 5, 11, 5]], "bool"),
        ([[1, 2, 3, 5]], "bool"),
        ([[1]], "bool"),
        ([[2, 2]], "bool"),
        ([[1, 2, 5]], "bool"),
        ([[1, 2, 3]], "bool"),
        ([[100, 100]], "bool"),
        ([[3, 3, 3, 4, 5]], "bool"),
        ([[1, 4, 5, 6]], "bool"),
        ([[8, 1]], "bool"),
    ],
    "atoi": [
        (["42"], "int"),
        (["   -042"], "int"),
        (["1337c0d3"], "int"),
        (["0-1"], "int"),
        (["words and 987"], "int"),
        (["-91283472332"], "int"),
        (["91283472332"], "int"),
        ([""], "int"),
        (["+-12"], "int"),
        (["  +  413"], "int"),
        (["-2147483648"], "int"),
        (["2147483647"], "int"),
        (["2147483648"], "int"),
    ],
    "spiral_matrix": [
        ([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "matrix"),
        ([[[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]], "matrix"),
        ([[[1], [2], [3]]], "matrix"),
        ([[[1, 2, 3, 4], [5, 6, 7, 8]]], "matrix"),
        ([[[1, 2], [3, 4]]], "matrix"),
        ([[[7]]], "matrix"),
        ([[[1, 2, 3]]], "matrix"),
        ([[]], "matrix"),
    ],
    "subsets": [
        ([[1, 2, 3]], "matrix"),
        ([[0]], "matrix"),
        ([[1]], "matrix"),
        ([[1, 2]], "matrix"),
        ([[-1]], "matrix"),
        ([[]], "matrix"),
    ],
    "right_side_view": [
        ([[1, 2, 3, None, 5, None, 4]], "array"),
        ([[1, None, 3, None, 5]], "array"),
        ([[1, 2, 3]], "array"),
        ([[]], "array"),
        ([[1]], "array"),
        ([[1, 2, 3, 4, None, None, 5]], "array"),
        ([[1, None, 2, 3]], "array"),
    ],
    "longest_palindrome": [
        (["babad"], "string"),
        (["cbbd"], "string"),
        (["a"], "string"),
        (["ac"], "string"),
        ([""], "string"),
        (["aaaa"], "string"),
        (["forgeeksskeegfor"], "string"),
        (["abacdfgdcaba"], "string"),
        (["abcda"], "string"),
        (["aacabdkacaa"], "string"),
    ],
    "unique_paths": [
        ([3, 7], "int"),
        ([3, 2], "int"),
        ([1, 1], "int"),
        ([7, 3], "int"),
        ([3, 3], "int"),
        ([1, 10], "int"),
        ([0, 5], "int"),
        ([5, 0], "int"),
    ],
    "build_tree": [
        ([[3, 9, 20, 15, 7], [9, 3, 15, 20, 7]], "tree"),
        ([[-1], [-1]], "tree"),
        ([[1], [1]], "tree"),
        ([[3, 9, 5, 20, 15, 7], [5, 9, 3, 15, 20, 7]], "tree"),
        ([[1], [1, 2]], "tree"),
    ],
    "max_area": [
        ([[1, 8, 7, 6, 2, 5, 4, 8, 3, 7]], "int"),
        ([[1, 1]], "int"),
        ([[4, 3, 2, 1, 4, 1, 2, 3, 1, 2, 1, 5, 4, 2]], "int"),
        ([[1, 2, 1]], "int"),
        ([[1, 2, 4, 3]], "int"),
        ([[5]], "int"),
    ],
    "letter_combinations": [
        (["23"], "strarray"),
        ([""], "strarray"),
        (["2"], "strarray"),
        (["79"], "strarray"),
        (["234"], "strarray"),
    ],
    "word_search": [
        ([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"], "bool"),
        ([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "SEE"], "bool"),
        ([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"], "bool"),
        ([[["a", "b"], ["c", "d"]], "ab"], "bool"),
        ([[["a", "b"], ["c", "d"]], "abc"], "bool"),
        ([[["A"]], "A"], "bool"),
        ([[["A"]], "B"], "bool"),
        ([[], "A"], "bool"),
    ],
    "find_anagrams": [
        (["cbaebabacd", "abc"], "array"),
        (["abab", "ab"], "array"),
        (["aaaaaaaaaa", "a"], "array"),
        (["abc", "wxyz"], "array"),
        (["aaa", "a"], "array"),
        (["ab", "ab"], "array"),
    ],
    "min_height_trees": [
        ([6, [[0, 1], [0, 2], [3, 4], [5, 4]]], "array"),
        ([4, [[0, 1], [1, 2], [1, 3]]], "array"),
        ([2, [[0, 1]]], "array"),
        ([1, []], "array"),
        ([3, [[0, 1], [1, 2]]], "array"),
        ([7, [[0, 1], [0, 2], [0, 3], [1, 4], [2, 5], [3, 6]]], "array"),
    ],
    "task_scheduler": [
        ([["A", "A", "A", "B", "B", "B"]], "int"),
        ([["A", "B", "C", "D", "D", "D", "D", "E", "E", "E", "F", "F"]], "int"),
        ([["A", "A", "A", "B", "B", "B", "C", "C", "C", "C", "C"]], "int"),
        ([["A", "A", "A", "B", "B", "B", "C", "C", "C", "C", "C", "C"]], "int"),
        ([["A", "A", "A", "A", "A", "A", "A", "A"]], "int"),
        ([["A"]], "int"),
    ],
    "kth_smallest": [
        ([[3, 1, 4, None, 2], 1], "int"),
        ([[5, 3, 6, 2, 4, None, None, 1], 3], "int"),
        ([[2, 1, 3], 2], "int"),
        ([[2, 1, 3], 1], "int"),
        ([[2, 1, 3], 3], "int"),
        ([[1], 1], "int"),
        ([[1, 2], 1], "int"),
    ],
    "min_window": [
        (["ADOBECODEBANC", "ABC"], "string"),
        (["a", "a"], "string"),
        (["a", "aa"], "string"),
        (["ab", "b"], "string"),
        (["bba", "ab"], "string"),
    ],
    "trap": [
        ([[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], "int"),
        ([[4, 2, 0, 3, 2, 5]], "int"),
        ([[]], "int"),
        ([[5]], "int"),
        ([[3, 2, 1, 0, 4]], "int"),
        ([[2, 0, 2]], "int"),
    ],
    "ladder_length": [
        (["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]], "int"),
        (["hit", "cog", ["hot", "dot", "dog", "lot", "log"]], "int"),
        (["a", "c", ["a", "b", "c"]], "int"),
        (["hot", "dog", ["hot", "dog"]], "int"),
        (["aa", "bb", ["aa", "ab", "bb"]], "int"),
    ],
    "calculate": [
        (["1 + 2"], "int"),
        ([" 2-1 + 2 "], "int"),
        (["(1+(4+5+2)-3)+(6+8)"], "int"),
        (["-2+ 6"], "int"),
        (["2147483647"], "int"),
        (["-(2+3)"], "int"),
        (["1-(2+3)"], "int"),
        (["(1)"], "int"),
        (["10-(5+6)"], "int"),
        (["2-(5-6)"], "int"),
    ],
    "max_profit": [
        ([[1, 2, 3, 3], [3, 4, 5, 6], [2, 7, 9, 3]], "int"),
        ([[1, 2, 3], [2, 3, 5], [0, 6, 8]], "int"),
        ([[1, 2, 3], [2, 3, 4], [3, 4, 5]], "int"),
        ([[1, 2, 1], [2, 3, 2], [3, 4, 1]], "int"),
    ],
    "merge_k_sorted": [
        ([[[1, 4, 5], [1, 3, 4], [2, 6]]], "list"),
        ([[[], []]], "list"),
        ([[[]]], "list"),
        ([[[1]]], "list"),
        ([[[-1], [0], [1]]], "list"),
    ],
    "largest_rectangle": [
        ([[2, 1, 5, 6, 2, 3]], "int"),
        ([[2, 4]], "int"),
        ([[]], "int"),
        ([[1, 1, 1, 1]], "int"),
        ([[5, 4, 3, 2, 1]], "int"),
        ([[2, 1, 2]], "int"),
    ],
}


def _spawn(value):
    """Deep-copy the list-shaped arguments, because word_search blanks its
    board in place and must not scribble on the case table."""
    if isinstance(value, list):
        return [_spawn(item) for item in value]
    return value


def main():
    failures = 0
    for name, cases in CASES.items():
        func = globals()[name]
        print(f"--- {name} ---")
        for args, _kind in cases:
            try:
                value = func(*[_spawn(a) for a in args])
                print(f"  {json.dumps(args)} -> {json.dumps(value)}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"  {json.dumps(args)} -> !! {exc}")
    if failures:
        raise SystemExit(f"{failures} case(s) raised")


if __name__ == "__main__":
    main()
