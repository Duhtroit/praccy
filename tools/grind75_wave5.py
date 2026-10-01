#!/usr/bin/env python3
"""Grind 75, wave 5: positions 50-61.

None of the twelve positions in this range is a skipped design problem, so all
twelve are here. Every expectation came out of `tools/_ref_wave56.py` rather
than from memory.

That file earned its place before a single question was written. Its first
draft contained a Right Side View that returned the leftmost node of each
level, a Kth Smallest whose index arithmetic walked off the end of the tree, a
Construct Tree that handed its root to the level-order encoder as though it
were a child, and a Word Ladder that built a path through words which were
never on the list. Four wrong answers caught before any of five languages had
to be written against them.

Two positions in this range are a problem of a different kind. Container With
Most Water at 59 and Trapping Rain Water at 69 were already in the catalogue
from the original LeetCode set, under their own ids and their own much thinner
prompts. `build_grind75.py` stamps their canonical positions onto those
questions rather than adding a second copy of the same problem -- the same
treatment Two Sum and Valid Anagram get.

So this file holds ten, and the two adopted ones make twelve.

A few of the questions here earn a contract type they did not previously have,
which is the point of walking the list in order:

Word Search takes a `charmatrix` -- a grid whose cells are single characters --
and returns a boolean, so it needs no new type on the way out. It is the first
practice question to take one, and the first to have to blank a cell and put it
back while searching, which is where the interesting bug lives.

Letter Combinations returns a `strarray`, and Subsets and Spiral Matrix return
`matrix`, so this is the first wave where a question returns a list of lists of
words or a flattened grid.
"""

from __future__ import annotations

from grind75_common import (ALGO, ARR, BOOL, CHARMATRIX, DP, INT, LC, LIST, MATRIX,
                            MATRIX_NOTE, SEARCH, SM, STRETCH, STR, STRARRAY, TREE,
                            TREE_NOTE, TREE_TAG, c, q, S)

QUESTIONS = [
    q("g-word-break", "Word Break", STRETCH, [DP, SM, "backtracking"],
      "WordBreak",
      "Have the function WordBreak(str, words) take a string and a list of "
      "dictionary words and return the boolean true if the string can be broken "
      "into words from the list, otherwise return false.\n\nThe break has to be "
      "somewhere, and the words are used in the order they appear in the string, "
      "so the pieces can be reused as often as they appear. The empty string is "
      "made of nothing, which is always a valid break.\n\nThe useful way to "
      "think about it is from the left. Ask, for every position, whether the "
      "text up to that position can be broken; position zero always can, "
      "because the empty text is a break. Then a position can if some word ends "
      "exactly there and the text before that word can. Checking only whether "
      "whole prefixes are in the dictionary is the mistake -- the words in a "
      "valid break do not have to line up with the start of the string.",
      (["str", "words"], [STR, STRARRAY]),
      [c(["leetcode", ["leet", "code"]], True, BOOL),
       c(["applepenapple", ["apple", "pen"]], True, BOOL),
       c(["catsandog", ["cats", "dog", "sand", "and", "cat"]], False, BOOL),
       c(["abc", ["a", "b", "c"]], True, BOOL),
       c(["aaaaaaa", ["aaa", "aaaa"]], True, BOOL),
       c(["iloveyou", ["i", "love", "you"]], True, BOOL),
       c(["cars", ["car", "ca", "rs"]], True, BOOL),
       c(["a", ["b"]], False, BOOL),
       c(["", ["a"]], True, BOOL)],
      S('''def WordBreak(str, words):
    # reach[end] is true when str[:end] splits into dictionary words, so the
    # answer to "is there a word ending here" is reach[start] and membership.
    reach = [False] * (len(str) + 1)
    reach[0] = True
    for end in range(1, len(str) + 1):
        for start in range(end):
            if reach[start] and str[start:end] in words:
                reach[end] = True
                break
    return reach[len(str)]
''',
        """
bool WordBreak(const string& str, const vector<string>& words) {
  set<string> dictionary(words.begin(), words.end());
  int n = (int)str.size();
  vector<bool> reach(n + 1, false);
  reach[0] = true;
  for (int end = 1; end <= n; ++end) {
    for (int start = 0; start < end; ++start) {
      if (reach[start] && dictionary.count(str.substr(start, end - start))) {
        reach[end] = true;
        break;
      }
    }
  }
  return reach[n];
}
""",
        """
public class Solution
{
    public static bool WordBreak(string str, string[] words)
    {
        var dictionary = new System.Collections.Generic.HashSet<string>(words);
        int n = str.Length;
        var reach = new bool[n + 1];
        reach[0] = true;
        for (int end = 1; end <= n; end++)
        {
            for (int start = 0; start < end; start++)
            {
                if (reach[start] && dictionary.Contains(str.Substring(start, end - start)))
                {
                    reach[end] = true;
                    break;
                }
            }
        }
        return reach[n];
    }
}
""",
        """
public class Solution {
    public static boolean wordBreak(String str, String[] words) {
        java.util.Set<String> dictionary =
            new java.util.HashSet<>(java.util.Arrays.asList(words));
        int n = str.length();
        boolean[] reach = new boolean[n + 1];
        reach[0] = true;
        for (int end = 1; end <= n; end++) {
            for (int start = 0; start < end; start++) {
                if (reach[start] && dictionary.contains(str.substring(start, end))) {
                    reach[end] = true;
                    break;
                }
            }
        }
        return reach[n];
    }
}
"""),
      position=50, source=LC, sourceId=139,
      sourceNote="LeetCode 139 (Medium). Asking whether each prefix is a dictionary word gets the first case and fails the rest; what propagates is reachability, not membership."),

    q("g-can-partition", "Partition Equal Subset Sum", STRETCH, [DP, "arrays"],
      "CanPartition",
      "Have the function CanPartition(nums) take a list of positive integers and "
      "return the boolean true if the numbers can be split into two groups of "
      "equal sum, otherwise return false.\n\nBoth groups have to use every "
      "number, and a number cannot be in both. So the question is not whether "
      "some subset sums to half the total -- it is whether the rest of the "
      "numbers also do, which is automatic once one of them does. A total that "
      "is odd can never split, and a single number never can either.\n\nThe "
      "trick is that there is only one question left to answer: can some subset "
      "sum to exactly half? One table of reachable sums does it, and the sum "
      "that has to be reached is half the total, which is always less than the "
      "largest number in a list that cannot split.",
      (["nums"], [ARR]),
      [c([[1, 5, 11, 5]], True, BOOL),
       c([[1, 2, 3, 5]], False, BOOL),
       c([[1, 2, 3]], True, BOOL),
       c([[2, 2]], True, BOOL),
       c([[1, 2, 5]], False, BOOL),
       c([[1]], False, BOOL),
       c([[100, 100]], True, BOOL),
       c([[3, 3, 3, 4, 5]], True, BOOL),
       c([[1, 4, 5, 6]], False, BOOL),
       c([[8, 1]], False, BOOL)],
      S('''def CanPartition(nums):
    total = sum(nums)
    if total % 2:
        return False
    half = total // 2
    # possible[target] is true when some subset of the numbers seen so far
    # adds up to target. Descending, so each number is used at most once.
    possible = [False] * (half + 1)
    possible[0] = True
    for value in nums:
        for target in range(half, value - 1, -1):
            if possible[target - value]:
                possible[target] = True
    return possible[half]
''',
        """
bool CanPartition(const vector<int>& nums) {
  int total = 0;
  for (int value : nums) total += value;
  if (total % 2) return false;
  int half = total / 2;
  vector<bool> possible(half + 1, false);
  possible[0] = true;
  for (int value : nums) {
    // Descending: ascending would let this number be spent twice.
    for (int target = half; target >= value; --target)
      if (possible[target - value]) possible[target] = true;
  }
  return possible[half];
}
""",
        """
public class Solution
{
    public static bool CanPartition(int[] nums)
    {
        int total = 0;
        foreach (int value in nums) total += value;
        if (total % 2 != 0) return false;
        int half = total / 2;
        var possible = new bool[half + 1];
        possible[0] = true;
        foreach (int value in nums)
            for (int target = half; target >= value; target--)
                if (possible[target - value]) possible[target] = true;
        return possible[half];
    }
}
""",
        """
public class Solution {
    public static boolean canPartition(int[] nums) {
        int total = 0;
        for (int value : nums) total += value;
        if (total % 2 != 0) return false;
        int half = total / 2;
        boolean[] possible = new boolean[half + 1];
        possible[0] = true;
        for (int value : nums)
            for (int target = half; target >= value; target--)
                if (possible[target - value]) possible[target] = true;
        return possible[half];
    }
}
"""),
      position=51, source=LC, sourceId=416,
      sourceNote="LeetCode 416 (Medium). The subset-sum table runs downwards; running it upwards lets one number pay for itself twice and the answer comes out too high."),

    q("g-atoi", "String to Integer (atoi)", STRETCH, [SM, "parsing"], "Atoi",
      "Have the function Atoi(str) take a string of text and return the whole "
      "number it starts with.\n\nThe rules, in order. Leading spaces are "
      "skipped. Then there may be one sign, + or -, and nothing else -- a second "
      "sign means the string does not start with a number at all. Then come the "
      "digits, and the number ends at the first character that is not a digit. "
      "If no digits were read the answer is 0, so text with a number in the "
      "middle of it converts to 0 rather than to that number. Finally the result "
      "is clamped to the range a 32 bit signed integer can hold: 2147483647 at "
      "the top and -2147483648 at the bottom. \n\nThe "
      "clamping has to happen even when the digits are not finished, which is "
      "why the accumulator is allowed to run past the limit and is trimmed once "
      "at the end.",
      (["str"], [STR]),
      [c(["42"], 42, INT),
       c(["   -042"], -42, INT),
       c(["1337c0d3"], 1337, INT),
       c(["0-1"], 0, INT),
       c(["words and 987"], 0, INT),
       c(["+-12"], 0, INT),
       c(["  +  413"], 0, INT),
       c(["-2147483648"], -2147483648, INT),
       c(["2147483647"], 2147483647, INT),
       c(["2147483648"], 2147483647, INT),
       c(["-91283472332"], -2147483648, INT),
       c(["91283472332"], 2147483647, INT),
       c([""], 0, INT)],
      S('''def Atoi(str):
    INT_MAX, INT_MIN = 2 ** 31 - 1, -(2 ** 31)
    index = 0
    n = len(str)
    while index < n and str[index] == " ":
        index += 1
    sign = 1
    if index < n and str[index] in "+-":
        # One sign only. A second sign falls through to the digit loop, which
        # reads nothing, and the answer is 0.
        if str[index] == "-":
            sign = -1
        index += 1
    value = 0
    digits = 0
    while index < n and str[index].isdigit():
        value = value * 10 + int(str[index])
        digits += 1
        index += 1
    if digits == 0:
        return 0
    return max(INT_MIN, min(INT_MAX, sign * value))
''',
        """
int Atoi(const string& str) {
  // Not named INT_MAX/INT_MIN: those are macros in <climits>, which the
  // harness's own includes pull in, and redefining one is a compile error.
  const long long LIMIT_HIGH = 2147483647LL, LIMIT_LOW = -2147483648LL;
  size_t index = 0, n = str.size();
  while (index < n && str[index] == ' ') ++index;
  int sign = 1;
  if (index < n && (str[index] == '+' || str[index] == '-')) {
    if (str[index] == '-') sign = -1;
    ++index;
  }
  long long value = 0;
  int digits = 0;
  // long long, so an eleven digit number does not overflow before the clamp.
  while (index < n && str[index] >= '0' && str[index] <= '9') {
    value = value * 10 + (str[index] - '0');
    ++digits;
    ++index;
  }
  if (digits == 0) return 0;
  value *= sign;
  if (value > LIMIT_HIGH) return (int)LIMIT_HIGH;
  if (value < LIMIT_LOW) return (int)LIMIT_LOW;
  return (int)value;
}
""",
        """
public class Solution
{
    public static int Atoi(string str)
    {
        const long INT_MAX = 2147483647L, INT_MIN = -2147483648L;
        int index = 0, n = str.Length;
        while (index < n && str[index] == ' ') index++;
        int sign = 1;
        if (index < n && (str[index] == '+' || str[index] == '-'))
        {
            if (str[index] == '-') sign = -1;
            index++;
        }
        // long, so an eleven digit number does not overflow before the clamp.
        long value = 0;
        int digits = 0;
        while (index < n && str[index] >= '0' && str[index] <= '9')
        {
            value = value * 10 + (str[index] - '0');
            digits++;
            index++;
        }
        if (digits == 0) return 0;
        value *= sign;
        if (value > INT_MAX) return (int)INT_MAX;
        if (value < INT_MIN) return (int)INT_MIN;
        return (int)value;
    }
}
""",
        """
public class Solution {
    public static int atoi(String str) {
        final long INT_MAX = 2147483647L, INT_MIN = -2147483648L;
        int index = 0, n = str.length();
        while (index < n && str.charAt(index) == ' ') index++;
        int sign = 1;
        if (index < n && (str.charAt(index) == '+' || str.charAt(index) == '-')) {
            if (str.charAt(index) == '-') sign = -1;
            index++;
        }
        long value = 0;
        int digits = 0;
        while (index < n && str.charAt(index) >= '0' && str.charAt(index) <= '9') {
            value = value * 10 + (str.charAt(index) - '0');
            digits++;
            index++;
        }
        if (digits == 0) return 0;
        value *= sign;
        if (value > INT_MAX) return (int) INT_MAX;
        if (value < INT_MIN) return (int) INT_MIN;
        return (int) value;
    }
}
"""),
      position=52, source=LC, sourceId=8,
      sourceNote="LeetCode 8 (Medium). Three separate failure modes hide here: no digits read at all, a second sign, and a value past the 32 bit range. The accumulator has to be wider than the answer."),

    q("g-spiral-matrix", "Spiral Matrix", STRETCH, [ALGO, "matrix", "simulation"],
      "SpiralMatrix",
      "Have the function SpiralMatrix(matrix) take a grid of numbers and return "
      "every value in the order a spiral would visit them: across the top row "
      "left to right, down the right column, back across the bottom row right "
      "to left, up the left column, and then inward on what is left. The answer "
      "is one flat list of every value, not a list of rows.\n\n"
      + MATRIX_NOTE +
      "\n\nThe whole question is four pointers, and they do not all move at "
      "the same rate. Walking the top row moves the top pointer down by one. "
      "Walking the right column moves the right pointer left by one. The bottom "
      "row and the left column are only walked if anything is left to walk -- "
      "on a single row or a single column the other two walks would step "
      "outside the grid and duplicate what has already been taken. A grid of "
      "one row is the case that catches this: the top row takes everything, and "
      "nothing after it may take anything again.",
      (["matrix"], [MATRIX]),
      [c([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], [1, 2, 3, 6, 9, 8, 7, 4, 5], LIST),
       c([[[1, 2, 3, 4], [5, 6, 7, 8]]], [1, 2, 3, 4, 8, 7, 6, 5], LIST),
       c([[[1, 2], [3, 4]]], [1, 2, 4, 3], LIST),
       c([[[1], [2], [3]]], [1, 2, 3], LIST),
       c([[[1, 2, 3]]], [1, 2, 3], LIST),
       c([[[7]]], [7], LIST),
       c([[[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]]],
         [1, 1, 1, 1, 2, 3, 3, 3, 3, 2, 2, 2], LIST),
       c([[]], [], LIST)],
      S('''def SpiralMatrix(matrix):
    if not matrix or not matrix[0]:
        return []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        for column in range(left, right + 1):
            out.append(matrix[top][column])
        top += 1
        for row in range(top, bottom + 1):
            out.append(matrix[row][right])
        right -= 1
        # The bottom row and the left column are only walked when the ring is
        # still a ring. After a single row the top is already past the bottom.
        if top <= bottom:
            for column in range(right, left - 1, -1):
                out.append(matrix[bottom][column])
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                out.append(matrix[row][left])
            left += 1
    return out
''',
        """
vector<int> SpiralMatrix(const vector<vector<int>>& matrix) {
  vector<int> out;
  if (matrix.empty() || matrix[0].empty()) return out;
  int top = 0, bottom = (int)matrix.size() - 1;
  int left = 0, right = (int)matrix[0].size() - 1;
  while (top <= bottom && left <= right) {
    for (int column = left; column <= right; ++column)
      out.push_back(matrix[top][column]);
    ++top;
    for (int row = top; row <= bottom; ++row)
      out.push_back(matrix[row][right]);
    --right;
    // Only walk the last two sides if there is still a ring to walk.
    if (top <= bottom) {
      for (int column = right; column >= left; --column)
        out.push_back(matrix[bottom][column]);
      --bottom;
    }
    if (left <= right) {
      for (int row = bottom; row >= top; --row)
        out.push_back(matrix[row][left]);
      ++left;
    }
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[] SpiralMatrix(int[][] matrix)
    {
        var outp = new System.Collections.Generic.List<int>();
        if (matrix.Length == 0 || matrix[0].Length == 0) return outp.ToArray();
        int top = 0, bottom = matrix.Length - 1;
        int left = 0, right = matrix[0].Length - 1;
        while (top <= bottom && left <= right)
        {
            for (int column = left; column <= right; column++)
                outp.Add(matrix[top][column]);
            top++;
            for (int row = top; row <= bottom; row++)
                outp.Add(matrix[row][right]);
            right--;
            if (top <= bottom)
            {
                for (int column = right; column >= left; column--)
                    outp.Add(matrix[bottom][column]);
                bottom--;
            }
            if (left <= right)
            {
                for (int row = bottom; row >= top; row--)
                    outp.Add(matrix[row][left]);
                left++;
            }
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[] spiralMatrix(int[][] matrix) {
        java.util.List<Integer> out = new java.util.ArrayList<>();
        if (matrix.length == 0 || matrix[0].length == 0)
            return new int[0];
        int top = 0, bottom = matrix.length - 1;
        int left = 0, right = matrix[0].length - 1;
        while (top <= bottom && left <= right) {
            for (int column = left; column <= right; column++)
                out.add(matrix[top][column]);
            top++;
            for (int row = top; row <= bottom; row++)
                out.add(matrix[row][right]);
            right--;
            if (top <= bottom) {
                for (int column = right; column >= left; column--)
                    out.add(matrix[bottom][column]);
                bottom--;
            }
            if (left <= right) {
                for (int row = bottom; row >= top; row--)
                    out.add(matrix[row][left]);
                left++;
            }
        }
        int[] result = new int[out.size()];
        for (int i = 0; i < result.length; i++) result[i] = out.get(i);
        return result;
    }
}
"""),
      position=53, source=LC, sourceId=54,
      sourceNote="LeetCode 54 (Medium). The bottom and left walks need their own guards, or a one-row grid hands back the row twice."),

    q("g-subsets", "Subsets", STRETCH, [ALGO, "backtracking"], "Subsets",
      "Have the function Subsets(nums) take a list of distinct integers and "
      "return every subset of it, each subset as a list, including the empty "
      "one.\n\n" + MATRIX_NOTE +
      "\n\nBecause the comparison is order-sensitive, the order of the answer "
      "is part of the question. The subsets come back with the empty one first, "
      "and then for each number in turn, every subset built so far followed by "
      "that same subset with the number added. For [1, 2, 3] that is the empty "
      "subset, then [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3].\n\nThe "
      "rule underneath is that a subset either contains the current number or "
      "it does not, and both halves are already known. A set of three numbers "
      "has eight subsets, not six: a doubling per number, starting from the one "
      "empty subset.",
      (["nums"], [ARR]),
      [c([[1, 2, 3]], [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]], MATRIX),
       c([[1, 2]], [[], [1], [2], [1, 2]], MATRIX),
       c([[0]], [[], [0]], MATRIX),
       c([[1]], [[], [1]], MATRIX),
       c([[-1]], [[], [-1]], MATRIX),
       c([[]], [[]], MATRIX)],
      S('''def Subsets(nums):
    out = [[]]
    for value in nums:
        # The subsets not using this value, then the same ones using it. A
        # comprehension over `out` rather than over a growing list, so the
        # two halves cannot see each other.
        out = out + [subset + [value] for subset in out]
    return out
''',
        """
vector<vector<int>> Subsets(const vector<int>& nums) {
  vector<vector<int>> out{{}};
  for (int value : nums) {
    size_t before = out.size();
    for (size_t i = 0; i < before; ++i) {
      vector<int> extended = out[i];
      extended.push_back(value);
      out.push_back(extended);
    }
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[][] Subsets(int[] nums)
    {
        var outp = new System.Collections.Generic.List<int[]>();
        outp.Add(new int[0]);
        foreach (int value in nums)
        {
            // Snapshot the count: only the subsets that existed before this
            // value are extended.
            int before = outp.Count;
            for (int i = 0; i < before; i++)
            {
                var extended = new System.Collections.Generic.List<int>(outp[i]);
                extended.Add(value);
                outp.Add(extended.ToArray());
            }
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[][] subsets(int[] nums) {
        java.util.List<int[]> out = new java.util.ArrayList<>();
        out.add(new int[0]);
        for (int value : nums) {
            int before = out.size();
            for (int i = 0; i < before; i++) {
                int[] extended = java.util.Arrays.copyOf(out.get(i), out.get(i).length + 1);
                extended[extended.length - 1] = value;
                out.add(extended);
            }
        }
        return out.toArray(new int[0][]);
    }
}
"""),
      position=54, source=LC, sourceId=78,
      sourceNote="LeetCode 78 (Medium). The count doubles per number, so the answer is 2^n and a solution that returns 2^(n-1) has dropped the empty subset."),

    q("g-right-side-view", "Binary Tree Right Side View", STRETCH, [TREE_TAG, "trees"],
      "RightSideView",
      "Have the function RightSideView(root) take a binary tree and return the "
      "value you would see looking at it from the right: the rightmost node of "
      "each level, from the root down.\n\n" + TREE_NOTE +
      "\n\nOne level at a time, and the answer for a level is the last node of "
      "it. If the children are visited left first and then right, the nodes of "
      "a level are collected in left-to-right order, and the rightmost one is "
      "the last -- which is why the same walk gives the left side view by "
      "taking the first instead.\n\nThere is also a version that walks the "
      "tree depth first, keeping the first node reached at each depth and "
      "overwriting it every time a shallower one is found. That works because "
      "depth first reaches a deeper node before a shallower one, so the shallow "
      "arrival is always the later of the two -- and it is the more interesting "
      "of the two to write.",
      (["root"], [TREE]),
      [c([[1, 2, 3, None, 5, None, 4]], [1, 3, 4], ARR),
       c([[1, None, 3, None, 5]], [1, 3], ARR),
       c([[1, 2, 3]], [1, 3], ARR),
       c([[1, 2, 3, 4, None, None, 5]], [1, 3, 5], ARR),
       c([[1, None, 2, 3]], [1, 2], ARR),
       c([[1]], [1], ARR),
       c([[]], [], ARR)],
      S('''def RightSideView(root):
    if not root:
        return []
    out = []
    level = [0]
    while level:
        # Children were appended left first, so the last node of the level is
        # its rightmost.
        out.append(root[level[-1]])
        nxt = []
        for node in level:
            for child in (2 * node + 1, 2 * node + 2):
                if child < len(root) and root[child] is not None:
                    nxt.append(child)
        level = nxt
    return out
''',
        """
vector<int> RightSideView(const vector<optional<int>>& root) {
  vector<int> out;
  if (root.empty()) return out;
  vector<size_t> level{0};
  while (!level.empty()) {
    // Children were appended left first, so the back of the level is the
    // rightmost node of it.
    out.push_back(*root[level.back()]);
    vector<size_t> nxt;
    for (size_t node : level) {
      for (size_t child : {(size_t)(2 * node + 1), (size_t)(2 * node + 2)}) {
        if (child < root.size() && root[child].has_value()) nxt.push_back(child);
      }
    }
    level = nxt;
  }
  return out;
}
""",
        """
public class Solution
{
    public static int[] RightSideView(int?[] root)
    {
        var outp = new System.Collections.Generic.List<int>();
        if (root.Length == 0) return outp.ToArray();
        var level = new System.Collections.Generic.List<int> { 0 };
        while (level.Count > 0)
        {
            outp.Add(root[level[level.Count - 1]].Value);
            var nxt = new System.Collections.Generic.List<int>();
            foreach (int node in level)
            {
                int left = 2 * node + 1, right = 2 * node + 2;
                if (left < root.Length && root[left].HasValue) nxt.Add(left);
                if (right < root.Length && root[right].HasValue) nxt.Add(right);
            }
            level = nxt;
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static int[] rightSideView(Integer[] root) {
        java.util.List<Integer> out = new java.util.ArrayList<>();
        if (root.length == 0) return new int[0];
        java.util.List<Integer> level = new java.util.ArrayList<>();
        level.add(0);
        while (!level.isEmpty()) {
            // Integer[] unboxes to int, so the list holds Integers and the
            // add takes the unboxed value rather than the boxed one.
            out.add(root[level.get(level.size() - 1)]);
            java.util.List<Integer> next = new java.util.ArrayList<>();
            for (int node : level) {
                int left = 2 * node + 1, right = 2 * node + 2;
                if (left < root.length && root[left] != null) next.add(left);
                if (right < root.length && root[right] != null) next.add(right);
            }
            level = next;
        }
        int[] result = new int[out.size()];
        for (int i = 0; i < result.length; i++) result[i] = out.get(i);
        return result;
    }
}
"""),
      position=55, source=LC, sourceId=199,
      sourceNote="LeetCode 199 (Medium). Taking the first node of each level instead of the last answers Binary Tree Left Side View, which is the same walk read backwards."),

    q("g-longest-palindromic-substring", "Longest Palindromic Substring",
      STRETCH, [SM, "two pointers"],
      "LongestPalindromicSubstring",
      "Have the function LongestPalindromicSubstring(str) take a string and "
      "return its longest substring that reads the same forwards and backwards. "
      "A substring is a run of characters with nothing skipped, so the answer is "
      "a piece of the original string and not a rearrangement of it.\n\nWhen "
      "two palindromes are the same length, return the one that starts earlier. "
      "\"babad\" therefore gives \"bab\" and not \"aba\", and the empty "
      "string gives itself.\n\nEvery palindrome has a middle, and the middle "
      "is either one character or the gap between two. So try every character as "
      "a middle and every gap as a middle, and grow outwards while the two "
      "characters match. That is a quadratic search, which is fine, and the "
      "reason it is not a wrong answer here is that it never has to compare the "
      "same pair of characters twice.",
      (["str"], [STR]),
      [c(["babad"], "bab", STR),
       c(["cbbd"], "bb", STR),
       c(["forgeeksskeegfor"], "geeksskeeg", STR),
       c(["abacdfgdcaba"], "aba", STR),
       c(["aacabdkacaa"], "aca", STR),
       c(["aaaa"], "aaaa", STR),
       c(["abcda"], "a", STR),
       c(["ac"], "a", STR),
       c(["a"], "a", STR),
       c([""], "", STR)],
      S('''def LongestPalindromicSubstring(str):
    best_start, best_length = 0, 0
    for centre in range(len(str)):
        # A palindrome's middle is either a character or the gap after it.
        for low, high in ((centre, centre), (centre, centre + 1)):
            while low >= 0 and high < len(str) and str[low] == str[high]:
                # Strictly greater, so the leftmost of two equals wins.
                if high - low + 1 > best_length:
                    best_start, best_length = low, high - low + 1
                low -= 1
                high += 1
    return str[best_start:best_start + best_length]
''',
        """
string LongestPalindromicSubstring(const string& str) {
  int best_start = 0, best_length = 0;
  int n = (int)str.size();
  for (int centre = 0; centre < n; ++centre) {
    for (int low = centre, high = centre; low >= 0 && high < n && str[low] == str[high];
         --low, ++high) {
      // Strictly greater, so the leftmost of two equals wins.
      if (high - low + 1 > best_length) {
        best_start = low;
        best_length = high - low + 1;
      }
    }
    for (int low = centre, high = centre + 1; low >= 0 && high < n && str[low] == str[high];
         --low, ++high) {
      if (high - low + 1 > best_length) {
        best_start = low;
        best_length = high - low + 1;
      }
    }
  }
  return str.substr(best_start, best_length);
}
""",
        """
public class Solution
{
    public static string LongestPalindromicSubstring(string str)
    {
        int bestStart = 0, bestLength = 0, n = str.Length;
        for (int centre = 0; centre < n; centre++)
        {
            for (int offset = 0; offset < 2; offset++)
            {
                int low = centre, high = centre + offset;
                while (low >= 0 && high < n && str[low] == str[high])
                {
                    // Strictly greater, so the leftmost of two equals wins.
                    if (high - low + 1 > bestLength)
                    {
                        bestStart = low;
                        bestLength = high - low + 1;
                    }
                    low--;
                    high++;
                }
            }
        }
        return str.Substring(bestStart, bestLength);
    }
}
""",
        """
public class Solution {
    public static String longestPalindromicSubstring(String str) {
        int bestStart = 0, bestLength = 0, n = str.length();
        for (int centre = 0; centre < n; centre++) {
            for (int offset = 0; offset < 2; offset++) {
                int low = centre, high = centre + offset;
                while (low >= 0 && high < n && str.charAt(low) == str.charAt(high)) {
                    if (high - low + 1 > bestLength) {
                        bestStart = low;
                        bestLength = high - low + 1;
                    }
                    low--;
                    high++;
                }
            }
        }
        return str.substring(bestStart, bestStart + bestLength);
    }
}
"""),
      position=56, source=LC, sourceId=5,
      sourceNote="LeetCode 5 (Medium). Odd and even lengths need separate starts; missing the even centre costs every even palindrome. A single centre loop is the usual bug."),

    q("g-unique-paths", "Unique Paths", STRETCH, [DP, "grids"], "UniquePaths",
      "Have the function UniquePaths(rows, columns) take the size of a grid and "
      "return the number of different paths from the top left cell to the bottom "
      "right one, moving only right or down at each step.\n\nA grid of zero "
      "rows or zero columns has no paths.\n\nThe whole grid is more than "
      "necessary. Every cell in the first row can be reached in exactly one "
      "way -- all right -- and every cell in the first column likewise. For the "
      "rest, the number of paths to a cell is the sum of the numbers to its left "
      "and above it, because those are the two ways in. So one row of running "
      "totals answers the question, read left to right and row by row, and the "
      "answer is the last number in it.\n\nA grid of one row or one column has "
      "exactly one path, which is worth checking: it is the case where the "
      "counting has to be right rather than merely plausible.",
      (["rows", "columns"], [INT, INT]),
      [c([3, 7], 28, INT),
       c([3, 2], 3, INT),
       c([7, 3], 28, INT),
       c([3, 3], 6, INT),
       c([1, 1], 1, INT),
       c([1, 10], 1, INT),
       c([10, 1], 1, INT),
       c([0, 5], 0, INT),
       c([5, 0], 0, INT)],
      S('''def UniquePaths(rows, columns):
    if rows <= 0 or columns <= 0:
        return 0
    # One row of running totals. The first row of the grid is all ones because
    # every cell in it can only be reached from the left.
    row = [1] * columns
    for _ in range(rows - 1):
        for column in range(1, columns):
            # From the left plus from above; row[column - 1] has already been
            # updated to this row, row[column] is still the row above.
            row[column] += row[column - 1]
    return row[columns - 1]
''',
        """
int UniquePaths(int rows, int columns) {
  if (rows <= 0 || columns <= 0) return 0;
  // One row of running totals. The first row of the grid is all ones, since
  // every cell in it can only be reached from the left.
  vector<int> row(columns, 1);
  for (int r = 1; r < rows; ++r) {
    for (int column = 1; column < columns; ++column) {
      // From the left plus from above: row[column - 1] is this row, row[column]
      // is still the row above.
      row[column] += row[column - 1];
    }
  }
  return row[columns - 1];
}
""",
        """
public class Solution
{
    public static int UniquePaths(int rows, int columns)
    {
        if (rows <= 0 || columns <= 0) return 0;
        var row = new int[columns];
        for (int i = 0; i < columns; i++) row[i] = 1;
        for (int r = 1; r < rows; r++)
            for (int column = 1; column < columns; column++)
                row[column] += row[column - 1];
        return row[columns - 1];
    }
}
""",
        """
public class Solution {
    public static int uniquePaths(int rows, int columns) {
        if (rows <= 0 || columns <= 0) return 0;
        int[] row = new int[columns];
        java.util.Arrays.fill(row, 1);
        for (int r = 1; r < rows; r++)
            for (int column = 1; column < columns; column++)
                row[column] += row[column - 1];
        return row[columns - 1];
    }
}
"""),
      position=57, source=LC, sourceId=62,
      sourceNote="LeetCode 62 (Medium). Paths to a cell is the sum of the two cells that lead into it, so a single row of running totals answers the whole grid."),

    q("g-build-tree", "Construct Binary Tree from Preorder and Inorder Traversal",
      STRETCH, [TREE_TAG, "trees", "recursion"],
      "BuildTreeFromTraversals",
      "Have the function BuildTreeFromTraversals(preorder, inorder) take the "
      "preorder and inorder traversals of a binary tree, where the values are "
      "all different, and return the tree.\n\n" + TREE_NOTE +
      "\n\nPreorder is root, then left subtree, then right subtree. Inorder is "
      "left subtree, then root, then right subtree. Neither list says anything "
      "on its own, but together they do: the first value of the preorder is the "
      "root, and where that value sits in the inorder list splits the inorder "
      "list into the root's left and right subtrees -- and it splits the rest of "
      "the preorder list at the same point, because the left subtree's values "
      "come first in both. So the first value in, find it in the inorder list, "
      "and recurse on the two halves.\n\nThe array that comes back is the same "
      "trimmed level order every other tree question here uses, which means the "
      "nulls are the positions with no node. [3, 9, 20, null, null, 15, 7] is a "
      "root of 3 with a left child 9 and a right child 20 whose children are 15 "
      "and 7.\n\nSearching the inorder list from the front every time is "
      "quadratic and is why this is a medium rather than an easy one: a table of "
      "where each value sits makes the whole walk linear.",
      (["preorder", "inorder"], [ARR, ARR]),
      [c([[3, 9, 20, 15, 7], [9, 3, 15, 20, 7]],
         [3, 9, 20, None, None, 15, 7], TREE),
       c([[3, 9, 5, 20, 15, 7], [5, 9, 3, 15, 20, 7]],
         [3, 9, 20, 5, None, 15, 7], TREE),
       c([[-1], [-1]], [-1], TREE),
       c([[1], [1]], [1], TREE),
       c([[1], [1, 2]], [1], TREE)],
      S('''def BuildTreeFromTraversals(preorder, inorder):
    # The first preorder value is the root. Where it sits in the inorder list
    # is the length of its left subtree, and that is where the preorder list
    # splits as well.
    root = preorder[0]
    pivot = inorder.index(root)
    # An empty half is a null child, which is None here and not the empty
    # level-order array -- those are two different things and mixing them up is
    # what makes the encoder trip over a three element unpack.
    left = _nodes(preorder[1:1 + pivot], inorder[:pivot])
    right = _nodes(preorder[1 + pivot:], inorder[pivot + 1:])
    return _level_order((root, left, right))


def _nodes(preorder, inorder):
    """The tree as nested (value, left, right) tuples, or None if it is empty."""
    if not preorder:
        return None
    root = preorder[0]
    pivot = inorder.index(root)
    return (root,
            _nodes(preorder[1:1 + pivot], inorder[:pivot]),
            _nodes(preorder[1 + pivot:], inorder[pivot + 1:]))


def _level_order(node):
    """Lay a node tree out in the trimmed level order the question uses.

    A subtree cannot simply be shifted into place by adding a constant: the
    positions inside it are heap positions relative to its own root, and a node
    two levels down has to land four positions further along, not two. So the
    tree is walked and each node is written at the position its walk reaches.
    """
    out = []

    def put(index, node):
        if node is None:
            while len(out) <= index:
                out.append(None)
            return
        value, left, right = node
        while len(out) <= index:
            out.append(None)
        out[index] = value
        put(2 * index + 1, left)
        put(2 * index + 2, right)

    put(0, node)
    while out and out[-1] is None:
        out.pop()
    return out
''',
        """
vector<optional<int>> BuildTreeFromTraversals(const vector<int>& preorder,
                                              const vector<int>& inorder) {
  vector<optional<int>> out;
  if (preorder.empty()) return out;
  // (value, child index pairs) laid out by heap position.
  map<size_t, int> placed;
  function<void(size_t, size_t, size_t, size_t, size_t)> build =
      [&](size_t heap, size_t pre_lo, size_t pre_hi, size_t in_lo, size_t in_hi) {
    if (pre_lo >= pre_hi) return;
    int value = preorder[pre_lo];
    placed[heap] = value;
    size_t pivot = in_lo;
    while (inorder[pivot] != value) ++pivot;
    size_t left_count = pivot - in_lo;
    build(2 * heap + 1, pre_lo + 1, pre_lo + 1 + left_count, in_lo, pivot);
    build(2 * heap + 2, pre_lo + 1 + left_count, pre_hi, pivot + 1, in_hi);
  };
  build(0, 0, preorder.size(), 0, inorder.size());
  if (placed.empty()) return out;
  size_t top = placed.rbegin()->first;
  out.assign(top + 1, nullopt);
  for (const auto& entry : placed) out[entry.first] = entry.second;
  while (!out.empty() && !out.back().has_value()) out.pop_back();
  return out;
}
""",
        """
public class Solution
{
    public static int?[] BuildTreeFromTraversals(int[] preorder, int[] inorder)
    {
        var placed = new System.Collections.Generic.Dictionary<int, int>();
        Build(placed, 0, 0, preorder.Length, 0, inorder.Length, preorder, inorder);
        if (placed.Count == 0) return new int?[0];
        int top = 0;
        foreach (int heap in placed.Keys) if (heap > top) top = heap;
        var outp = new int?[top + 1];
        foreach (var entry in placed) outp[entry.Key] = entry.Value;
        int end = outp.Length;
        while (end > 0 && !outp[end - 1].HasValue) end--;
        var trimmed = new int?[end];
        System.Array.Copy(outp, trimmed, end);
        return trimmed;
    }

    private static void Build(System.Collections.Generic.Dictionary<int, int> placed,
                              int heap, int preLo, int preHi, int inLo, int inHi,
                              int[] preorder, int[] inorder)
    {
        if (preLo >= preHi) return;
        int value = preorder[preLo];
        placed[heap] = value;
        int pivot = inLo;
        while (inorder[pivot] != value) pivot++;
        int leftCount = pivot - inLo;
        Build(placed, 2 * heap + 1, preLo + 1, preLo + 1 + leftCount, inLo, pivot, preorder, inorder);
        Build(placed, 2 * heap + 2, preLo + 1 + leftCount, preHi, pivot + 1, inHi, preorder, inorder);
    }
}
""",
        """
public class Solution {
    public static Integer[] buildTreeFromTraversals(int[] preorder, int[] inorder) {
        java.util.Map<Integer, Integer> placed = new java.util.HashMap<>();
        build(placed, 0, 0, preorder.length, 0, inorder.length, preorder, inorder);
        if (placed.isEmpty()) return new Integer[0];
        int top = 0;
        for (int heap : placed.keySet()) if (heap > top) top = heap;
        Integer[] out = new Integer[top + 1];
        for (java.util.Map.Entry<Integer, Integer> entry : placed.entrySet())
            out[entry.getKey()] = entry.getValue();
        int end = out.length;
        while (end > 0 && out[end - 1] == null) end--;
        Integer[] trimmed = new Integer[end];
        System.arraycopy(out, 0, trimmed, 0, end);
        return trimmed;
    }

    private static void build(java.util.Map<Integer, Integer> placed, int heap,
                              int preLo, int preHi, int inLo, int inHi,
                              int[] preorder, int[] inorder) {
        if (preLo >= preHi) return;
        int value = preorder[preLo];
        placed.put(heap, value);
        int pivot = inLo;
        while (inorder[pivot] != value) pivot++;
        int leftCount = pivot - inLo;
        build(placed, 2 * heap + 1, preLo + 1, preLo + 1 + leftCount, inLo, pivot, preorder, inorder);
        build(placed, 2 * heap + 2, preLo + 1 + leftCount, preHi, pivot + 1, inHi, preorder, inorder);
    }
}
"""),
      position=58, source=LC, sourceId=105,
      sourceNote="LeetCode 105 (Medium). The first preorder value is the root and its position in the inorder list is the length of the left subtree -- that one number splits both lists."),

    q("g-letter-combinations", "Letter Combinations of a Phone Number",
      STRETCH, ["backtracking", SM], "LetterCombinations",
      "Have the function LetterCombinations(digits) take a string of digits from "
      "2 to 9 and return every combination of letters those digits spell, on a "
      "phone keypad. 2 is abc, 3 is def, 4 is ghi, 5 is jkl, 6 is mno, 7 is "
      "pqrs, 8 is tuv, 9 is wxyz.\n\nThe empty string has no combinations, and "
      "so does any string holding a digit that is not a key. A two digit string "
      "has nine combinations, because the first digit gives three choices and "
      "the second gives three more.\n\nThe combinations come back with the "
      "first digit varying slowest, so \"23\" gives ad, ae, af, bd, be, bf, cd, "
      "ce, cf.\n\nOne list, carried forward. It starts as a single empty "
      "combination, and each digit replaces it with a longer list made of one "
      "copy of each existing combination per letter of that key. The order of "
      "the list is what makes the output order, so it matters that the letters "
      "are appended in order and that the old combinations are read before the "
      "new ones are added.",
      (["digits"], [STR]),
      [c(["23"], ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"], STRARRAY),
       c(["2"], ["a", "b", "c"], STRARRAY),
       c(["79"], ["pw", "px", "py", "pz", "qw", "qx", "qy", "qz",
                  "rw", "rx", "ry", "rz", "sw", "sx", "sy", "sz"], STRARRAY),
       c(["234"], ["adg", "adh", "adi", "aeg", "aeh", "aei", "afg", "afh", "afi",
                   "bdg", "bdh", "bdi", "beg", "beh", "bei", "bfg", "bfh", "bfi",
                   "cdg", "cdh", "cdi", "ceg", "ceh", "cei", "cfg", "cfh", "cfi"],
         STRARRAY),
       c([""], [], STRARRAY)],
      S('''LETTERS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
           "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def LetterCombinations(digits):
    if not digits or any(digit not in LETTERS for digit in digits):
        return []
    out = [""]
    for digit in digits:
        # Read `out` while building the new list, so the earliest digit is the
        # one that varies slowest and the answer comes back in key order.
        out = [prefix + letter for prefix in out for letter in LETTERS[digit]]
    return out
''',
        """
vector<string> LetterCombinations(const string& digits) {
  const map<char, string> letters{
      {'2', "abc"}, {'3', "def"}, {'4', "ghi"}, {'5', "jkl"},
      {'6', "mno"}, {'7', "pqrs"}, {'8', "tuv"}, {'9', "wxyz"}};
  for (char digit : digits)
    if (!letters.count(digit)) return vector<string>();
  if (digits.empty()) return vector<string>();
  vector<string> out{""};
  for (char digit : digits) {
    vector<string> nxt;
    for (const string& prefix : out)
      for (char letter : letters.at(digit)) nxt.push_back(prefix + letter);
    out = nxt;
  }
  return out;
}
""",
        """
public class Solution
{
    public static string[] LetterCombinations(string digits)
    {
        var letters = new System.Collections.Generic.Dictionary<char, string>
        {
            { '2', "abc" }, { '3', "def" }, { '4', "ghi" }, { '5', "jkl" },
            { '6', "mno" }, { '7', "pqrs" }, { '8', "tuv" }, { '9', "wxyz" },
        };
        foreach (char digit in digits)
            if (!letters.ContainsKey(digit)) return new string[0];
        if (digits.Length == 0) return new string[0];
        var outp = new System.Collections.Generic.List<string> { "" };
        foreach (char digit in digits)
        {
            var nxt = new System.Collections.Generic.List<string>();
            foreach (string prefix in outp)
                foreach (char letter in letters[digit])
                    nxt.Add(prefix + letter);
            outp = nxt;
        }
        return outp.ToArray();
    }
}
""",
        """
public class Solution {
    public static String[] letterCombinations(String digits) {
        java.util.Map<Character, String> letters = new java.util.HashMap<>();
        letters.put('2', "abc"); letters.put('3', "def"); letters.put('4', "ghi");
        letters.put('5', "jkl"); letters.put('6', "mno"); letters.put('7', "pqrs");
        letters.put('8', "tuv"); letters.put('9', "wxyz");
        for (int i = 0; i < digits.length(); i++)
            if (!letters.containsKey(digits.charAt(i))) return new String[0];
        if (digits.length() == 0) return new String[0];
        java.util.List<String> out = new java.util.ArrayList<>();
        out.add("");
        for (int i = 0; i < digits.length(); i++) {
            java.util.List<String> next = new java.util.ArrayList<>();
            for (String prefix : out)
                for (char letter : letters.get(digits.charAt(i)).toCharArray())
                    next.add(prefix + letter);
            out = next;
        }
        return out.toArray(new String[0]);
    }
}
"""),
      position=60, source=LC, sourceId=17,
      sourceNote="LeetCode 17 (Medium). The output order falls out of the order the list is built in: the earliest digit varies slowest, which is the opposite of what most people write first."),

    q("g-word-search", "Word Search", STRETCH, [ALGO, "backtracking", "matrix"],
      "WordSearch",
      "Have the function WordSearch(board, word) take a grid of single "
      "characters and a word, and return the boolean true if the word can be "
      "spelled by starting at some cell and stepping to a cell above, below, "
      "left or right, never reusing a cell.\n\n" + MATRIX_NOTE.replace(
          "A matrix arrives as a list of rows, each row a list of the same length, "
          "and is returned the same way.",
          "The board arrives as a list of rows, and each cell is a one character "
          "string rather than a number, so a board of letters is written as "
          "[[\"A\", \"B\"], [\"C\", \"D\"]].") +
      "\n\nThe word has to start somewhere, so try every cell. From there the "
      "search is depth first and the one thing that has to be undone on the way "
      "back out is the cell just used: a letter cannot be part of two branches "
      "at once, and a cell holding the letter that is currently wanted has to be "
      "hidden while the rest of the word is looked for and put back afterwards. "
      "Forgetting to put it back loses every path that needs that cell later.\n\n"
      "Backing out of a successful branch is what stops the search as soon as "
      "it finds one, rather than going on to prove that no other cell works "
      "either.",
      (["board", "word"], [CHARMATRIX, STR]),
      [c([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"],
         True, BOOL),
       c([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "SEE"],
         True, BOOL),
       c([[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"],
         False, BOOL),
       c([[["a", "b"], ["c", "d"]], "ab"], True, BOOL),
       c([[["a", "b"], ["c", "d"]], "abc"], False, BOOL),
       c([[["A"]], "A"], True, BOOL),
       c([[["A"]], "B"], False, BOOL),
       c([[], "A"], False, BOOL)],
      S('''def WordSearch(board, word):
    if not word:
        return True
    if not board or not board[0]:
        return False

    def search(row, column, index):
        if board[row][column] != word[index]:
            return False
        if index == len(word) - 1:
            return True
        # The cell cannot serve two branches at once, so it is hidden while
        # this branch is open and restored on the way out -- including when
        # the branch succeeds.
        saved = board[row][column]
        board[row][column] = None
        found = False
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_row, next_column = row + row_step, column + column_step
            if (0 <= next_row < len(board) and 0 <= next_column < len(board[0])
                    and board[next_row][next_column] is not None):
                if search(next_row, next_column, index + 1):
                    found = True
                    break
        board[row][column] = saved
        return found

    for row in range(len(board)):
        for column in range(len(board[0])):
            if search(row, column, 0):
                return True
    return False
''',
        """
bool WordSearch(vector<vector<string>> board, const string& word) {
  if (word.empty()) return true;
  if (board.empty() || board[0].empty()) return false;
  int rows = (int)board.size(), columns = (int)board[0].size();
  const int steps[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
  function<bool(int, int, int)> search = [&](int row, int column, int index) -> bool {
    if (board[row][column] != word.substr(index, 1)) return false;
    if (index == (int)word.size() - 1) return true;
    // Hide the cell while this branch is open, and restore it afterwards --
    // including on the way out of a branch that succeeded.
    string saved = board[row][column];
    board[row][column] = "";
    bool found = false;
    for (const auto& step : steps) {
      int next_row = row + step[0], next_column = column + step[1];
      if (next_row < 0 || next_row >= rows || next_column < 0 || next_column >= columns)
        continue;
      if (board[next_row][next_column].empty()) continue;
      if (search(next_row, next_column, index + 1)) { found = true; break; }
    }
    board[row][column] = saved;
    return found;
  };
  for (int row = 0; row < rows; ++row)
    for (int column = 0; column < columns; ++column)
      if (search(row, column, 0)) return true;
  return false;
}
""",
        """
public class Solution
{
    public static bool WordSearch(string[][] board, string word)
    {
        if (word.Length == 0) return true;
        if (board.Length == 0 || board[0].Length == 0) return false;
        int rows = board.Length, columns = board[0].Length;
        int[,] steps = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } };
        Func<int, int, int, bool> search = null;
        search = (row, column, index) =>
        {
            if (board[row][column] != word.Substring(index, 1)) return false;
            if (index == word.Length - 1) return true;
            string saved = board[row][column];
            board[row][column] = "";
            bool found = false;
            for (int step = 0; step < 4 && !found; step++)
            {
                int nextRow = row + steps[step, 0], nextColumn = column + steps[step, 1];
                if (nextRow < 0 || nextRow >= rows || nextColumn < 0 || nextColumn >= columns)
                    continue;
                if (board[nextRow][nextColumn].Length == 0) continue;
                if (search(nextRow, nextColumn, index + 1)) found = true;
            }
            board[row][column] = saved;
            return found;
        };
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++)
                if (search(row, column, 0)) return true;
        return false;
    }
}
""",
        """
public class Solution {
    public static boolean wordSearch(String[][] board, String word) {
        if (word.length() == 0) return true;
        if (board.length == 0 || board[0].length == 0) return false;
        int rows = board.length, columns = board[0].length;
        int[][] steps = { { 1, 0 }, { -1, 0 }, { 0, 1 }, { 0, -1 } };
        // A local class rather than a lambda, because the recursion needs the
        // method to name itself. A cell cannot serve two branches at once, so
        // it is blanked while the branch is open and restored afterwards.
        class Search {
            boolean walk(int row, int column, int index) {
                if (!board[row][column].equals(word.substring(index, index + 1)))
                    return false;
                if (index == word.length() - 1) return true;
                String saved = board[row][column];
                board[row][column] = "";
                boolean found = false;
                for (int[] step : steps) {
                    int nextRow = row + step[0], nextColumn = column + step[1];
                    if (nextRow < 0 || nextRow >= rows || nextColumn < 0 || nextColumn >= columns)
                        continue;
                    if (board[nextRow][nextColumn].isEmpty()) continue;
                    if (walk(nextRow, nextColumn, index + 1)) { found = true; break; }
                }
                board[row][column] = saved;
                return found;
            }
        }
        Search search = new Search();
        for (int row = 0; row < rows; row++)
            for (int column = 0; column < columns; column++)
                if (search.walk(row, column, 0)) return true;
        return false;
    }
}
"""),
      position=61, source=LC, sourceId=79,
      sourceNote="LeetCode 79 (Medium). The cell has to be restored on the way out of a successful branch as well as an unsuccessful one, or a later starting cell sees a board with a hole in it."),
]
